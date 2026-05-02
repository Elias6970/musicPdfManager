import os
from typing import List
from sqlmodel import Session, select
from backend.app.models.archive import Archive
from backend.app.models.author import Author
from backend.app.models.type import Type
from backend.app.services.author_service import get_or_create_author
from backend.app.services.type_service import get_or_create_type
from backend.app.models.user import User
from backend.app.models.user_archive_link import UserArchiveLink, ArchiveRole
from backend.app.error import (
    FileCouldNotBeReadException, InsufficientPermissionsError,
    PieceCodAlreadyExistsError, PieceNameAlreadyExistsError
)
from backend.app.models.piece import Piece, PieceCreate
from backend.app.crud.piece_crud import create_piece, get_piece, delete_piece, update_piece
from backend.app.files_management.archive_file_manager import ArchiveFileManager
from backend.app.settings import get_server_settings


def check_archive_role(
    session: Session,
    user_id: int,
    archive_id: int,
    allowed_roles: List[ArchiveRole]
) -> UserArchiveLink:
    """
    Core business logic to verify if a user has sufficient permissions for an archive.
    Admin users can access all archives regardless of their specific role.

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

    #Check if the user is admin
    user = session.get(User, user_id)
    if user and user.role and user.role.name == "admin":
        return UserArchiveLink(user_id=user_id, archive_id=archive_id, role=ArchiveRole.OWNER)

    #Check archive roles
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

def get_archive_path(session: Session, archive_id: int) -> str:
    """
    Retrieve the file system path for a given archive ID.

    Args:
        session: The database session.
        archive_id: The ID of the archive.
    Returns:
        str: The file system path of the archive.
    """
    archive = session.exec(select(Archive).where(Archive.id == archive_id)).first()
    if not archive:
        raise ValueError(f"Archive with id {archive_id} not found")
    if not archive.path:
        raise ValueError(f"Archive with id {archive_id} does not have a valid path")
    
    return os.path.join(get_server_settings().archive_root, archive.path)

def get_all_piece_std_names(session: Session, archive_id: int) -> List[str]:
    """
    Retrieve a list of std_name for all pieces belonging to a specific archive.
    """
    statement = select(Piece).where(Piece.archive_id == archive_id)
    return [piece.std_name for piece in session.exec(statement).all()]


def get_all_digitalized_piece_std_names(session: Session, archive_id: int) -> List[str]:
    """
    Retrieve a list of std_name for all pieces digitalized belonging to a specific archive.
    """    
    statement = select(Piece).where(Piece.archive_id == archive_id, Piece.digitalized == True)
    return [piece.std_name for piece in session.exec(statement).all()]


def add_piece_to_archive(
    session: Session,
    piece: "PieceCreate",
    files: List[str],
    file_manager: ArchiveFileManager
) -> "Piece":
    """
    Add a new piece to an archive with associated files.
    
    This function creates the directory structure, copies files to the archive,
    and saves the piece metadata to the database. If author or type names are provided instead of IDs, 
    it will create or fetch those records as well.
    
    Args:
        session: The database session.
        piece: PieceCreate object containing piece metadata.
        files: List of absolute file paths to copy into the archive.
        file_manager: ArchiveFileManager instance tied to the specific archive path.
    
    Returns:
        Piece: The created Piece object.
        
    Raises:
        PieceCodAlreadyExistsError: If a piece with the same cod already exists in the archive.
        PieceNameAlreadyExistsError: If a piece with the same name already exists in the archive.
        FileCouldNotBeReadException: If file operations fail.
    """

    # Check if cod already exists in the archive
    existing_cod = session.exec(select(Piece).where(Piece.cod == piece.cod, Piece.archive_id == piece.archive_id)).first()
    if existing_cod:
        raise PieceCodAlreadyExistsError(f"A piece with cod {piece.cod} already exists in archive {piece.archive_id}.")

    # Check if name already exists in the archive
    existing_name = session.exec(select(Piece).where(Piece.name == piece.name, Piece.archive_id == piece.archive_id)).first()
    if existing_name:
        raise PieceNameAlreadyExistsError(f"A piece with name '{piece.name}' already exists in archive {piece.archive_id}.")

    #Create directory and copy the files
    folder_name = file_manager.parse_name_to_file_manager(piece.std_name)
    file_manager.make_dir(folder_name)
    
    settings = get_server_settings()
    temp_folder = settings.temp_upload_folder
    temp_files = [os.path.join(temp_folder, f) for f in files]
    
    files_copied = file_manager.copy_files_in_archive(folder_name, temp_files)
    if not files_copied:
        raise FileCouldNotBeReadException("Failed to copy files to archive")

    # Handle author and type creation if names are provided instead of IDs
    if piece.author_id is None and piece.author_name:
        author = get_or_create_author(session, piece.author_name)
        piece.author_id = author.id

    if piece.type_id is None and piece.type_name:
        type_ = get_or_create_type(session, piece.type_name)
        piece.type_id = type_.id


    return create_piece(session, piece)

def update_piece_in_archive(
    session: Session,
    piece_id: int,
    piece_in: "PieceCreate",
    file_manager: ArchiveFileManager
) -> "Piece":
    """
    Update an existing piece in the archive.
    
    Args:
        session: The database session.
        piece_id: The ID of the existing piece.
        piece_in: PieceCreate object containing updated piece metadata.
        file_manager: ArchiveFileManager instance tied to the specific archive path.
        
    Returns:
        Piece: The updated Piece object.
        
    Raises:
        ValueError: If the piece does not exist.
        PieceCodAlreadyExistsError: If a piece with the same cod already exists in the archive.
        PieceNameAlreadyExistsError: If a piece with the same name already exists in the archive.
    """
    piece = get_piece(session, piece_id)
    if not piece:
        raise ValueError(f"Piece with ID {piece_id} not found")

    # Check if new cod already exists for another piece
    existing_cod = session.exec(select(Piece).where(Piece.cod == piece_in.cod, Piece.archive_id == piece_in.archive_id, Piece.id != piece_id)).first()
    if existing_cod:
        raise PieceCodAlreadyExistsError(f"A piece with cod {piece_in.cod} already exists in archive {piece_in.archive_id}.")

    # Check if new name already exists for another piece
    existing_name = session.exec(select(Piece).where(Piece.name == piece_in.name, Piece.archive_id == piece_in.archive_id, Piece.id != piece_id)).first()
    if existing_name:
        raise PieceNameAlreadyExistsError(f"A piece with name '{piece_in.name}' already exists in archive {piece_in.archive_id}.")

    # Handle author and type update if names are provided instead of IDs
    if piece_in.author_id is None and piece_in.author_name:
        author = get_or_create_author(session, piece_in.author_name)
        piece_in.author_id = author.id

    if piece_in.type_id is None and piece_in.type_name:
        type_ = get_or_create_type(session, piece_in.type_name)
        piece_in.type_id = type_.id

    # Store the old folder name before the update because the std_name might change after the update
    old_folder_name = file_manager.parse_name_to_file_manager(piece.std_name)

    updated_piece = update_piece(session, piece_id, piece_in)
    if not updated_piece:
        raise ValueError(f"Piece with ID {piece_id} not found")
    
    # Update the folder name if changed
    new_folder_name = file_manager.parse_name_to_file_manager(updated_piece.std_name)
    if old_folder_name != new_folder_name:
        file_manager.change_piece_dir_name(old_folder_name, new_folder_name)
        
    return updated_piece

def add_file_to_existing_piece(
        session: Session,
        piece_id: int,
        file_bytes: bytes,
        filename: str,
        file_manager: ArchiveFileManager
) -> "Piece":
    """
    Add a new file to an existing piece in the archive.
    
    Args:
        session: The database session.
        piece_id: The ID of the existing piece.
        file_bytes: The content of the file as bytes.
        filename: The name of the file to be added.
        file_manager: ArchiveFileManager instance tied to the specific archive path.
        
    Returns:
        Piece: The updated Piece object with the new file added.
        
    Raises:
        ValueError: If the piece does not exist.
        FileCouldNotBeReadException: If file operations fail.
    """
    piece = get_piece(session, piece_id)
    if not piece:
        raise ValueError(f"Piece with ID {piece_id} not found")
        
    folder_name = file_manager.parse_name_to_file_manager(piece.std_name)
    file_added = file_manager.add_file_to_piece(folder_name, file_bytes, filename)

    if file_added:
        return piece
    else:
        raise FileCouldNotBeReadException("Failed to add file to existing piece in archive")


def add_files_to_existing_piece(
    session: Session,
    piece_id: int,
    files: List[str],
    file_manager: ArchiveFileManager
) -> "Piece":
    """
    Add additional files to an existing piece in the archive.
    
    Args:
        session: The database session.
        piece_id: The ID of the existing piece.
        files: List of absolute file paths to copy into the archive.
        file_manager: ArchiveFileManager instance tied to the specific archive path.
        
    Returns:
        Piece: The updated Piece object.
        
    Raises:
        ValueError: If the piece does not exist.
        FileCouldNotBeReadException: If file operations fail.
    """
    piece = get_piece(session, piece_id)
    if not piece:
        raise ValueError(f"Piece with ID {piece_id} not found")
        
    folder_name = file_manager.parse_name_to_file_manager(piece.std_name)
    
    settings = get_server_settings()
    temp_folder = settings.temp_upload_folder
    temp_files = [os.path.join(temp_folder, f) for f in files]
    
    files_copied = file_manager.copy_files_in_archive(folder_name, temp_files)
    if not files_copied:
        raise FileCouldNotBeReadException("Failed to copy additional files to archive")
        
    return piece


def delete_piece_from_archive(
    session: Session,
    piece_id: int,
    file_manager: ArchiveFileManager
) -> bool:
    """
    Delete a piece from the archive and database.
    
    Args:
        session: The database session.
        piece_id: The ID of the piece to delete.
        file_manager: ArchiveFileManager instance tied to the specific archive path.
        
    Returns:
        bool: True if deleted successfully.
        
    Raises:
        ValueError: If the piece does not exist in the database.
    """
    piece = get_piece(session, piece_id)
    if not piece:
        raise ValueError(f"Piece with ID {piece_id} not found")
        
    folder_name = file_manager.parse_name_to_file_manager(piece.std_name)
    
    # Delete from the file system
    file_manager.delete_piece(folder_name)
    
    # Delete from the database
    return delete_piece(session, piece_id)


def get_all_archives_for_user(session: Session, user_id: int) -> List[Archive]:
    """
    Retrieve all archives that a user has access to, including those they own, edit, or view.
    
    Args:
        session: The database session.
        user_id: The ID of the user.
    """
    statement = select(Archive).join(UserArchiveLink).where(UserArchiveLink.user_id == user_id)
    return list(session.exec(statement).all())