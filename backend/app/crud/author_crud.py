from sqlmodel import Session, select
from typing import Sequence
from backend.app.models.author import Author
from backend.app.models.piece import Piece

def create_author(session: Session, author_name: str) -> Author:
    new_author = Author(name=author_name)
    session.add(new_author)
    session.commit()
    session.refresh(new_author)
    return new_author

def get_author_by_id(session: Session, author_id: int) -> Author | None:
    return session.get(Author, author_id)

def get_author_by_name(session: Session, author_name: str) -> Author | None:
    statement = select(Author).where(Author.name == author_name)
    return session.exec(statement).first()

def get_all_authors(session: Session) -> Sequence[Author]:
    statement = select(Author)
    return session.exec(statement).all()

def get_all_authors_for_archive(session: Session, archive_id: int) -> Sequence[Author]:
    statement = select(Author).join(Piece).where(Piece.archive_id == archive_id).distinct()
    return session.exec(statement).all()

def delete_author(session: Session, author_id: int) -> bool:
    author = session.get(Author, author_id)
    if not author:
        return False
    session.delete(author)
    session.commit()
    return True