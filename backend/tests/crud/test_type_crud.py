import pytest
from sqlmodel import SQLModel, Session, create_engine, Field, Relationship
from typing import Optional
from backend.app.models.type import Type
from backend.app.crud.type_crud import (
    get_or_create_type,
    get_type_by_id,
    get_type_by_name,
    delete_type
)

@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

def test_get_or_create_type(session: Session):
    # Standard creation
    type1 = get_or_create_type(session, "Symphony")
    assert type1.id is not None
    assert type1.name == "Symphony"

    # Fetch existing
    type2 = get_or_create_type(session, "Symphony")
    assert type1.id == type2.id

    # Extreme: Empty string
    type_empty = get_or_create_type(session, "")
    assert type_empty.name == ""

    # Extreme: Special characters and long string
    long_name = "T" * 1000 + "🎵&^%"
    type_long = get_or_create_type(session, long_name)
    assert type_long.name == long_name

def test_get_type_by_id(session: Session):
    type_obj = get_or_create_type(session, "Concerto")
    
    # Standard fetch
    fetched = get_type_by_id(session, type_obj.id)
    assert fetched is not None
    assert fetched.name == "Concerto"

    # Extreme: Non-existent ID
    missing = get_type_by_id(session, 999999)
    assert missing is None

def test_get_type_by_name(session: Session):
    get_or_create_type(session, "Sonata")
    
    # Standard fetch
    fetched = get_type_by_name(session, "Sonata")
    assert fetched is not None
    assert fetched.name == "Sonata"

    # Extreme: Non-existent name
    missing = get_type_by_name(session, "Unknown Type")
    assert missing is None

def test_delete_type(session: Session):
    type_obj = get_or_create_type(session, "March")
    type_id = type_obj.id
    
    # Standard deletion
    result = delete_type(session, type_id)
    assert result is True
    assert get_type_by_id(session, type_id) is None

    # Extreme: Delete already deleted / non-existent type
    result_missing = delete_type(session, type_id)
    assert result_missing is False

    # Extreme: ID out of bounds
    result_invalid = delete_type(session, -1)
    assert result_invalid is False