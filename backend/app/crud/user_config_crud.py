from sqlmodel import Session, select
from backend.app.models.user_config import UserConfig, UserConfigCreate


def create_user_config(session: Session, user_config_in: UserConfigCreate) -> UserConfig:
    db_obj = UserConfig.model_validate(user_config_in)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_user_config(session: Session, user_config_id: int) -> UserConfig | None:
    return session.get(UserConfig, user_config_id)


def get_user_config_by_user_id(session: Session, user_id: int) -> UserConfig | None:
    statement = select(UserConfig).where(UserConfig.user_id == user_id)
    return session.exec(statement).first()


def update_user_config(session: Session, user_config_id: int, user_config_in: UserConfigCreate) -> UserConfig | None:
    db_obj = session.get(UserConfig, user_config_id)
    if not db_obj:
        return None
    config_data = user_config_in.model_dump(exclude_unset=True)
    for key, value in config_data.items():
        setattr(db_obj, key, value)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def delete_user_config(session: Session, user_config_id: int) -> bool:
    db_obj = session.get(UserConfig, user_config_id)
    if not db_obj:
        return False
    session.delete(db_obj)
    session.commit()
    return True
