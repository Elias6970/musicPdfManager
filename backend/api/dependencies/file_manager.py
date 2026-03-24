from fastapi import Depends
import os
from backend.app.settings import get_server_settings
from backend.app.files_management.archive_file_manager import ArchiveFileManager
from backend.app.services.archive_services import get_archive_path
from backend.app.crud.archive_crud import Archive
from sqlmodel import Session, select
from backend.api.dependencies.database import get_session

def get_archive_file_manager(archive_id: int, session: Session = Depends(get_session)) -> ArchiveFileManager:
    path = get_archive_path(session, archive_id)
    return ArchiveFileManager(path)
