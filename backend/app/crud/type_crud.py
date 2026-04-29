from sqlmodel import Session, select
from typing import Sequence
from backend.app.models.type import Type
from backend.app.models.piece import Piece

def create_type(session: Session, type_name: str) -> Type:
    new_type = Type(name=type_name)
    session.add(new_type)
    session.commit()
    session.refresh(new_type)
    return new_type

def get_type_by_id(session: Session, type_id: int) -> Type | None:
    return session.get(Type, type_id)

def get_type_by_name(session: Session, type_name: str) -> Type | None:
    statement = select(Type).where(Type.name == type_name)
    return session.exec(statement).first()

def get_all_types(session: Session) -> Sequence[Type]:
    statement = select(Type)
    return session.exec(statement).all()

def get_all_types_for_archive(session: Session, archive_id: int) -> Sequence[Type]:
    statement = select(Type).join(Piece).where(Piece.archive_id == archive_id).distinct()
    return session.exec(statement).all()

def delete_type(session: Session, type_id: int) -> bool:
    db_type = session.get(Type, type_id)
    if not db_type:
        return False
    session.delete(db_type)
    session.commit()
    return True