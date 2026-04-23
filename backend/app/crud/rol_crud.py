from sqlmodel import Session, select
from backend.app.error import RoleNotFoundError
from backend.app.error import RoleNotFoundError
from backend.app.models.role import Role, RoleCreate

def create_role(session: Session, role: RoleCreate) -> Role:
    db_role = Role.model_validate(role)
    session.add(db_role)
    session.commit()
    session.refresh(db_role)
    return db_role

def get_role(session: Session, role_id: int) -> Role | None:
    return session.get(Role, role_id)

def get_role_by_name(session: Session, name: str) -> Role | None:
    statement = select(Role).where(Role.name == name)
    return session.exec(statement).first()

def get_all_roles(session: Session) -> list[Role]:
    return list(session.exec(select(Role)).all())

def update_role(session: Session, role_id: int, role_in: Role) -> Role:
    db_role = get_role(session, role_id)
    if not db_role:
        raise RoleNotFoundError()
    
    db_role.name = role_in.name
    session.add(db_role)
    session.commit()
    session.refresh(db_role)
    return db_role

def delete_role(session: Session, db_role: Role) -> None:
    session.delete(db_role)
    session.commit()
