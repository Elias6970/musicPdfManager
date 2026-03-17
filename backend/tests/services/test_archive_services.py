import pytest
from unittest.mock import MagicMock
from sqlmodel import Session, SQLModel, create_engine

from backend.app.models.piece import Piece, PieceCreate
from backend.app.models.archive import Archive
from backend.app.models.user_archive_link import UserArchiveLink, ArchiveRole
from backend.app.models.user import User
from backend.app.models.author import Author
from backend.app.models.type import Type
from backend.app.models.role import Role
from backend.app.error import FileCouldNotBeReadException, InsufficientPermissionsError

from backend.app.services.archive_services import (
    check_archive_role,
    get_all_piece_std_names,
    get_all_digitalized_piece_std_names,
    add_piece_to_archive,
    delete_piece_from_archive,
    add_files_to_existing_piece
)

@pytest.fixture(name="engine")
def engine_fixture():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    return engine

@pytest.fixture(name="session")
def session_fixture(engine):
    with Session(engine) as session:
        # Create base dependencies
        archive = Archive(name="Central Archive")
        user = User(name="testuser", email="test@test.com", password_hash="pw")
        
        session.add_all([archive, user])
        session.commit()
        
        # Link user to archive as OWNER
        link = UserArchiveLink(user_id=1, archive_id=1, role=ArchiveRole.OWNER)
        session.add(link)
        session.commit()
        
        yield session

@pytest.fixture(name="file_manager")
def file_manager_fixture():
    # Mocking the ArchiveFileManager directly
    fm = MagicMock()
    fm.parse_name_to_file_manager = MagicMock(side_effect=lambda x: x)
    return fm

def test_check_archive_role_success(session: Session):
    link = check_archive_role(session, user_id=1, archive_id=1, allowed_roles=[ArchiveRole.OWNER, ArchiveRole.EDITOR])
    assert link is not None
    assert link.role == ArchiveRole.OWNER

def test_check_archive_role_failure(session: Session):
    with pytest.raises(InsufficientPermissionsError):
        check_archive_role(session, user_id=1, archive_id=1, allowed_roles=[ArchiveRole.VIEWER])

    with pytest.raises(InsufficientPermissionsError):
        check_archive_role(session, user_id=99, archive_id=1, allowed_roles=[ArchiveRole.OWNER])

def test_get_all_piece_std_names(session: Session):
    p1 = Piece(cod=1, name="Piece 1", archive_id=1, digitalized=False, handwrited=False, parted=False)
    p2 = Piece(cod=2, name="Piece 2", archive_id=1, digitalized=True, handwrited=False, parted=False)
    session.add_all([p1, p2])
    session.commit()

    names = get_all_piece_std_names(session, 1)
    assert len(names) == 2
    assert "1-Piece 1" in names
    assert "2-Piece 2" in names

def test_get_all_digitalized_piece_std_names(session: Session):
    p1 = Piece(cod=1, name="Piece 1", archive_id=1, digitalized=False, handwrited=False, parted=False)
    p2 = Piece(cod=2, name="Piece 2", archive_id=1, digitalized=True, handwrited=False, parted=False)
    session.add_all([p1, p2])
    session.commit()

    names = get_all_digitalized_piece_std_names(session, 1)
    assert len(names) == 1
    assert names[0] == "2-Piece 2"

def test_add_piece_to_archive_success(session: Session, file_manager: MagicMock):
    piece_in = PieceCreate(
        cod=10, name="New", archive_id=1, handwrited=False, parted=False, digitalized=True
    )
    files = ["/tmp/file1.pdf", "/tmp/file2.pdf"]
    file_manager.copy_files_in_archive.return_value = True

    piece = add_piece_to_archive(session, piece_in, files, file_manager)

    file_manager.make_dir.assert_called_once_with("10-New")
    file_manager.copy_files_in_archive.assert_called_once_with("10-New", files)
    assert piece.id is not None
    assert piece.name == "New"

def test_add_piece_to_archive_failure(session: Session, file_manager: MagicMock):
    piece_in = PieceCreate(
        cod=11, name="Fail", archive_id=1, handwrited=False, parted=False, digitalized=True
    )
    file_manager.copy_files_in_archive.return_value = False

    with pytest.raises(FileCouldNotBeReadException):
        add_piece_to_archive(session, piece_in, [], file_manager)

def test_add_piece_to_archive_with_author_and_type_names(session: Session, file_manager: MagicMock):
    piece_in = PieceCreate(
        cod=12, name="With Author and Type", archive_id=1, 
        handwrited=False, parted=False, digitalized=True,
        author_name="Beethoven", type_name="Sonata"
    )
    file_manager.copy_files_in_archive.return_value = True

    piece = add_piece_to_archive(session, piece_in, [], file_manager)

    assert piece.author_id is not None
    assert piece.type_id is not None
    
    # Verify they were actually created in the DB
    author = session.get(Author, piece.author_id)
    assert author is not None
    assert author.name == "Beethoven"
    
    type_obj = session.get(Type, piece.type_id)
    assert type_obj is not None
    assert type_obj.name == "Sonata"

def test_delete_piece_from_archive_success(session: Session, file_manager: MagicMock):
    p1 = Piece(cod=1, name="ToDelete", archive_id=1, digitalized=False, handwrited=False, parted=False)
    session.add(p1)
    session.commit()

    assert p1.id is not None
    result = delete_piece_from_archive(session, p1.id, file_manager)
    assert result is True
    file_manager.delete_piece.assert_called_once_with("1-ToDelete")
    
    deleted_p = session.get(Piece, p1.id)
    assert deleted_p is None

def test_delete_piece_from_archive_failure(session: Session, file_manager: MagicMock):
    with pytest.raises(ValueError, match="Piece with ID 999 not found"):
        delete_piece_from_archive(session, 999, file_manager)

def test_add_files_to_existing_piece_success(session: Session, file_manager: MagicMock):
    p1 = Piece(cod=5, name="Existing", archive_id=1, digitalized=False, handwrited=False, parted=False)
    session.add(p1)
    session.commit()

    file_manager.copy_files_in_archive.return_value = True
    new_files = ["/tmp/new_file.pdf"]

    assert p1.id is not None
    updated_piece = add_files_to_existing_piece(session, p1.id, new_files, file_manager)
    assert updated_piece.id == p1.id
    file_manager.copy_files_in_archive.assert_called_once_with("5-Existing", new_files)

def test_add_files_to_existing_piece_not_found(session: Session, file_manager: MagicMock):
    with pytest.raises(ValueError):
        add_files_to_existing_piece(session, 999, ["test.pdf"], file_manager)

def test_add_files_to_existing_piece_copy_fail(session: Session, file_manager: MagicMock):
    p1 = Piece(cod=6, name="Existing2", archive_id=1, digitalized=False, handwrited=False, parted=False)
    session.add(p1)
    session.commit()

    file_manager.copy_files_in_archive.return_value = False
    
    with pytest.raises(FileCouldNotBeReadException):
        assert p1.id is not None
        add_files_to_existing_piece(session, p1.id, ["test.pdf"], file_manager)