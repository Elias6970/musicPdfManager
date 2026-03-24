from fastapi import APIRouter, Request, HTTPException, status

from backend.app.services.upload_services import process_upload_stream
from backend.app.error import FileTooLargeException
from backend.app.models.upload import UploadStagingResponse

router = APIRouter(prefix="/uploads", tags=["uploads"])

@router.post("/staging", response_model=UploadStagingResponse, status_code=status.HTTP_201_CREATED)
async def upload_file_to_staging(request: Request):
    """
    Upload a file stream to a temporary staging area before linking to a piece.
    The file name must be passed in the 'filename' HTTP Header.
    """
    try:
        return await process_upload_stream(request)
    except FileTooLargeException as e:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while uploading the file"
        )