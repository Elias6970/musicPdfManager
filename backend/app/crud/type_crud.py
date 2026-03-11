from sqlmodel import Session, select
from backend.app.models.type import Type

def get_or_create_type(session: Session, type_name: str) -> Type:
    # Try to find the existing type by name
    statement = select(Type).where(Type.name == type_name)
    existing_type = session.exec(statement).first()
    
    if existing_type:
        return existing_type
    
    new_type = Type(name=type_name)
    session.add(new_type)
    session.commit()
    session.refresh(new_type)
    
    return new_type

def get_type_by_id(session: Session, type_id: int) -> Type | None:
    return session.get(Type, type_id)

def get_type_by_name(session: Session, type_name: str) -> Type | None:
    statement = select(Type).where(Type.name == type_name)
    return session.exec(statement).first()

def delete_type(session: Session, type_id: int) -> bool:
    db_type = session.get(Type, type_id)
    if not db_type:
        return False
    session.delete(db_type)
    session.commit()
    return True