import pytest
from sqlmodel import Session, SQLModel, create_engine
from unittest.mock import patch
from backend.app.models.user import User, UserCreate
from backend.app.crud.user_crud import (
    create_user,
    get_user_by_id,
    get_user_by_email,
    delete_user,
)

#USER CRUD DON'T APPLY LOGIC, JUST DB OPERATIONS

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

@pytest.mark.parametrize("name, email, password", [
    ("Normal Name", "normal@example.com", "pass123"),
    ("", "emptyname@example.com", "pass"),   # Empty name string
    ("NoEmail", "", "pass"),                 # Empty email string
    ("Whitespace", "   ", "   "),            # Only whitespaces
])
@patch("backend.app.crud.user_crud.get_password_hash")
def test_create_user(mock_hash, session: Session, name, email, password):
    mock_hash.return_value = "hashed_" + password
    user_in = UserCreate(name=name, email=email, password=password)
    user = create_user(session, user_in)
    
    assert user.id is not None
    assert user.name == name
    assert user.email == email
    assert user.password_hash == "hashed_" + password

@pytest.mark.parametrize("test_id_key, expected_found", [
    ("valid", True),
    (9999, False),    # Large non-existent ID
    (-1, False),      # Negative ID
    (0, False),       # Zero ID
])
def test_get_user_by_id(session: Session, sample_user: User, test_id_key, expected_found):
    query_id = sample_user.id if test_id_key == "valid" else test_id_key
    
    fetched = get_user_by_id(session, query_id)
    if expected_found:
        assert fetched is not None
        assert fetched.id == sample_user.id
    else:
        assert fetched is None

@pytest.mark.parametrize("test_email, expected_found", [
    ("sample@example.com", True),
    ("missing@example.com", False),
    ("", False),          # Empty string
    ("   ", False),       # Whitespace string
])
def test_get_user_by_email(session: Session, sample_user: User, test_email, expected_found):
    fetched = get_user_by_email(session, test_email)
    if expected_found:
        assert fetched is not None
        assert fetched.email == sample_user.email
    else:
        assert fetched is None

@pytest.mark.parametrize("test_id_key, expected_result", [
    ("valid", True),
    (9999, False),    # Large non-existent ID
    (-1, False),      # Negative ID
    (0, False),       # Zero ID
])
def test_delete_user(session: Session, sample_user: User, test_id_key, expected_result):
    query_id = sample_user.id if test_id_key == "valid" else test_id_key
    
    result = delete_user(session, query_id)
    assert result is expected_result
    
    if result is True:
        # Check that it's actually removed from the DB
        assert get_user_by_id(session, query_id) is None

def test_get_all_users(session: Session, sample_user: User):
    from backend.app.crud.user_crud import get_all_users
    users = get_all_users(session)
    assert len(users) == 1
    assert users[0].id == sample_user.id

