from sqlmodel import Session, select
from backend.app.models.author import Author

def get_or_create_author(session: Session, author_name: str) -> Author:
    # Try to find the existing author by name
    statement = select(Author).where(Author.name == author_name)
    existing_author = session.exec(statement).first()
    
    if existing_author:
        return existing_author
    
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

def delete_author(session: Session, author_id: int) -> bool:
    author = session.get(Author, author_id)
    if not author:
        return False
    session.delete(author)
    session.commit()
    return True