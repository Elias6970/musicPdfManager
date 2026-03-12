import pytest
from sqlmodel import Session, SQLModel, create_engine
from backend.app.models.archive import Archive, ArchiveCreate
from backend.app.models.user import User
from backend.app.models.author import Author
from backend.app.models.type import Type
from backend.app.models.piece import Piece
from backend.app.models.user_archive_link import UserArchiveLink, ArchiveRole
from backend.app.crud.archive_crud import (
    create_archive,
    get_archive,
    get_all_archives,
    update_archive,
    delete_archive,
    add_user_to_archive,
    remove_user_from_archive,
    get_user_archive_role,
)

@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False}
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.fixture(name="sample_user")
def sample_user_fixture(session: Session):
    user = User(name="Sample User", email="sample@example.com", password_hash="dummy_hash")
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def test_create_archive(session: Session, sample_user: User):
    archive_in = ArchiveCreate(name="Test Archive")
    archive = create_archive(session, archive_in, sample_user.id)
    
    assert archive.id is not None
    assert archive.name == "Test Archive"
    assert archive.path is not None
    
    # Check if the user is linked as OWNER
    role = get_user_archive_role(session, archive.id, sample_user.id)
    assert role == ArchiveRole.OWNER

def test_get_archive(session: Session, sample_user: User):
    archive_in = ArchiveCreate(name="Get Archive")
    created_archive = create_archive(session, archive_in, sample_user.id)
    
    fetched_archive = get_archive(session, created_archive.id)
    assert fetched_archive is not None
    assert fetched_archive.id == created_archive.id
    assert fetched_archive.name == "Get Archive"

    not_found_archive = get_archive(session, 999)
    assert not_found_archive is None

def test_get_all_archives(session: Session, sample_user: User):
    create_archive(session, ArchiveCreate(name="Archive 1"), sample_user.id)
    create_archive(session, ArchiveCreate(name="Archive 2"), sample_user.id)
    create_archive(session, ArchiveCreate(name="Archive 3"), sample_user.id)
    
    archives = get_all_archives(session)
    assert len(archives) >= 3
    
    limited_archives = get_all_archives(session, limit=2)
    assert len(limited_archives) == 2
    
    offset_archives = get_all_archives(session, offset=1, limit=2)
    assert len(offset_archives) == 2
    assert offset_archives[0].id != archives[0].id

def test_update_archive(session: Session, sample_user: User):
    archive = create_archive(session, ArchiveCreate(name="Old Name"), sample_user.id)
    
    updated = update_archive(session, archive.id, ArchiveCreate(name="New Name"))
    assert updated is not None
    assert updated.name == "New Name"
    assert updated.id == archive.id
    
    not_found = update_archive(session, 999, ArchiveCreate(name="Fail"))
    assert not_found is None

def test_delete_archive(session: Session, sample_user: User):
    archive = create_archive(session, ArchiveCreate(name="Delete Me"), sample_user.id)
    
    # User linkage should cascade or at least the archive is removed
    deleted = delete_archive(session, archive.id)
    assert deleted is True
    
    fetched = get_archive(session, archive.id)
    assert fetched is None
    
    not_found_deleted = delete_archive(session, 999)
    assert not_found_deleted is False

def test_add_user_to_archive(session: Session, sample_user: User):
    archive = create_archive(session, ArchiveCreate(name="Test Link"), sample_user.id)
    
    # Create another user
    new_user = User(name="Other User", email="other@example.com", password_hash="dummy")
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    
    link = add_user_to_archive(session, archive.id, new_user.id, ArchiveRole.EDITOR)
    assert link is not None
    assert link.user_id == new_user.id
    assert link.archive_id == archive.id
    assert link.role == ArchiveRole.EDITOR
    
    # Invalid user / archive
    invalid_link = add_user_to_archive(session, 999, new_user.id, ArchiveRole.VIEWER)
    assert invalid_link is None

def test_remove_user_from_archive(session: Session, sample_user: User):
    archive = create_archive(session, ArchiveCreate(name="Test Unlink"), sample_user.id)
    
    removed = remove_user_from_archive(session, archive.id, sample_user.id)
    assert removed is True
    
    role = get_user_archive_role(session, archive.id, sample_user.id)
    assert role is None
    
    # Try removing non-existing link
    removed_fail = remove_user_from_archive(session, archive.id, sample_user.id)
    assert removed_fail is False

def test_get_user_archive_role(session: Session, sample_user: User):
    archive = create_archive(session, ArchiveCreate(name="Role Check"), sample_user.id)
    
    role = get_user_archive_role(session, archive.id, sample_user.id)
    assert role == ArchiveRole.OWNER
    
    none_role = get_user_archive_role(session, 999, sample_user.id)
    assert none_role is None
