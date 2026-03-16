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
    # 1. Decode token
    # 2. Get user_id from token
    # 3. Query the user from the DB using the session
    # 4. If invalid or user not found, raise HTTPException(status_code=401)
    
    user = session.get(User, int(token))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user