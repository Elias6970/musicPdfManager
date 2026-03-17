from fastapi import Depends
import os
from backend.app.settings import get_server_settings
from backend.app.files_management.archive_file_manager import ArchiveFileManager
from backend.app.crud.archive_crud import Archive
from sqlmodel import Session, select
from backend.api.dependencies.database import get_session

def get_archive_file_manager(archive_id: int, session: Session = Depends(get_session)) -> ArchiveFileManager:
    archive = session.exec(select(Archive).where(Archive.id == archive_id)).first()
    if not archive:
        raise ValueError(f"Archive with id {archive_id} not found")
    if not archive.path:
        raise ValueError(f"Archive with id {archive_id} does not have a valid path")
    
    settings = get_server_settings()
    path = os.path.join(settings.archive_root, archive.path)
    return ArchiveFileManager(path)
