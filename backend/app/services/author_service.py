from sqlmodel import Session
from typing import Sequence
from backend.app.models.author import Author
import backend.app.crud.author_crud as author_crud

def get_or_create_author(session: Session, author_name: str) -> Author:
    existing_author = author_crud.get_author_by_name(session, author_name)
    if existing_author:
        return existing_author
    return author_crud.create_author(session, author_name)

def get_author_by_id(session: Session, author_id: int) -> Author | None:
    return author_crud.get_author_by_id(session, author_id)

def get_author_by_name(session: Session, author_name: str) -> Author | None:
    return author_crud.get_author_by_name(session, author_name)

def get_all_authors(session: Session) -> Sequence[Author]:
    return author_crud.get_all_authors(session)

def get_all_authors_for_archive(session: Session, archive_id: int) -> Sequence[Author]:
    return author_crud.get_all_authors_for_archive(session, archive_id)

def delete_author(session: Session, author_id: int) -> bool:
    return author_crud.delete_author(session, author_id)
