from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from backend.api.dependencies.database import get_session
from backend.api.dependencies.permissions import RequireRoleFastAPI,require_admin
from backend.api.dependencies.auth import get_current_user
from backend.app.models.user import User, UserCreate, UserPublic
from backend.app.models.user_config import UserConfigCreate, UserConfigCreatePublic, UserConfigPublic
from backend.app.models.token import Token
from backend.app.services.user_services import (
    register_user, 
    login_user, 
    get_all_users as _get_all_users, 
    update_user as _update_user, 
    delete_user as _delete_user,
    is_admin as _is_admin,
)
from backend.app.services.user_config_services import (
    get_user_config_by_user_id,
    update_user_config as _update_user_config
)

from backend.app.error import EmailAlreadyRegisteredError, InvalidCredentialsError, InvalidUserDataError

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/register", response_model=UserPublic)
def register(user_in: UserCreate, session: Session = Depends(get_session), creator: User = Depends(require_admin)) -> UserPublic:
    try:
        user = register_user(session, user_create=user_in)
        return UserPublic.model_validate(user)
    
    except EmailAlreadyRegisteredError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except InvalidUserDataError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)) -> Token:
    try:
        token = login_user(session, email=form_data.username, password=form_data.password)
        return token
    except InvalidCredentialsError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

@router.put("/{user_id}", response_model=UserPublic)
def update_user(
    user_id: int,
    user_update: UserCreate,
    session: Session = Depends(get_session),
    _: User = Depends(require_admin)
):
    try:
        updated_user = _update_user(session, user_id=user_id, user_update=user_update)
        if not updated_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return UserPublic.model_validate(updated_user)
    except InvalidUserDataError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    session: Session = Depends(get_session),
    _: User = Depends(require_admin)
):
    result = _delete_user(session, user_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return

@router.get("/", response_model=list[UserPublic])
def get_all_users(
    session: Session = Depends(get_session),
    _: User = Depends(require_admin)
) -> list[UserPublic]:
    users = _get_all_users(session)
    return [UserPublic.model_validate(user) for user in users]

@router.get("/config", response_model=UserConfigPublic)
def get_user_config(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
    ) -> UserConfigPublic:
    user_config = get_user_config_by_user_id(session, current_user.id) #type: ignore
    is_admin = _is_admin(session, current_user)
    
    if not user_config:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User config not found")
    return UserConfigPublic.model_validate(user_config, update={"is_admin": is_admin})

@router.put("/config", response_model=UserConfigPublic)
def update_user_config(
    user_config_in: UserConfigCreatePublic,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
) -> UserConfigPublic:
    user_config = get_user_config_by_user_id(session, current_user.id) #type: ignore
    if not user_config or not user_config.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User config not found")
    
    # Only allow updating the config for the current user
    if user_config.user_id != current_user.id or not current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot update another user's config")
    
    in_config = UserConfigCreate(**user_config_in.model_dump(), user_id=current_user.id)
    updated_config = _update_user_config(session, user_config_id=user_config.id, user_config_in=in_config)
    if not updated_config:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User config not found during update")
    
    return UserConfigPublic.model_validate(updated_config, update={"is_admin": _is_admin(session, current_user)})
