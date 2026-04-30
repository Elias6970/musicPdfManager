import pytest
from sqlmodel import SQLModel, Session, create_engine, Field, Relationship
from typing import Optional
from backend.app.models.author import Author
from backend.app.crud.author_crud import (
    create_author,
    get_author_by_id,
    get_author_by_name,
    delete_author
)
from backend.app.services.author_service import get_or_create_author


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

def test_get_or_create_author(session: Session):
    # Standard creation
    author1 = get_or_create_author(session, "Beethoven")
    assert author1.id is not None
    assert author1.name == "Beethoven"

    # Fetch existing
    author2 = get_or_create_author(session, "Beethoven")
    assert author1.id == author2.id

    # Extreme: Empty string
    author_empty = get_or_create_author(session, "")
    assert author_empty.name == ""

    # Extreme: Special characters and long string
    long_name = "A" * 1000 + "🚀&^%"
    author_long = get_or_create_author(session, long_name)
    assert author_long.name == long_name

def test_get_author_by_id(session: Session):
    author = get_or_create_author(session, "Mozart")
    
    # Standard fetch
    fetched = get_author_by_id(session, author.id)
    assert fetched is not None
    assert fetched.name == "Mozart"

    # Extreme: Non-existent ID
    missing = get_author_by_id(session, 999999)
    assert missing is None

def test_get_author_by_name(session: Session):
    get_or_create_author(session, "Bach")
    
    # Standard fetch
    fetched = get_author_by_name(session, "Bach")
    assert fetched is not None
    assert fetched.name == "Bach"

    # Extreme: Non-existent name
    missing = get_author_by_name(session, "Unknown Composer")
    assert missing is None

def test_delete_author(session: Session):
    author = get_or_create_author(session, "Chopin")
    author_id = author.id
    
    # Standard deletion
    result = delete_author(session, author_id)
    assert result is True
    assert get_author_by_id(session, author_id) is None

    # Extreme: Delete already deleted / non-existent author
    result_missing = delete_author(session, author_id)
    assert result_missing is False

    # Extreme: ID out of bounds
    result_invalid = delete_author(session, -1)
    assert result_invalid is False