from sqlmodel import Session
from uuid import uuid4

from backend.app.crud import user_config_crud
from backend.app.models.user_config import UserConfig, UserConfigCreate


def create_user_config(session: Session, user_config_in: UserConfigCreate) -> UserConfig:
    """Service to create config and auto-generate system paths for a user."""
    
    # Construct the final UserConfig object that the CRUD expects
    db_obj = UserConfig(**user_config_in.model_dump(),
                        presets_instruments_path=f"{uuid4()}.json",
                        presets_pieces_path=f"{uuid4()}.json",
                        catalog_cover_path="",
            )
    
    # Delegate to CRUD layer
    return user_config_crud.create_user_config(
        session=session, 
        user_config_in=db_obj
    )

def get_user_config(session: Session, user_config_id: int) -> UserConfig | None:
    return user_config_crud.get_user_config(session, user_config_id)

def get_user_config_by_user_id(session: Session, user_id: int) -> UserConfig | None:
    return user_config_crud.get_user_config_by_user_id(session, user_id)

def update_user_config(session: Session, user_config_id: int, user_config_in: UserConfigCreate) -> UserConfig | None:
    """Service to update config. Paths are immutable unless explicitly regenerated here."""
    db_obj = user_config_crud.get_user_config(session, user_config_id)
    if not db_obj:
        return None
        
    update_data = user_config_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_obj, key, value)
        
    return user_config_crud.update_user_config(session, user_config_in=db_obj)

def delete_user_config(session: Session, user_config_id: int) -> bool:
    return user_config_crud.delete_user_config(session, user_config_id)
