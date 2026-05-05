from sqlmodel import Session
from backend.app.models.role import Role, RoleCreate
import backend.app.crud.rol_crud as rol_crud
from backend.app.error import RoleNameAlreadyExistsError, RoleNotFoundError

def create_role(session: Session, role: RoleCreate) -> Role:
    existing_role = rol_crud.get_role_by_name(session, role.name)
    if existing_role:
        raise RoleNameAlreadyExistsError()
    return rol_crud.create_role(session, role)

def get_role(session: Session, role_id: int) -> Role:
    role = rol_crud.get_role(session, role_id)
    if not role:
        raise RoleNotFoundError()
    return role

def get_all_roles(session: Session) -> list[Role]:
    return rol_crud.get_all_roles(session)

def update_role(session: Session, role_id: int, role_in: RoleCreate) -> Role:
    db_role = get_role(session, role_id)
    if not db_role:
        raise RoleNotFoundError()

    existing_role = rol_crud.get_role_by_name(session, role_in.name)
    if existing_role and existing_role.id != db_role.id:
        raise RoleNameAlreadyExistsError()
            
    return rol_crud.update_role(session, role_id, role_in)

def delete_role(session: Session, role_id: int) -> None:
    db_role = get_role(session, role_id)
    rol_crud.delete_role(session, db_role)
