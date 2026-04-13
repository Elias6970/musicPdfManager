# backend/api/dependencies/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session
from backend.app.models.user import User
from backend.api.dependencies.database import get_session
from backend.app.security.auth import decode_access_token
# Import your token decoding logic here


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/users/login")

def get_current_user(
    token: str = Depends(oauth2_scheme), 
    session: Session = Depends(get_session)
) -> User:
    
    # 1. Decode the token to get the subject (user id)
    user_id_str = decode_access_token(token)
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # 2. Fetch user from DB
    user = session.get(User, int(user_id_str))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user