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

def update_user(session: Session, user_id: int, user_update: UserCreate) -> User | None:
    """
    Update the user_id with the user_update data.
    The password is only updated if it is not None and not empty
    """
    user = session.get(User, user_id)
    if not user:
        return None
    
    # Update fields if provided
    if user_update.email is not None:
        user.email = user_update.email
    if user_update.name is not None:
        user.name = user_update.name
    if user_update.role_id is not None:
        user.role_id = user_update.role_id
    if user_update.password is not None and user_update.password != "":
        user.password_hash = get_password_hash(user_update.password)

    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def delete_user(session: Session, user_id: int) -> bool:
    user = session.get(User, user_id)
    if not user:
        return False
    session.delete(user)
    session.commit()
    return True