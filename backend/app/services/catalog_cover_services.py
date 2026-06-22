from sqlmodel import Session
import os

from backend.app.services.files_management.archive_file_manager import ArchiveFileManager
from backend.app.error import InvalidUserDataError, MovingTheCoverFileError
from backend.app.services.user_config_services import get_user_config_by_user_id
from backend.app.utils.settings import get_server_settings

def save_catalog_cover(session: Session, user_id: int, file_id: str) -> bool:
    """
    Service that moves a catalog cover from upload folder to its correct folder and updates the user config.
    Args:
    - session: Database session for querying user config.
    - user_id: ID of the user to whom the catalog cover belongs.
    - file_id: Temporary file ID of the uploaded catalog cover.
    Returns:
    - True if the operation was successful.
    Raises:
    - InvalidUserDataError: If the user config is not found.
    - MovingTheCoverFileError: If the file fails to be moved.
    """
    settings = get_server_settings()

    user_config = get_user_config_by_user_id(session, user_id)
    if not user_config:
        raise InvalidUserDataError("User config not found")

    temp_file = os.path.join(settings.temp_upload_folder, file_id)
    moved_path = ArchiveFileManager.move_catalog_cover_from_temp(temp_file, settings.base_catalog_cover_path)

    if moved_path == "":
        raise MovingTheCoverFileError("Failed to move catalog cover")

    return True