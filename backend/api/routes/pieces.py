from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from requests import session
from sqlmodel import Session

from backend.api.dependencies.database import get_session
from backend.api.dependencies.file_manager import get_archive_file_manager
from backend.api.dependencies.permissions import require_archive_viewer, require_archive_editor
from backend.app.models.piece import PieceCreate, PiecePublic
from backend.app.custom_order.instrument_sorter import InstrumentSorter
from backend.app.files_management.archive_file_manager import ArchiveFileManager
from backend.app.crud.piece_crud import (
    get_piece as _get_piece,
    get_pieces as _get_pieces
)
from backend.app.error import (
    FileCouldNotBeReadException,
    PieceCodAlreadyExistsError,
    PieceNameAlreadyExistsError
)
from backend.app.services.archive_services import (
    add_piece_to_archive as _add_piece_to_archive,
    add_files_to_existing_piece as _add_files_to_existing_piece,
    delete_piece_from_archive as _delete_piece_from_archive,
    update_piece_in_archive as _update_piece_in_archive,
    get_all_piece_std_names as _get_all_piece_std_names,
    get_all_digitalized_piece_std_names as _get_all_digitalized_piece_std_names
)
from backend.app.services.pieces_services import (
    get_scores as _get_piece_scores,
    get_scores_and_page_counts as _get_scores_and_page_counts
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

@router.get("/", response_model=List[PiecePublic])
def get_pieces(
    archive_id: int, 
    session: Session = Depends(get_session), 
    _ = Depends(require_archive_viewer)
):
    """Retrieve a list of pieces in the archive."""
    return _get_pieces(session, archive_id)

@router.get("/{piece_std_name}/scores", response_model=List[str])
def get_piece_scores(
        archive_id: int,
        piece_std_name: str,
        file_manager: ArchiveFileManager = Depends(get_archive_file_manager),
        _ = Depends(require_archive_viewer)
):
    """Get the scores of a piece."""
    try:
        scores = _get_piece_scores(piece_std_name, file_manager)
        return InstrumentSorter.sort_instruments(scores) # Sort the instrument names
    except FileCouldNotBeReadException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )

@router.get("/{piece_std_name}/scores/page_counts", response_model=List[tuple[str, int]])
def get_piece_scores_and_page_counts(
    archive_id: int,
    piece_std_name: str,
    file_manager: ArchiveFileManager = Depends(get_archive_file_manager),
    _ = Depends(require_archive_viewer)
):
    """Get the scores of a piece along with their page counts."""
    try:
        scores_and_page_counts = _get_scores_and_page_counts(piece_std_name, file_manager)
        
        # Sort the list of tuples by instrument name using the sorter
        sorted_scores = InstrumentSorter.sort_instruments([score for score, _ in scores_and_page_counts])
        score_dict = {score: count for score, count in scores_and_page_counts}
        
        return [(score, score_dict[score]) for score in sorted_scores]
    except FileCouldNotBeReadException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )

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
    except (PieceCodAlreadyExistsError, PieceNameAlreadyExistsError) as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(e)
        )
    except FileCouldNotBeReadException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.put("/{piece_id}", response_model=PiecePublic)
def update_piece(
    archive_id: int,
    piece_id: int,
    piece: PieceCreate,
    added_files: List[str] | None = None,
    removed_files: List[str] | None = None,
    session: Session = Depends(get_session),
    file_manager: ArchiveFileManager = Depends(get_archive_file_manager),
    _ = Depends(require_archive_editor)
):
    """Update an existing piece in the archive."""
    try:
        
        if removed_files is None:
            pass #TODO: Implement the remove of the files
        if added_files is not None and added_files != []:
            _add_files_to_existing_piece(session, piece_id, added_files, file_manager) # Add new files first to handle potential file-related errors before updating piece data
        return _update_piece_in_archive(session, piece_id, piece, file_manager)
    except (PieceCodAlreadyExistsError, PieceNameAlreadyExistsError) as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(e)
        )
    except FileCouldNotBeReadException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
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
