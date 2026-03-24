import pytest
import os
from unittest.mock import AsyncMock, patch
from fastapi import Request

from backend.app.services.upload_services import process_upload_stream
from backend.app.error import FileTooLargeException
from backend.app.models.upload import UploadStagingResponse

@pytest.fixture
def mock_settings():
    with patch("backend.app.services.upload_services.get_server_settings") as mock:
        mock.return_value.max_upload_size_mb = 10
        mock.return_value.temp_upload_folder = "/tmp/test_uploads"
        yield mock.return_value

@pytest.mark.asyncio
async def test_process_upload_stream_success(mock_settings, tmp_path):
    # Setup
    mock_settings.temp_upload_folder = str(tmp_path)
    
    mock_request = AsyncMock(spec=Request)
    mock_request.headers = {
        "content-length": "1024",
        "filename": "test_file.pdf"
    }
    
    # Mock stream chunks
    async def mock_stream():
        yield b"chunk1"
        yield b"chunk2"
        
    mock_request.stream = mock_stream

    # Act
    with patch("backend.app.services.upload_services.uuid.uuid4", return_value="1234-5678"):
        result = await process_upload_stream(mock_request)

    # Assert
    assert isinstance(result, UploadStagingResponse)
    assert result.file_id == "1234-5678.pdf"
    assert result.original_filename == "test_file.pdf"
    assert result.size_bytes == 12
    
    # Verify file was written
    filepath = os.path.join(tmp_path, "1234-5678.pdf")
    assert os.path.exists(filepath)
    with open(filepath, "rb") as f:
        assert f.read() == b"chunk1chunk2"

@pytest.mark.asyncio
async def test_process_upload_stream_exceeds_content_length(mock_settings):
    # Setup - pretend size is 11MB, limit is 10MB
    mock_request = AsyncMock(spec=Request)
    mock_request.headers = {
        "content-length": str(11 * 1024 * 1024)
    }

    # Act & Assert
    with pytest.raises(FileTooLargeException) as exc_info:
        await process_upload_stream(mock_request)
        
    assert "File size exceeds the limit" in str(exc_info.value)

@pytest.mark.asyncio
async def test_process_upload_stream_exceeds_during_stream(mock_settings, tmp_path):
    # Setup
    mock_settings.temp_upload_folder = str(tmp_path)
    mock_settings.max_upload_size_mb = 1  # 1 MB limit
    
    mock_request = AsyncMock(spec=Request)
    mock_request.headers = {}  # No content-length provided
    
    # Mock stream chunks that exceed 1MB in total
    async def mock_stream():
        yield b"0" * (1024 * 1024)  # 1 MB
        yield b"1"  # 1 byte over limit
        
    mock_request.stream = mock_stream

    # Act & Assert
    with patch("backend.app.services.upload_services.uuid.uuid4", return_value="1234-5678"):
        with pytest.raises(FileTooLargeException) as exc_info:
            await process_upload_stream(mock_request)
            
    assert "during streaming" in str(exc_info.value)
    
    # Verify file was cleaned up
    filepath = os.path.join(tmp_path, "1234-5678")
    assert not os.path.exists(filepath)

@pytest.mark.asyncio
async def test_cleanup_temp_uploads_routine_deletes_expired(mock_settings, tmp_path):
    from backend.app.services.upload_services import cleanup_temp_uploads_routine
    import time
    
    mock_settings.temp_upload_folder = str(tmp_path)
    mock_settings.max_temp_file_age_minutes = 2
    mock_settings.cleanup_uploads_interval_minutes = 15

    # Create two files
    old_file = tmp_path / "old.pdf"
    new_file = tmp_path / "new.pdf"
    
    old_file.write_text("old text")
    new_file.write_text("new text")
    
    # Set modify time to 3 minutes ago
    old_time = time.time() - (3 * 60)
    os.utime(str(old_file), (old_time, old_time))
    
    class StopLoop(Exception):
        pass

    with patch("asyncio.sleep", side_effect=StopLoop):
        with pytest.raises(StopLoop):
            await cleanup_temp_uploads_routine()
            
    assert not os.path.exists(str(old_file))
    assert os.path.exists(str(new_file))


@pytest.mark.asyncio
async def test_cleanup_temp_uploads_routine_ignores_missing_folder(mock_settings):
    from backend.app.services.upload_services import cleanup_temp_uploads_routine
    
    mock_settings.temp_upload_folder = "/path/that/does/not/exist"
    mock_settings.max_temp_file_age_minutes = 2
    mock_settings.cleanup_uploads_interval_minutes = 15

    class StopLoop(Exception):
        pass

    with patch("asyncio.sleep", side_effect=StopLoop):
        with pytest.raises(StopLoop):
            # Should silently fail and reach the sleep statement
            await cleanup_temp_uploads_routine()
