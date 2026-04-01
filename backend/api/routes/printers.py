from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlmodel import Session

from backend.api.dependencies.database import get_session
from backend.api.dependencies.permissions import require_user
from backend.app.models.user import User
from backend.app.models.user_archive_link import ArchiveRole
from backend.app.services.archive_services import check_archive_role
from backend.app.error import InsufficientPermissionsError, UnresolvedInstrumentsException
from backend.app.services.printing_services import process_simple_print_job, process_preset_print_job
from backend.app.models.printers.jobs.simple_print_job import SimplePrintJob
from backend.app.models.printers.jobs.preset_print_job import PresetPrintJob, ExportStrategyType

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

@router.post("/preset")
def preset_print(
    job: PresetPrintJob,
    session: Session = Depends(get_session),
    user: User = Depends(require_user)
):
    if job.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User ID mismatch. Cannot perform job for another user."
        )
    
    try:
        check_archive_role(
            session=session,
            user_id=user.id, #type: ignore
            archive_id=job.archive_id,
            allowed_roles=[ArchiveRole.OWNER, ArchiveRole.EDITOR, ArchiveRole.VIEWER]
        )
    except InsufficientPermissionsError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
            
    try:
        result_bytes = process_preset_print_job(session, job)
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except UnresolvedInstrumentsException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Unresolved instruments", "unresolved": [u.model_dump() for u in e.unresolved]}
        )
        
    if job.config.export_strategy == ExportStrategyType.ALL_IN_ONE:
        media_type = "application/pdf"
        filename = "preset_print.pdf"
    else:
        media_type = "application/zip"
        filename = "preset_print.zip"
        
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return Response(content=result_bytes, media_type=media_type, headers=headers)

