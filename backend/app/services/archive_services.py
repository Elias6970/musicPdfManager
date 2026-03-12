from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select
from backend.app.models.user_archive_link import UserArchiveLink, ArchiveRole
from backend.app.error import FileCouldNotBeReadException, InsufficientPermissionsError
from backend.app.models.piece import Piece, PieceCreate
from backend.app.crud.piece_crud import create_piece
from backend.app.files_management.archive_file_manager import ArchiveFileManager


def check_archive_role(
    session: Session,
    user_id: int,
    archive_id: int,
    allowed_roles: List[ArchiveRole]
) -> UserArchiveLink:
    """
    Core business logic to verify if a user has sufficient permissions for an archive.
    
    This function is completely isolated from FastAPI. You can use it in your services
    or anywhere else in your backend. If the user doesn't have an allowed role,
    it raises a custom `InsufficientPermissionsError` which can be handled by
    your API endpoint or an exception handler.

    Args:
        session: The database session.
        user_id: The ID of the user requesting access.
        archive_id: The ID of the archive being accessed.
        allowed_roles: A list of `ArchiveRole` enums that are permitted to perform the action.

    Returns:
        UserArchiveLink: The relationship link containing the exact role, if successful.
        
    Raises:
        InsufficientPermissionsError: If the user is lacking access or the required role.
    """
    statement = select(UserArchiveLink).where(
        UserArchiveLink.user_id == user_id,
        UserArchiveLink.archive_id == archive_id
    )
    link = session.exec(statement).first()

    if not link or link.role not in allowed_roles:
        raise InsufficientPermissionsError(
            f"User {user_id} does not have sufficient permissions for archive {archive_id}. "
            f"Required one of: {[r.value for r in allowed_roles]}"
        )
    
    return link


def get_all_piece_std_names(session: Session, archive_id: int) -> List[str]:
    """
    Retrieve a list of std_name for all pieces belonging to a specific archive.
    """
    statement = select(Piece.std_name).where(Piece.archive_id == archive_id)
    return list(session.exec(statement).all())

def get_all_digitalized_piece_std_names(session: Session, archive_id: int) -> List[str]:
    """
    Retrieve a list of std_name for all pieces digitalized belonging to a specific archive.
    """    
    statement = select(Piece.std_name).where(Piece.archive_id == archive_id, Piece.digitalized.is_(True))
    return list(session.exec(statement).all())

def add_piece_to_archive(
    session: Session,
    piece: "PieceCreate",
    files: List[str],
    file_manager: ArchiveFileManager
) -> "Piece":
    """
    Add a new piece to an archive with associated files.
    
    This function creates the directory structure, copies files to the archive,
    and saves the piece metadata to the database.
    
    Args:
        session: The database session.
        piece: PieceCreate object containing piece metadata.
        files: List of absolute file paths to copy into the archive.
        file_manager: ArchiveFileManager instance tied to the specific archive path.
    
    Returns:
        Piece: The created Piece object.
        
    Raises:
        FileCouldNotBeReadException: If file operations fail.
    """
    folder_name = file_manager.parse_name_to_file_manager(piece.std_name)
    
    # Create the directory structure in the archive
    file_manager.make_dir(folder_name)

    # Copy files to the archive
    files_copied = file_manager.copy_files_in_archive(folder_name, files)
    
    if not files_copied:
        raise FileCouldNotBeReadException("Failed to copy files to archive")

    return create_piece(session, piece)