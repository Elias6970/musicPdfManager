from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from backend.api.dependencies.database import get_session
from backend.api.dependencies.permissions import RequireRoleFastAPI,require_user,require_admin
from backend.api.dependencies.auth import get_current_user
from backend.app.models.role import RoleCreate, RolePublic

from backend.app.services.rol_services import create_role, get_role, get_all_roles, update_role, delete_role


router = APIRouter(prefix="/roles", tags=["roles"])


@router.get("/", response_model=list[RolePublic])
def get_roles(
    session: Session = Depends(get_session),
    _: None = Depends(require_user)
):
    return get_all_roles(session)

@router.get("/{role_id}", response_model=RolePublic)
def get_role(
    role_id: int,
    session: Session = Depends(get_session),
    _: None = Depends(require_user)
):
    return get_role(session, role_id)

@router.post("/", response_model=RolePublic, status_code=status.HTTP_201_CREATED)
def create_new_role(
    role: RoleCreate,
    session: Session = Depends(get_session),
    _: None = Depends(require_admin)
):
    return create_role(session, role)