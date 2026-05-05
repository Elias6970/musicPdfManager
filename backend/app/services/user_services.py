import os
from uuid import uuid4
from sqlmodel import Session, select
from backend.app.crud import user_crud
from backend.app.crud import rol_crud
from backend.app.services.user_config_services import create_user_config, get_user_config_by_user_id
from backend.app.models.role import Role
from backend.app.models.user import UserCreate, User
from backend.app.models.user_config import UserConfigCreate
from backend.app.models.token import Token
from backend.app.security.auth import verify_password, create_access_token
from backend.app.utils.settings import get_server_settings
from backend.app.error import EmailAlreadyRegisteredError, InsufficientPermissionsError, InvalidCredentialsError, InvalidUserDataError


def register_user(session: Session, user_create: UserCreate) -> User:
    if "@" not in user_create.email:
        raise InvalidUserDataError("Invalid email format")
    
    if not user_create.name.strip():
        raise InvalidUserDataError("Name can't be empty")

    # Check if user already exists
    existing_user = user_crud.get_user_by_email(session, email=user_create.email)
    if existing_user:
        raise EmailAlreadyRegisteredError("Email already registered")
    
    # Set the default role
    if user_create.role_id is None or user_create.role_id == 0:
        role = session.exec(select(Role).where(Role.name == "user")).first()  # Ensure "user" role exists
        if not role:
            raise InvalidUserDataError("Default role 'user' not found in the database")
        user_create.role_id = role.id
    
    # Check if the role_id provided is valid
    role = rol_crud.get_role(session, user_create.role_id)
    if not role:
        raise InvalidUserDataError("Provided role_id does not exist")

    # Create the user
    user = user_crud.create_user(session, user_create)
    create_user_config(
        session,
        UserConfigCreate(
            language="en_US",
            user_id=user.id, #type: ignore
        ),
    )
    return user

def login_user(session: Session, email: str, password: str) -> Token:
    user = user_crud.get_user_by_email(session, email=email)
    if not user:
        raise InvalidCredentialsError("Email does not exist")
    
    if not verify_password(plain_password=password, hashed_password=user.password_hash):
        raise InvalidCredentialsError("Incorrect password")
    
    access_token = create_access_token(subject=user.id) #type: ignore
    return Token(access_token=access_token, token_type="bearer")

def update_user(session: Session, user_id: int, user_update: UserCreate) -> User | None:
    if user_update.email is not None and "@" not in user_update.email:
        raise InvalidUserDataError("Invalid email format")
    
    if user_update.name is not None and not user_update.name.strip():
        raise InvalidUserDataError("Name can't be empty")

    # Check if the role_id provided is valid
    if user_update.role_id is not None:
        role = rol_crud.get_role(session, user_update.role_id)
        if not role:
            raise InvalidUserDataError("Provided role_id does not exist")  

    return user_crud.update_user(session, user_id=user_id, user_update=user_update)

def delete_user(session: Session, user_id: int) -> bool:
    return user_crud.delete_user(session, user_id=user_id)

def get_user_presets_instruments_path(session: Session, user_id: int) -> str:
    user_config = get_user_config_by_user_id(session, user_id=user_id)
    if not user_config:
        raise InvalidUserDataError("User config not found")

    settings = get_server_settings()
    return os.path.join(settings.base_presets_instruments_path, user_config.presets_instruments_path)


def get_user_presets_pieces_path(session: Session, user_id: int) -> str:
    user_config = get_user_config_by_user_id(session, user_id=user_id)
    if not user_config:
        raise InvalidUserDataError("User config not found")

    settings = get_server_settings()
    return os.path.join(settings.base_presets_pieces_path, user_config.presets_pieces_path)


def get_user_dossier_cover_path(session: Session, user_id: int) -> str:
    user_config = get_user_config_by_user_id(session, user_id=user_id)
    if not user_config:
        raise InvalidUserDataError("User config not found")

    settings = get_server_settings()
    return os.path.join(settings.base_dossier_cover_path, user_config.dossier_cover_path)


def check_user_role(session: Session, user_id: int, allowed_roles: list[str]) -> User:
    user = user_crud.get_user_by_id(session, user_id=user_id)
    if not user:
        raise InvalidUserDataError("User not found")
    
    if user.role is None or user.role.name not in allowed_roles:
        raise InsufficientPermissionsError("User does not have the required role")
    
    return user


def get_all_users(session: Session) -> list[User]:
    return user_crud.get_all_users(session)