from sqlmodel import Session, select
from backend.app.models.user import User, UserCreate
from backend.app.security.auth import get_password_hash

def create_user(session: Session, user_create: UserCreate) -> User:
    db_obj = User.model_validate(
        user_create, update={"password_hash": get_password_hash(user_create.password)}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj

def get_user_by_id(session: Session, user_id: int) -> User | None:
    return session.get(User, user_id)

def get_user_by_email(session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()

def get_all_users(session: Session) -> list[User]:
    statement = select(User)
    return session.exec(statement).all()

def delete_user(session: Session, user_id: int) -> bool:
    user = session.get(User, user_id)
    if not user:
        return False
    session.delete(user)
    session.commit()
    return True