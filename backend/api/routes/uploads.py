from fastapi import APIRouter, Depends, Request, HTTPException, status

from backend.app.services.upload_services import process_upload_stream, process_upload_stream_to_folder_compressed
from backend.app.error import FileTooLargeException
from backend.app.models.upload import UploadStagingResponse, UploadToFolderResponse
from backend.api.dependencies.permissions import require_user

router = APIRouter(prefix="/uploads", tags=["uploads"])

@router.post("/staging", response_model=UploadStagingResponse, status_code=status.HTTP_201_CREATED)
async def upload_file_to_staging(
    request: Request, 
    _ = Depends(require_user)):
    """
    Upload a file stream to a temporary staging area before linking to a piece.
    The file name must be passed in the 'filename' HTTP Header.
    Params:
    - request: The incoming HTTP request containing the file stream and headers.
    Returns:
    - UploadStagingResponse: Contains the generated `file_id` (the combined UUID_filename) and the `original_filename`.
    """
    try:
        return await process_upload_stream(request)
    except FileTooLargeException as e:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=str(e)
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while uploading the file"
        )


@router.post("/staging/{folder_id}/compressed", response_model=UploadToFolderResponse, status_code=status.HTTP_201_CREATED)
async def upload_compressed_file_to_folder_staging(
    request: Request, 
    folder_id: str | None = None,
    _ = Depends(require_user)):
    """
    A wrapper around `upload_file_to_staging` that uploads the file to a subfolder and then uncompresses the uploaded file (zip, rar, etc.).
    Params:
        - request: The incoming HTTP request containing the file stream and headers.
        - folder_id: A string identifier for the staging folder (e.g., "massive_import"). 
                    If it is not provided, it creates a new subfolder and return the identifier.
    Returns:
        - UploadToFolderResponse: Contains the `folder_id` where the file was uploaded and extracted, the `original_filename`, and the size in bytes.
    """
    try:
        return await process_upload_stream_to_folder_compressed(request, folder_id)
    except FileTooLargeException as e:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=str(e)
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while uploading and processing the compressed file"
        )