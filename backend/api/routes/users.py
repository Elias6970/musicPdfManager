from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from backend.api.dependencies.database import get_session
from backend.api.dependencies.permissions import RequireRoleFastAPI,require_admin
from backend.app.models.user import User, UserCreate, UserPublic
from backend.app.models.token import Token
from backend.app.services.user_services import register_user, login_user
from backend.app.error import EmailAlreadyRegisteredError, InvalidCredentialsError, InvalidUserDataError

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/register", response_model=UserPublic)
def register(user_in: UserCreate, session: Session = Depends(get_session), creator: User = Depends(require_admin)):
    try:
        user = register_user(session, user_create=user_in)
        return user
    except EmailAlreadyRegisteredError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except InvalidUserDataError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    try:
        token = login_user(session, email=form_data.username, password=form_data.password)
        return token
    except InvalidCredentialsError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

