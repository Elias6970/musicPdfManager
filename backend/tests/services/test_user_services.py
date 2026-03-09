import pytest
from unittest.mock import MagicMock, patch
from sqlmodel import Session

from backend.app.services.user_services import login_user, register_user
from backend.app.models.token import Token
from backend.app.models.user import UserCreate
from backend.app.error import InvalidCredentialsError, EmailAlreadyRegisteredError, InvalidUserDataError

@pytest.fixture
def mock_session():
    return MagicMock(spec=Session)

@patch("backend.app.services.user_services.create_access_token")
@patch("backend.app.services.user_services.verify_password")
@patch("backend.app.services.user_services.user_crud.get_user_by_email")
def test_login_user_success(mock_get_user, mock_verify, mock_create_token, mock_session):
    # Arrange
    test_email = "test@example.com"
    test_password = "password123"
    
    mock_user = MagicMock()
    mock_user.id = 1
    mock_user.password_hash = "hashed_password123"
    
    mock_get_user.return_value = mock_user
    mock_verify.return_value = True
    mock_create_token.return_value = "fake_access_token"

    # Act
    result = login_user(session=mock_session, email=test_email, password=test_password)

    # Assert
    assert isinstance(result, Token)
    assert result.access_token == "fake_access_token"
    assert result.token_type == "bearer"
    
    mock_get_user.assert_called_once_with(mock_session, email=test_email)
    mock_verify.assert_called_once_with(plain_password=test_password, hashed_password="hashed_password123")
    mock_create_token.assert_called_once_with(subject=1)

@patch("backend.app.services.user_services.user_crud.get_user_by_email")
def test_login_user_not_found(mock_get_user, mock_session):
    # Arrange
    test_email = "missing@example.com"
    test_password = "password123"
    
    mock_get_user.return_value = None

    # Act & Assert
    with pytest.raises(InvalidCredentialsError) as exc_info:
        login_user(session=mock_session, email=test_email, password=test_password)
        
    assert str(exc_info.value) == "Email does not exist"
    mock_get_user.assert_called_once_with(mock_session, email=test_email)

@patch("backend.app.services.user_services.verify_password")
@patch("backend.app.services.user_services.user_crud.get_user_by_email")
def test_login_user_wrong_password(mock_get_user, mock_verify, mock_session):
    # Arrange
    test_email = "test@example.com"
    test_password = "wrongpassword"
    
    mock_user = MagicMock()
    mock_user.password_hash = "hashed_password123"
    
    mock_get_user.return_value = mock_user
    mock_verify.return_value = False

    # Act & Assert
    with pytest.raises(InvalidCredentialsError) as exc_info:
        login_user(session=mock_session, email=test_email, password=test_password)
        
    assert str(exc_info.value) == "Incorrect password"
    mock_get_user.assert_called_once_with(mock_session, email=test_email)
    mock_verify.assert_called_once_with(plain_password=test_password, hashed_password="hashed_password123")


@patch("backend.app.services.user_services.user_crud.get_user_by_email")
@patch("backend.app.services.user_services.user_crud.create_user")
def test_register_user_success(mock_create_user, mock_get_user, mock_session):
    # Arrange
    user_in = UserCreate(name="Test", email="new@example.com", password="password")
    mock_get_user.return_value = None  # user doesn't exist yet
    
    mock_created_user = MagicMock()
    mock_create_user.return_value = mock_created_user

    # Act
    result = register_user(session=mock_session, user_create=user_in)

    # Assert
    assert result == mock_created_user
    mock_get_user.assert_called_once_with(mock_session, email="new@example.com")
    mock_create_user.assert_called_once_with(mock_session, user_in)

@patch("backend.app.services.user_services.user_crud.get_user_by_email")
def test_register_user_already_exists(mock_get_user, mock_session):
    # Arrange
    user_in = UserCreate(name="Test", email="existing@example.com", password="password")
    mock_existing_user = MagicMock()
    mock_get_user.return_value = mock_existing_user  # user exists

    # Act & Assert
    with pytest.raises(EmailAlreadyRegisteredError) as exc_info:
        register_user(session=mock_session, user_create=user_in)

    assert str(exc_info.value) == "Email already registered"
    mock_get_user.assert_called_once_with(mock_session, email="existing@example.com")


def test_register_user_invalid_email(mock_session):
    # Arrange: Email missing '@'
    user_in = UserCreate(name="Test User", email="bademail.com", password="password")
    
    # Act & Assert
    with pytest.raises(InvalidUserDataError) as exc_info:
        register_user(session=mock_session, user_create=user_in)
        
    assert str(exc_info.value) == "Invalid email format"


def test_register_user_empty_name(mock_session):
    # Arrange: Name is only whitespace
    user_in = UserCreate(name="   ", email="good@example.com", password="password")
    
    # Act & Assert
    with pytest.raises(InvalidUserDataError) as exc_info:
        register_user(session=mock_session, user_create=user_in)
        
    assert str(exc_info.value) == "Name can't be empty"

