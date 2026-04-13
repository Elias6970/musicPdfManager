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
    db_piece = session.get(Piece, piece_id)
    if not db_piece:
        return None
    piece_data = piece_in.model_dump(exclude_unset=True)
    for key, value in piece_data.items():
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
    return session.exec(select(Piece).where(Piece.archive_id == archive_id)).all()

def delete_piece(session: Session, piece_id: int) -> bool:
    db_piece = session.get(Piece, piece_id)
    if not db_piece:
        return False
    session.delete(db_piece)
    session.commit()
    return True
