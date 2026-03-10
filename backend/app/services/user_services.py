from sqlmodel import Session
from backend.app.crud import user_crud
from backend.app.models.user import UserCreate, UserPublic
from backend.app.models.token import Token
from backend.app.utils.auth import verify_password, create_access_token
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
