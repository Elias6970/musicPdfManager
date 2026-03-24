from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from backend.api.dependencies.database import get_session
from backend.api.dependencies.file_manager import get_archive_file_manager
from backend.api.dependencies.permissions import require_archive_viewer, require_archive_editor

from backend.app.models.piece import PieceCreate, PiecePublic
from backend.app.files_management.archive_file_manager import ArchiveFileManager
from backend.app.crud.piece_crud import get_piece as _get_piece
from backend.app.error import FileCouldNotBeReadException
from backend.app.services.archive_services import (
    add_piece_to_archive as _add_piece_to_archive,
    add_files_to_existing_piece as _add_files_to_existing_piece,
    delete_piece_from_archive as _delete_piece_from_archive,
    get_all_piece_std_names as _get_all_piece_std_names,
    get_all_digitalized_piece_std_names as _get_all_digitalized_piece_std_names
)

router = APIRouter(prefix="/archives/{archive_id}/pieces", tags=["pieces"])

@router.get("/std", response_model=List[str])
def get_all_piece_std_names(
    archive_id: int, 
    session: Session = Depends(get_session), 
    _ = Depends(require_archive_viewer)
):
    """Retrieve a list of std_name for all pieces in the archive."""
    return _get_all_piece_std_names(session, archive_id)

@router.get("/std/digitalized", response_model=List[str])
def get_all_digitalized_piece_std_names(
    archive_id: int, 
    session: Session = Depends(get_session), 
    _ = Depends(require_archive_viewer)
):
    """Retrieve a list of std_name for all digitalized pieces in the archive."""
    return _get_all_digitalized_piece_std_names(session, archive_id)

@router.get("/{piece_id}", response_model=PiecePublic)
def get_piece(
    archive_id: int, 
    piece_id: int, 
    session: Session = Depends(get_session), 
    _ = Depends(require_archive_viewer)
):
    """Retrieve a piece by ID."""
    piece = _get_piece(session, piece_id)
    if not piece:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Piece with ID {piece_id} not found",
        )
    return piece

@router.post("/", response_model=PiecePublic, status_code=status.HTTP_201_CREATED)
def add_piece_to_archive(
    archive_id: int,
    piece: PieceCreate,
    files: List[str],
    session: Session = Depends(get_session),
    file_manager: ArchiveFileManager = Depends(get_archive_file_manager),
    _ = Depends(require_archive_editor)
):
    """Add a new piece to an archive with associated files."""
    try:
        return _add_piece_to_archive(session, piece, files, file_manager)
    except FileCouldNotBeReadException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.post("/{piece_id}/files", response_model=PiecePublic)
def add_files_to_existing_piece(
    archive_id: int,
    piece_id: int,
    files: List[str],
    session: Session = Depends(get_session),
    file_manager: ArchiveFileManager = Depends(get_archive_file_manager),
    _ = Depends(require_archive_editor)
):
    """Add additional files to an existing piece in the archive."""
    try:
        return _add_files_to_existing_piece(session, piece_id, files, file_manager)
    except FileCouldNotBeReadException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )


@router.delete("/{piece_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_piece_from_archive(
    archive_id: int,
    piece_id: int,
    session: Session = Depends(get_session),
    file_manager: ArchiveFileManager = Depends(get_archive_file_manager),
    _ = Depends(require_archive_editor)
):
    """Delete a piece from the archive and database."""
    try:
        success = _delete_piece_from_archive(session, piece_id, file_manager)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to delete piece",
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )
