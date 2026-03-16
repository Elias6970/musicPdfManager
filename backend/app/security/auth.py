# backend/app/utils/security.py
from datetime import datetime, timedelta, timezone
from pwdlib import PasswordHash
import jwt
import backend.app.settings as settings

pwd_context = PasswordHash.recommended()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(subject: str | int, expires_delta: timedelta | None = None) -> str:
    """Creates a JWT access token for the given subject (user ID or email). Subject is usually the user ID."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.get_server_settings().access_token_expire_minutes)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(payload=to_encode, 
                             key=settings.get_server_settings().jwt_secret_key, 
                             algorithm=settings.get_server_settings().jwt_algorithm)
    return encoded_jwt

def decode_access_token(token: str) -> str | None:
    """Decodes a JWT access token and returns the payload if valid."""
    try:
        decoded_jwt = jwt.decode(
            token, 
            key=settings.get_server_settings().jwt_secret_key, 
            algorithms=[settings.get_server_settings().jwt_algorithm]
        )
        return decoded_jwt["sub"] if "sub" in decoded_jwt else None
    except jwt.InvalidTokenError:
        return None