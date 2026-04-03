import os
from sqlmodel import Session, select

from backend.app.models.presets.pieces_preset import PiecesPreset
from backend.app.models.user_config import UserConfig
from backend.app.settings import get_server_settings
from backend.app.crud import pieces_preset_crud
from backend.app.error import UserConfigNotFoundError, PresetNotFoundError, PresetAlreadyExistsError

def _get_user_preset_file_path(session: Session, user_id: int) -> str:
    """Helper to determine the physical file path for a user's pieces presets."""
    user_config = session.exec(select(UserConfig).where(UserConfig.user_id == user_id)).first()
    if not user_config:
        raise UserConfigNotFoundError("User configuration not found")

    settings = get_server_settings()
    
    # Combine the base directory from settings with the user's specific filename/path
    base_path = settings.base_presets_pieces_path
    filepath = os.path.join(base_path, user_config.presets_pieces_path)
    
    # Ensure the directory exists before we try to read/write from it
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    return filepath

def get_preset(session: Session, user_id: int, preset_name: str) -> PiecesPreset:
    """Retrieve a piece preset by name for a specific user."""
    filepath = _get_user_preset_file_path(session, user_id)
    preset = pieces_preset_crud.get_pieces_preset(filepath, preset_name)
    
    if not preset:
        raise PresetNotFoundError(f"Preset '{preset_name}' not found")
        
    return preset

def get_all_presets(session: Session, user_id: int) -> list[PiecesPreset]:
    """Retrieve all piece presets for a specific user."""
    filepath = _get_user_preset_file_path(session, user_id)
    return pieces_preset_crud.get_all_pieces_presets(filepath)

def get_all_preset_names(session: Session, user_id: int) -> list[str]:
    """Retrieve all piece preset names for a specific user."""
    filepath = _get_user_preset_file_path(session, user_id)
    return pieces_preset_crud.get_all_pieces_presets_names(filepath)

def add_preset(session: Session, user_id: int, preset: PiecesPreset) -> PiecesPreset:
    """Add a new piece preset. Fails if the preset already exists."""
    filepath = _get_user_preset_file_path(session, user_id)
    
    # Check if a preset with the same name already exists
    existing_preset = pieces_preset_crud.get_pieces_preset(filepath, preset.name)
    if existing_preset:
        raise PresetAlreadyExistsError(f"Preset '{preset.name}' already exists")
        
    pieces_preset_crud.save_pieces_preset(filepath, preset)
    return preset

def update_preset(session: Session, user_id: int, preset: PiecesPreset) -> PiecesPreset:
    """Update an existing piece preset. Fails if the preset doesn't exist."""
    filepath = _get_user_preset_file_path(session, user_id)
    
    # Check if it actually exists before updating
    existing_preset = pieces_preset_crud.get_pieces_preset(filepath, preset.name)
    if not existing_preset:
        raise PresetNotFoundError(f"Preset '{preset.name}' not found")
        
    pieces_preset_crud.save_pieces_preset(filepath, preset)
    return preset

def delete_preset(session: Session, user_id: int, preset_name: str) -> None:
    """Delete a piece preset. Fails if it doesn't exist."""
    filepath = _get_user_preset_file_path(session, user_id)
    
    success = pieces_preset_crud.delete_pieces_preset(filepath, preset_name)
    if not success:
        raise PresetNotFoundError(f"Preset '{preset_name}' not found")
