import pytest
from sqlmodel import Session, SQLModel, create_engine
from backend.app.crud.piece_crud import create_piece, update_piece, get_piece, delete_piece
from backend.app.models.piece import Piece, PieceCreate
from backend.app.models.author import Author
from backend.app.models.type import Type
from backend.app.models.archive import Archive
from backend.app.models.user_archive_link import UserArchiveLink  # Required for Archive relationship registry
from backend.app.models.user import User  # Required for UserArchiveLink relationship registry
from backend.app.models.role import Role  # Required for User relationship registry

@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine("sqlite:///:memory:")
    # Create tables in the in-memory database
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        # Create default dependencies (authors, types) for foreign keys
        author1 = Author(name="Author 1")
        author2 = Author(name="Author 2")
        type1 = Type(name="Type 1")
        type2 = Type(name="Type 2")
        archive1 = Archive(name="Archive 1")
        archive2 = Archive(name="Archive 2")
        session.add_all([author1, author2, type1, type2, archive1, archive2])
        session.commit()
        yield session

def test_create_piece_normal(session: Session):
    piece_in = PieceCreate(
        cod=101,
        name="Symphony No. 5",
        handwrited=False,
        parted=True,
        digitalized=True,
        author_id=1,
        type_id=1,
        archive_id=1
    )
    piece = create_piece(session, piece_in)
    
    assert piece.id is not None
    assert piece.cod == 101
    assert piece.name == "Symphony No. 5"
    assert piece.handwrited is False
    assert piece.parted is True
    assert piece.digitalized is True
    assert piece.author_id == 1
    assert piece.type_id == 1
    assert piece.archive_id == 1

def test_create_piece_extreme(session: Session):
    # Extreme: very large cod, very long name, combinations of bools
    long_name = "A" * 1000
    piece_in = PieceCreate(
        cod=999999999,
        name=long_name,
        handwrited=True,
        parted=False,
        digitalized=True,
        author_id=1,
        type_id=1,
        archive_id=2
    )
    piece = create_piece(session, piece_in)
    
    assert piece.id is not None
    assert piece.cod == 999999999
    assert piece.name == long_name
    assert piece.handwrited is True
    assert piece.parted is False
    assert piece.digitalized is True
    assert piece.author_id == 1
    assert piece.type_id == 1
    assert piece.archive_id == 2


def test_update_piece_every_field(session: Session):
    # Initial piece
    piece_in = PieceCreate(
        cod=10, name="Original", handwrited=False, parted=False,
        digitalized=False, author_id=1, type_id=1, archive_id=1
    )
    piece = create_piece(session, piece_in)
    piece_id = piece.id

    # Update absolutely everything
    update_data = PieceCreate(
        cod=0, # Extreme case: cod goes to 0
        name="", # Extreme case: empty name but explicitly provided
        handwrited=True,
        parted=True,
        digitalized=True,
        author_id=2, # Changing foreign keys
        type_id=2,
        archive_id=2
    )
    updated_piece = update_piece(session, piece_id, update_data)
    
    assert updated_piece is not None
    assert updated_piece.id == piece_id
    assert updated_piece.cod == 0
    assert updated_piece.name == ""
    assert updated_piece.handwrited is True
    assert updated_piece.parted is True
    assert updated_piece.digitalized is True
    assert updated_piece.author_id == 2
    assert updated_piece.type_id == 2
    assert updated_piece.archive_id == 2


def test_update_piece_non_existent(session: Session):
    update_data = PieceCreate(
        cod=1, name="Ghost", handwrited=False, parted=False, digitalized=False, author_id=1, type_id=1, archive_id=1
    )
    result = update_piece(session, 9999, update_data)
    assert result is None


def test_get_piece_existing_and_non_existent(session: Session):
    piece_in = PieceCreate(
        cod=1, name="Find me", handwrited=True, parted=True, digitalized=True, author_id=1, type_id=1, archive_id=1
    )
    piece = create_piece(session, piece_in)
    
    # Existing
    found = get_piece(session, piece.id)
    assert found is not None
    assert found.name == "Find me"
    assert found.archive_id == 1
    
    # Non-existent
    not_found = get_piece(session, 9999)
    assert not_found is None


def test_delete_piece(session: Session):
    piece_in = PieceCreate(
        cod=404, name="To Delete", handwrited=True, parted=True, digitalized=True, author_id=1, type_id=1, archive_id=1
    )
    piece = create_piece(session, piece_in)
    piece_id = piece.id
    
    # Valid deletion
    deleted = delete_piece(session, piece_id)
    assert deleted is True
    
    # Verify it doesn't exist
    assert get_piece(session, piece_id) is None
    
    # Delete non-existent
    deleted_again = delete_piece(session, piece_id)
    assert deleted_again is False