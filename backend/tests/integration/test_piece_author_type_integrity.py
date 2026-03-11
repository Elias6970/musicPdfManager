import pytest
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy import event
from backend.app.models.piece import Piece, PieceCreate
from backend.app.models.author import Author
from backend.app.models.type import Type



@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine("sqlite:///:memory:")
    
    # Enable SQLite foreign key support for true integrity testing
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

def test_relationship_piece_author_type(session: Session):
    # 1. Create dependencies
    author = Author(name="Ludwig van Beethoven")
    p_type = Type(name="Symphony")
    
    session.add(author)
    session.add(p_type)
    session.commit()
    session.refresh(author)
    session.refresh(p_type)

    # 2. Create piece linked to them
    piece = Piece(
        cod=5,
        name="Symphony No. 5",
        handwrited=False,
        parted=True,
        digitalized=True,
        author_id=author.id,
        type_id=p_type.id
    )
    session.add(piece)
    session.commit()
    session.refresh(piece)

    # 3. Test relationships from Piece -> Author/Type
    assert piece.author is not None
    assert piece.author.name == "Ludwig van Beethoven"
    assert piece.type is not None
    assert piece.type.name == "Symphony"

    # 4. Test relationships from Author/Type -> Piece (List)
    assert len(author.pieces) == 1
    assert author.pieces[0].name == "Symphony No. 5"
    assert len(p_type.pieces) == 1
    assert p_type.pieces[0].cod == 5

def test_foreign_key_integrity_failure(session: Session):
    # Attempt to create a piece with non-existent author_id and type_id
    # Since we enabled PRAGMA foreign_keys=ON, this should raise an IntegrityError
    from sqlalchemy.exc import IntegrityError
    
    invalid_piece = Piece(
        cod=99,
        name="Invalid Piece",
        handwrited=False,
        parted=False,
        digitalized=False,
        author_id=9999, # Does not exist
        type_id=9999    # Does not exist
    )
    
    session.add(invalid_piece)
    
    with pytest.raises(IntegrityError):
        session.commit()
