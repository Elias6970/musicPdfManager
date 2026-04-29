from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from backend.api.dependencies.database import get_session
from backend.api.dependencies.permissions import RequireArchiveRoleFastAPI
from backend.app.models.user_archive_link import ArchiveRole
from backend.app.models.classification.classification_job import ClassificationJob
from backend.app.services.classification_services import classify
from backend.app.error import ClassificationFileExistsError

router = APIRouter(prefix="/classification", tags=["Classification"])

@router.post("/{archive_id}", status_code=status.HTTP_200_OK)
def execute_classification(
    archive_id: int,
    job: ClassificationJob,
    session: Session = Depends(get_session),
    _ = Depends(RequireArchiveRoleFastAPI([ArchiveRole.OWNER, ArchiveRole.EDITOR, ArchiveRole.VIEWER]))
):
    """
    Executes the complete classification pipeline.
    Expects a ClassificationJob object containing the piece's standardized name, archive ID, 
    source files, and a dictionary of extracted page maps (ClassifiedDocument).
    """
    if archive_id != job.archive_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Archive ID in URL does not match the ClassificationJob payload."
        )

    try:
        success = classify(session, job)
        if success:
            return {"message": "Classification completed successfully"}
    except ClassificationFileExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "File collision detected. The configurations lacked rename/overwrite strategies.",
                "missing_names": e.incorrect_keys
            }
        )
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        print(f"Unexpected error during classification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during classification: {str(e)}"
        )