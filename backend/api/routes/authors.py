from fastapi import APIRouter, Depends
from sqlmodel import Session
from typing import List

from backend.api.dependencies.database import get_session
from backend.api.dependencies.permissions import require_user, RequireArchiveRoleFastAPI
from backend.app.models.author import AuthorPublic
from backend.app.models.user_archive_link import ArchiveRole
from backend.app.services.author_service import get_all_authors, get_all_authors_for_archive

router = APIRouter(prefix="/authors", tags=["authors"])

@router.get("/", response_model=List[AuthorPublic])
def read_authors(
    session: Session = Depends(get_session),
    _: None = Depends(require_user)
):
    return get_all_authors(session)

@router.get("/archive/{archive_id}", response_model=List[AuthorPublic])
def read_authors_for_archive(
    archive_id: int,
    session: Session = Depends(get_session),
    _: None = Depends(RequireArchiveRoleFastAPI([ArchiveRole.OWNER, ArchiveRole.EDITOR, ArchiveRole.VIEWER]))
):
    return get_all_authors_for_archive(session, archive_id)
