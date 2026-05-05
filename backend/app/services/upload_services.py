import asyncio, io,  os, uuid, time, aiofiles
from urllib.parse import unquote
from fastapi import Request

from backend.app.utils.settings import get_server_settings
from backend.app.error import FileTooLargeException
from backend.app.models.upload import UploadStagingResponse, UploadToFolderResponse
from backend.app.files_management.archive_file_manager import ArchiveFileManager
from backend.app.massive_import.file_decompressor.file_decompressor_services import get_strategy

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
        print(f"Error processing upload stream: {e}")
        raise e

async def process_upload_stream_to_folder_compressed(request: Request, folder_id: str|None = None) -> UploadToFolderResponse:
    """
    Uploads a compressed file stream to staging , extracts its contents, and saves them in the staging folder_id folder. Deletes the original compressed file.
    WARNING: The user can provide a folder_id that doesn't exits and it will be created. Be careful
        Params:
        - request: The incoming HTTP request containing the file stream and headers.
        - folder_id: A string identifier for the staging folder (e.g., "massive_import"). 
                    If it is not provided, it creates a new subfolder and return the identifier.
    
    """
    upload_response = await process_upload_stream(request)
    
    if folder_id is None or folder_id.strip() == "" or folder_id == "None":
        folder_id = str(uuid.uuid4())

    piece_folder_name = os.path.splitext(upload_response.original_filename)[0] #Remove extension
    extraction_folder_path = os.path.join(get_server_settings().temp_upload_folder, folder_id, piece_folder_name)
    os.makedirs(extraction_folder_path, exist_ok=True)

    compressed_filepath = os.path.join(get_server_settings().temp_upload_folder, upload_response.file_id)
    strategy = get_strategy(upload_response.original_filename)
    if strategy:
        try:
            with open(compressed_filepath, 'rb') as f:
                file_data = f.read()
                extracted_files = strategy.extract_all(io.BytesIO(file_data))
                
                # Save extracted files to the extraction folder
                for filename, file_bytes in extracted_files.items():
                    extracted_filepath = os.path.join(extraction_folder_path, filename)
                    os.makedirs(os.path.dirname(extracted_filepath), exist_ok=True)
                    
                    # Skip if it is just a directory entry
                    if not filename.endswith('/') and not filename.endswith('\\'):
                        async with aiofiles.open(extracted_filepath, 'wb') as ef:
                            await ef.write(file_bytes)
            
            # Delete compressed
            os.remove(compressed_filepath)
            
            return UploadToFolderResponse(
                folder_id=folder_id,
                original_filename=upload_response.original_filename,
                    size_bytes=upload_response.size_bytes,
                    message="Successfully uploaded and extracted compressed file"
                )
            
        except Exception as e:
            raise Exception(f"Error processing compressed file: {str(e)}")
    else:
        raise Exception("Unsupported compressed file format")



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