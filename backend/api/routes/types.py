from fastapi import APIRouter, Depends
from sqlmodel import Session
from typing import List

from backend.api.dependencies.database import get_session
from backend.api.dependencies.permissions import require_user, RequireArchiveRoleFastAPI
from backend.app.models.type import TypePublic
from backend.app.models.user_archive_link import ArchiveRole
from backend.app.services.type_service import get_all_types, get_all_types_for_archive

router = APIRouter(prefix="/types", tags=["types"])

@router.get("/", response_model=List[TypePublic])
def read_types(
    session: Session = Depends(get_session),
    _: None = Depends(require_user)
):
    return get_all_types(session)

@router.get("/archive/{archive_id}", response_model=List[TypePublic])
def read_types_for_archive(
    archive_id: int,
    session: Session = Depends(get_session),
    _: None = Depends(RequireArchiveRoleFastAPI([ArchiveRole.OWNER, ArchiveRole.EDITOR, ArchiveRole.VIEWER]))
):
    return get_all_types_for_archive(session, archive_id)
