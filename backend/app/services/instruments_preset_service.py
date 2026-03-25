import os
from sqlmodel import Session, select

from backend.app.models.presets.instruments_preset import InstrumentsPreset
from backend.app.models.user_config import UserConfig
from backend.app.settings import get_server_settings
from backend.app.crud import instruments_preset_crud
from backend.app.error import UserConfigNotFoundError, PresetNotFoundError, PresetAlreadyExistsError

def _get_user_preset_file_path(session: Session, user_id: int) -> str:
    """Helper to determine the physical file path for a user's instruments presets."""
    user_config = session.exec(select(UserConfig).where(UserConfig.user_id == user_id)).first()
    if not user_config:
        raise UserConfigNotFoundError("User configuration not found")

    settings = get_server_settings()
    
    # Combine the base directory from settings with the user's specific filename/path
    base_path = settings.base_presets_instruments_path
    filepath = os.path.join(base_path, user_config.presets_instruments_path)
    
    # Ensure the directory exists before we try to read/write from it
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    return filepath

def get_preset(session: Session, user_id: int, preset_name: str) -> InstrumentsPreset:
    """Retrieve an instrument preset by name for a specific user."""
    filepath = _get_user_preset_file_path(session, user_id)
    preset = instruments_preset_crud.get_instruments_preset(filepath, preset_name)
    
    if not preset:
        raise PresetNotFoundError(f"Preset '{preset_name}' not found")
        
    return preset

def add_preset(session: Session, user_id: int, preset: InstrumentsPreset) -> InstrumentsPreset:
    """Add a new instrument preset. Fails if the preset already exists."""
    filepath = _get_user_preset_file_path(session, user_id)
    
    # Check if a preset with the same name already exists
    existing_preset = instruments_preset_crud.get_instruments_preset(filepath, preset.name)
    if existing_preset:
        raise PresetAlreadyExistsError(f"Preset '{preset.name}' already exists")
        
    instruments_preset_crud.save_instruments_preset(filepath, preset)
    return preset

def update_preset(session: Session, user_id: int, preset: InstrumentsPreset) -> InstrumentsPreset:
    """Update an existing instrument preset. Fails if the preset doesn't exist."""
    filepath = _get_user_preset_file_path(session, user_id)
    
    # Check if it actually exists before updating
    existing_preset = instruments_preset_crud.get_instruments_preset(filepath, preset.name)
    if not existing_preset:
        raise PresetNotFoundError(f"Preset '{preset.name}' not found")
        
    instruments_preset_crud.save_instruments_preset(filepath, preset)
    return preset

def delete_preset(session: Session, user_id: int, preset_name: str) -> None:
    """Delete an instrument preset. Fails if it doesn't exist."""
    filepath = _get_user_preset_file_path(session, user_id)
    
    success = instruments_preset_crud.delete_instruments_preset(filepath, preset_name)
    if not success:
        raise PresetNotFoundError(f"Preset '{preset_name}' not found")

