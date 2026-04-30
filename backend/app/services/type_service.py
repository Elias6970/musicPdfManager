from sqlmodel import Session
from typing import Sequence
from backend.app.models.type import Type
import backend.app.crud.type_crud as type_crud

def get_or_create_type(session: Session, type_name: str) -> Type:
    existing_type = type_crud.get_type_by_name(session, type_name)
    if existing_type:
        return existing_type
    return type_crud.create_type(session, type_name)

def get_type_by_id(session: Session, type_id: int) -> Type | None:
    return type_crud.get_type_by_id(session, type_id)

def get_type_by_name(session: Session, type_name: str) -> Type | None:
    return type_crud.get_type_by_name(session, type_name)

def get_all_types(session: Session) -> Sequence[Type]:
    return type_crud.get_all_types(session)

def get_all_types_for_archive(session: Session, archive_id: int) -> Sequence[Type]:
    return type_crud.get_all_types_for_archive(session, archive_id)

def delete_type(session: Session, type_id: int) -> bool:
    return type_crud.delete_type(session, type_id)
