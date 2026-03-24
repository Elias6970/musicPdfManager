from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlmodel import Session

from backend.api.dependencies.database import get_session
from backend.api.dependencies.permissions import require_user
from backend.app.models.user import User
from backend.app.models.user_archive_link import ArchiveRole
from backend.app.services.archive_services import check_archive_role
from backend.app.error import InsufficientPermissionsError
from backend.app.services.printing_services import process_simple_print_job
from backend.app.models.printers.jobs.simple_print_job import SimplePrintJob

router = APIRouter(prefix="/printers", tags=["printers"])

@router.post("/simple")
def simple_print(
    job: SimplePrintJob,
    session: Session = Depends(get_session),
    user: User = Depends(require_user)
):
    try:
        for file_element in job.files:
            check_archive_role(
                session=session,
                user_id=user.id, #type: ignore
                archive_id=file_element.archive_id,
                allowed_roles=[ArchiveRole.OWNER, ArchiveRole.EDITOR, ArchiveRole.VIEWER]
            )
    except InsufficientPermissionsError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
            
    try:
        pdf_bytes = process_simple_print_job(session, job)
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
        
    headers = {"Content-Disposition": 'attachment; filename="print_job.pdf"'}
    return Response(content=pdf_bytes, media_type="application/pdf", headers=headers)
