from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlmodel import Session

from backend.api.dependencies.database import get_session
from backend.api.dependencies.permissions import require_user, require_archive_viewer
from backend.app.models.catalog_generation_config import CatalogGenerationConfig, CatalogGenerationConfigCreate
from backend.app.models.user import User
from backend.app.models.user_archive_link import ArchiveRole
from backend.app.services.archive_services import check_archive_role
from backend.app.error import InsufficientPermissionsError, UnresolvedInstrumentsException
from backend.app.services.catalog_services import generate_pdf_catalog_for_archive
from backend.app.services.printing_services import process_simple_print_job, process_preset_print_job
from backend.app.models.printers.jobs.simple_print_job import SimplePrintJob
from backend.app.models.printers.jobs.preset_print_job import PresetPrintJob, PresetPrintJobPublic, ExportStrategyType

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
    public_job: PresetPrintJobPublic,
    session: Session = Depends(get_session),
    user: User = Depends(require_user)
):
    
    try:
        check_archive_role(
            session=session,
            user_id=user.id, #type: ignore
            archive_id=public_job.archive_id,
            allowed_roles=[ArchiveRole.OWNER, ArchiveRole.EDITOR, ArchiveRole.VIEWER]
        )
    except InsufficientPermissionsError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
            
    try:
        processable_job = PresetPrintJob(
            preset_name=public_job.preset_name,
            user_id=user.id,
            archive_id=public_job.archive_id,
            pieces=public_job.pieces,
            config=public_job.config,
            solved_fails=public_job.solved_fails
        )
        result_bytes = process_preset_print_job(session, processable_job)
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
        
    if public_job.config.export_strategy == ExportStrategyType.ALL_IN_ONE:
        media_type = "application/pdf"
        filename = "preset_print.pdf"
    else:
        media_type = "application/zip"
        filename = "preset_print.zip"
        
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return Response(content=result_bytes, media_type=media_type, headers=headers)


@router.get("/catalog/{archive_id}")
def get_catalog(
    archive_id: int,
    config: CatalogGenerationConfigCreate, 
    session: Session = Depends(get_session),
    _: User = Depends(require_archive_viewer)
):
    config_obj = CatalogGenerationConfig(**config.model_dump(), archive_id=archive_id)
    pdf_bytes = generate_pdf_catalog_for_archive(session, config_obj)
    headers = {"Content-Disposition": 'attachment; filename="catalog.pdf"'}
    return Response(content=pdf_bytes, media_type="application/pdf", headers=headers)