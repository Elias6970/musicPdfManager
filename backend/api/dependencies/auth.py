# backend/api/dependencies/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session
from backend.app.models.user import User
from backend.api.dependencies.database import get_session
from backend.app.security.auth import decode_access_token
# Import your token decoding logic here


def get_current_user(
    token: str = Depends(decode_access_token), 
    session: Session = Depends(get_session)
) -> User:
    
    user = session.get(User, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user