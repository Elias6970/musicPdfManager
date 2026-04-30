from typing import Optional
from sqlmodel import Session, select
from backend.app.models.piece import Piece, PieceCreate

def create_piece(session: Session, piece_in: PieceCreate) -> Piece:
    db_piece = Piece.model_validate(piece_in)
    session.add(db_piece)
    session.commit()
    session.refresh(db_piece)
    return db_piece

def update_piece(session: Session, piece_id: int, piece_in: PieceCreate) -> Optional[Piece]:
    """
    Updates the piece with the given ID using the piece_in data.
    Params:
    - session: The database session to use for the operation.
    - piece_id: The ID of the piece to update.
    - piece_in: The data to update the piece with. It ignores author_name and type_names. They need to be set in author_id and type_id respectively.
    Returns:
    - The updated Piece object if the update was successful, or None if the piece with the given ID does not exist.
    """
    db_piece = session.get(Piece, piece_id)
    if not db_piece:
        return None
    piece_data = piece_in.model_dump(exclude_unset=True, exclude_computed_fields=True)

    for key, value in piece_data.items():
            if hasattr(db_piece, key):
                setattr(db_piece, key, value)

    # Increment version manually on update
    db_piece.version = (db_piece.version or 0) + 1
    
    session.add(db_piece)
    session.commit()
    session.refresh(db_piece)
    return db_piece

def increment_piece_version(session: Session, piece_id: int) -> Optional[Piece]:
    db_piece = session.get(Piece, piece_id)
    if not db_piece:
        return None
    db_piece.version = (db_piece.version or 0) + 1
    session.add(db_piece)
    session.commit()
    session.refresh(db_piece)
    return db_piece

def get_piece(session: Session, piece_id: int) -> Optional[Piece]:
    return session.get(Piece, piece_id)

def get_pieces(session: Session, archive_id: int) -> list[Piece]:
    return list(session.exec(select(Piece).where(Piece.archive_id == archive_id)).all())

def delete_piece(session: Session, piece_id: int) -> bool:
    db_piece = session.get(Piece, piece_id)
    if not db_piece:
        return False
    session.delete(db_piece)
    session.commit()
    return True
