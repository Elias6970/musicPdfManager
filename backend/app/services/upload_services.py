import asyncio
import os
import uuid
import time
import aiofiles
from urllib.parse import unquote
from fastapi import Request

from backend.app.settings import get_server_settings
from backend.app.error import FileTooLargeException
from backend.app.models.upload import UploadStagingResponse
from backend.app.files_management.archive_file_manager import ArchiveFileManager

async def process_upload_stream(request: Request) -> UploadStagingResponse:
    """
    Processes an incoming file upload stream and saves it to a temporary staging folder.
    
    The file is saved on disk with a unique name combining a newly generated UUID and the 
    original filename separated by an underscore (e.g., '123e4567-e89b-12d3_myscore.pdf'). 
    This prevents name collisions and unauthorized access while keeping the original name 
    recoverable.
    
    Returns:
        UploadStagingResponse: Contains the generated `file_id` (the combined UUID_filename) 
        and the `original_filename`.
    """
    settings = get_server_settings()
    
    # Pre-validation check for declared size
    content_length = request.headers.get("content-length")
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    
    if content_length and int(content_length) > max_bytes:
        raise FileTooLargeException(f"File size exceeds the limit of {settings.max_upload_size_mb} MB")

    filename = request.headers.get("filename", "uploaded_file")
    filename = unquote(filename)
    
    file_uuid = str(uuid.uuid4())
    temp_filename = ArchiveFileManager.format_temp_filename(file_uuid, filename)
    
    os.makedirs(settings.temp_upload_folder, exist_ok=True)
    filepath = os.path.join(settings.temp_upload_folder, temp_filename)
    
    bytes_written = 0
    
    try:
        async with aiofiles.open(filepath, 'wb') as f:
            async for chunk in request.stream():
                bytes_written += len(chunk)
                if bytes_written > max_bytes:
                    break
                await f.write(chunk)
        
        # Mid-stream enforcement
        if bytes_written > max_bytes:
            os.remove(filepath)
            raise FileTooLargeException(f"File size exceeds the limit of {settings.max_upload_size_mb} MB during streaming")
            
        # Update timestamp to right now for future cleanup logic
        current_time = time.time()
        os.utime(filepath, (current_time, current_time))
        
        return UploadStagingResponse(
            file_id=temp_filename,
            original_filename=filename,
            size_bytes=bytes_written,
            message="Successfully uploaded file to staging"
        )
        
    except Exception as e:
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
            except OSError:
                pass
        raise e

async def cleanup_temp_uploads_routine():
    """Background routine that periodically deletes expired temporary files."""
    while True:
        settings = get_server_settings()

        try:
            temp_folder = settings.temp_upload_folder
            max_age_seconds = settings.max_temp_file_age_minutes * 60
            
            if os.path.exists(temp_folder):
                current_time = time.time()
                for filename in os.listdir(temp_folder):
                    filepath = os.path.join(temp_folder, filename)
                    
                    if os.path.isfile(filepath):
                        file_mtime = os.path.getmtime(filepath)
                        
                        if (current_time - file_mtime) > max_age_seconds:
                            try:
                                os.remove(filepath)
                            except OSError:
                                pass
                                
        except Exception:
            pass
            
        await asyncio.sleep(settings.cleanup_uploads_interval_minutes * 60)