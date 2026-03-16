from sqlmodel import Session
from typing import List
from backend.app.models.user_archive_link import UserArchiveLink, ArchiveRole
from backend.app.error import InsufficientPermissionsError, InvalidUserDataError
from backend.app.models.user import User
from backend.app.services.archive_services import check_archive_role
from backend.app.services.user_services import check_user_role
from backend.api.dependencies.database import get_session
from backend.api.dependencies.auth import get_current_user
from fastapi import Depends, HTTPException, status

class RequireRoleFastAPI:
    """
    FastAPI Dependency that wraps the `check_role` business logic.
    This gives you the clean `Depends(...)` syntax in your API routes while
    keeping the core logic isolated.
    """

    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(
        self, 
        session: Session = Depends(get_session), 
        current_user: User = Depends(get_current_user)
    ) -> User:
        try:
            print("Checking user role for user_id:", current_user.id)
            return check_user_role(
                session=session,
                user_id=current_user.id,
                allowed_roles=self.allowed_roles
            )
        except (InsufficientPermissionsError,InvalidUserDataError) as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e)
            )
        

class RequireArchiveRoleFastAPI:
    """
    FastAPI Dependency that wraps the `check_archive_role` business logic.
    This gives you the clean `Depends(...)` syntax in your API routes while
    keeping the core logic isolated.
    """

    def __init__(self, allowed_roles: List[ArchiveRole]):
        self.allowed_roles = allowed_roles

    def __call__(
        self, 
        archive_id: int, 
        session: Session = Depends(get_session), 
        current_user: User = Depends(get_current_user)
    ) -> UserArchiveLink:
        try:
            return check_archive_role(
                session=session,
                user_id=current_user.id,
                archive_id=archive_id,
                allowed_roles=self.allowed_roles
            )
        except InsufficientPermissionsError as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e)
            )