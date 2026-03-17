from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from backend.api.dependencies.database import get_session
from backend.api.dependencies.auth import get_current_user
from backend.api.dependencies.permissions import RequireArchiveRoleFastAPI
from backend.app.models.archive import Archive, ArchiveCreate, ArchivePublic
from backend.app.models.user import User
from backend.app.models.user_archive_link import ArchiveRole
from backend.app.crud import archive_crud

router = APIRouter(prefix="/archives", tags=["archives"])

@router.post("/", response_model=ArchivePublic)
def create_archive(
    archive: ArchiveCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    if current_user.id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not authenticated")
    return archive_crud.create_archive(session, archive, current_user.id)

@router.get("/{archive_id}", response_model=ArchivePublic)
def get_archive(
    archive_id: int,
    session: Session = Depends(get_session),
    _ = Depends(RequireArchiveRoleFastAPI([ArchiveRole.OWNER, ArchiveRole.EDITOR, ArchiveRole.VIEWER]))
):
    archive = archive_crud.get_archive(session, archive_id)
    if not archive:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Archive not found")
    return archive

@router.put("/{archive_id}", response_model=ArchivePublic)
def update_archive(
    archive_id: int,
    archive_data: ArchiveCreate,
    session: Session = Depends(get_session),
    _ = Depends(RequireArchiveRoleFastAPI([ArchiveRole.OWNER, ArchiveRole.EDITOR]))
):
    archive = archive_crud.update_archive(session, archive_id, archive_data)
    if not archive:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Archive not found")
    return archive

@router.delete("/{archive_id}")
def delete_archive(
    archive_id: int,
    session: Session = Depends(get_session),
    _ = Depends(RequireArchiveRoleFastAPI([ArchiveRole.OWNER]))
):
    success = archive_crud.delete_archive(session, archive_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Archive not found")
    return {"message": "Archive deleted successfully"}

@router.post("/{archive_id}/users/{user_id}")
def add_user_to_archive(
    archive_id: int,
    user_id: int,
    role: ArchiveRole,
    session: Session = Depends(get_session),
    _ = Depends(RequireArchiveRoleFastAPI([ArchiveRole.OWNER, ArchiveRole.EDITOR]))
):
    link = archive_crud.add_user_to_archive(session, archive_id, user_id, role)
    if not link:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Archive or User not found")
    return link
