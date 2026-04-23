import os
import pytest
from unittest.mock import MagicMock, patch
from sqlmodel import Session

from backend.app.services.user_services import (
    login_user,
    register_user,
    get_user_presets_instruments_path,
    get_user_presets_pieces_path,
    get_user_dossier_cover_path,
)
from backend.app.models.token import Token
from backend.app.models.user import UserCreate
from backend.app.models.user_config import UserConfigCreate
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
@patch("backend.app.services.user_services.create_user_config")
@patch("backend.app.services.user_services.rol_crud.get_role")
def test_register_user_success(
    mock_get_role,
    mock_create_user_config,
    mock_create_user,
    mock_get_user,
    mock_session,
):
    # Arrange
    user_in = UserCreate(name="Test", email="new@example.com", password="password")
    mock_get_user.return_value = None  # user doesn't exist yet
    mock_get_role.return_value = MagicMock()
    
    mock_created_user = MagicMock()
    mock_created_user.id = 42
    mock_create_user.return_value = mock_created_user

    # Act
    result = register_user(session=mock_session, user_create=user_in)

    # Assert
    assert result == mock_created_user
    mock_get_user.assert_called_once_with(mock_session, email="new@example.com")
    mock_create_user.assert_called_once_with(mock_session, user_in)
    mock_create_user_config.assert_called_once()

    create_args, _ = mock_create_user_config.call_args
    assert create_args[0] == mock_session
    assert create_args[1] == UserConfigCreate(
        language="en_US",
        user_id=42,
    )

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


@patch("backend.app.services.user_services.user_crud.get_user_by_email")
def test_register_user_default_role_not_found(mock_get_user, mock_session):
    # Arrange
    user_in = UserCreate(name="Test", email="test@example.com", password="password", role_id=0)
    mock_get_user.return_value = None  # User doesn't exist
    
    mock_exec = MagicMock()
    mock_exec.first.return_value = None  # Role not found
    mock_session.exec.return_value = mock_exec

    # Act & Assert
    with pytest.raises(InvalidUserDataError) as exc_info:
        register_user(session=mock_session, user_create=user_in)

    assert str(exc_info.value) == "Default role 'user' not found in the database"


@patch("backend.app.services.user_services.user_crud.get_user_by_email")
@patch("backend.app.services.user_services.rol_crud.get_role")
def test_register_user_provided_role_not_found(mock_get_role, mock_get_user, mock_session):
    # Arrange
    user_in = UserCreate(name="Test", email="test@example.com", password="password", role_id=99)
    mock_get_user.return_value = None  # User doesn't exist
    mock_get_role.return_value = None

    # Act & Assert
    with pytest.raises(InvalidUserDataError) as exc_info:
        register_user(session=mock_session, user_create=user_in)

    assert str(exc_info.value) == "Provided role_id does not exist"
    mock_get_role.assert_called_once_with(mock_session, 99)

@patch("backend.app.services.user_services.user_crud.get_user_by_email")
@patch("backend.app.services.user_services.user_crud.create_user")
@patch("backend.app.services.user_services.create_user_config")
@patch("backend.app.services.user_services.rol_crud.get_role")
def test_register_user_default_role_assigned(
    mock_get_role, mock_create_user_config, mock_create_user, mock_get_user, mock_session
):
    # Arrange
    user_in = UserCreate(name="Test", email="test@example.com", password="password", role_id=None)
    mock_get_user.return_value = None  # User doesn't exist
    
    # Mocking the database role query
    mock_role = MagicMock()
    mock_role.id = 5
    mock_exec = MagicMock()
    mock_exec.first.return_value = mock_role
    mock_session.exec.return_value = mock_exec

    mock_get_role.return_value = mock_role

    mock_created_user = MagicMock()
    mock_created_user.id = 1
    mock_create_user.return_value = mock_created_user

    # Act
    register_user(session=mock_session, user_create=user_in)

    # Assert
    assert user_in.role_id == 5
    mock_get_role.assert_called_once_with(mock_session, 5)
    mock_create_user.assert_called_once_with(mock_session, user_in)


@pytest.mark.parametrize(
    "service_fn,base_attr,user_attr",
    [
        (
            get_user_presets_instruments_path,
            "base_presets_instruments_path",
            "presets_instruments_path",
        ),
        (
            get_user_presets_pieces_path,
            "base_presets_pieces_path",
            "presets_pieces_path",
        ),
        (
            get_user_dossier_cover_path,
            "base_dossier_cover_path",
            "dossier_cover_path",
        ),
    ],
)
def test_get_user_paths_success(service_fn, base_attr, user_attr, mock_session):
    user_id = 7
    user_relative_path = "user/custom/path"
    base_path = "base/root"

    mock_user_config = MagicMock()
    setattr(mock_user_config, user_attr, user_relative_path)

    mock_settings = MagicMock()
    setattr(mock_settings, base_attr, base_path)

    with patch(
        "backend.app.services.user_services.get_user_config_by_user_id"
    ) as mock_get_user_config, patch(
        "backend.app.services.user_services.get_server_settings"
    ) as mock_get_settings:
        mock_get_user_config.return_value = mock_user_config
        mock_get_settings.return_value = mock_settings

        result = service_fn(session=mock_session, user_id=user_id)

        assert result == os.path.join(base_path, user_relative_path)
        mock_get_user_config.assert_called_once_with(mock_session, user_id=user_id)
        mock_get_settings.assert_called_once_with()


@pytest.mark.parametrize(
    "service_fn",
    [
        get_user_presets_instruments_path,
        get_user_presets_pieces_path,
        get_user_dossier_cover_path,
    ],
)
def test_get_user_paths_user_config_not_found_raises(service_fn, mock_session):
    user_id = 99

    with patch(
        "backend.app.services.user_services.get_user_config_by_user_id"
    ) as mock_get_user_config:
        mock_get_user_config.return_value = None

        with pytest.raises(InvalidUserDataError) as exc_info:
            service_fn(session=mock_session, user_id=user_id)

        assert str(exc_info.value) == "User config not found"
        mock_get_user_config.assert_called_once_with(mock_session, user_id=user_id)

@patch("backend.app.services.user_services.user_crud.get_all_users")
def test_get_all_users(mock_crud_get_all, mock_session):
    # Arrange
    from backend.app.services.user_services import get_all_users
    mock_users = [MagicMock(), MagicMock()]
    mock_crud_get_all.return_value = mock_users

    # Act
    result = get_all_users(mock_session)

    # Assert
    assert result == mock_users
    mock_crud_get_all.assert_called_once_with(mock_session)


