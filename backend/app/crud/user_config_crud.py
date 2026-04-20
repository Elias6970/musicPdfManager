from sqlmodel import Session, select
from backend.app.models.user_config import UserConfig


def create_user_config(session: Session, user_config_in: UserConfig) -> UserConfig:
    session.add(user_config_in)
    session.commit()
    session.refresh(user_config_in)
    return user_config_in


def get_user_config(session: Session, user_config_id: int) -> UserConfig | None:
    return session.get(UserConfig, user_config_id)


def get_user_config_by_user_id(session: Session, user_id: int) -> UserConfig | None:
    statement = select(UserConfig).where(UserConfig.user_id == user_id)
    return session.exec(statement).first()


def update_user_config(session: Session, user_config_in: UserConfig) -> UserConfig:
    session.add(user_config_in)
    session.commit()
    session.refresh(user_config_in)
    return user_config_in


def delete_user_config(session: Session, user_config_id: int) -> bool:
    db_obj = session.get(UserConfig, user_config_id)
    if not db_obj:
        return False
    session.delete(db_obj)
    session.commit()
    return True

