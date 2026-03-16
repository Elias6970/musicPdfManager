import os
from sqlmodel import Session
from backend.app.crud import user_crud, user_config_crud
from backend.app.models.user import UserCreate, UserPublic
from backend.app.models.token import Token
from backend.app.security.auth import verify_password, create_access_token
from backend.app.settings import get_server_settings
from backend.app.error import EmailAlreadyRegisteredError, InvalidCredentialsError, InvalidUserDataError

def register_user(session: Session, user_create: UserCreate) -> UserPublic:
    if "@" not in user_create.email:
        raise InvalidUserDataError("Invalid email format")
    
    if not user_create.name.strip():
        raise InvalidUserDataError("Name can't be empty")

    # Check if user already exists
    existing_user = user_crud.get_user_by_email(session, email=user_create.email)
    if existing_user:
        raise EmailAlreadyRegisteredError("Email already registered")
    
    # Create the user
    user = user_crud.create_user(session, user_create)
    return user

def login_user(session: Session, email: str, password: str) -> Token:
    user = user_crud.get_user_by_email(session, email=email)
    if not user:
        raise InvalidCredentialsError("Email does not exist")
    
    if not verify_password(plain_password=password, hashed_password=user.password_hash):
        raise InvalidCredentialsError("Incorrect password")
    
    access_token = create_access_token(subject=user.id)
    return Token(access_token=access_token, token_type="bearer")


def get_user_presets_instruments_path(session: Session, user_id: int) -> str:
    user_config = user_config_crud.get_user_config_by_user_id(session, user_id=user_id)
    if not user_config:
        raise InvalidUserDataError("User config not found")

    settings = get_server_settings()
    return os.path.join(settings.base_presets_instruments_path, user_config.presets_instruments_path)


def get_user_presets_pieces_path(session: Session, user_id: int) -> str:
    user_config = user_config_crud.get_user_config_by_user_id(session, user_id=user_id)
    if not user_config:
        raise InvalidUserDataError("User config not found")

    settings = get_server_settings()
    return os.path.join(settings.base_presets_pieces_path, user_config.presets_pieces_path)


def get_user_dossier_cover_path(session: Session, user_id: int) -> str:
    user_config = user_config_crud.get_user_config_by_user_id(session, user_id=user_id)
    if not user_config:
        raise InvalidUserDataError("User config not found")

    settings = get_server_settings()
    return os.path.join(settings.base_dossier_cover_path, user_config.dossier_cover_path)


