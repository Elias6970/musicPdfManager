import json
import os
from typing import Optional

from backend.app.models.presets.pieces_preset import PiecesPreset

def save_pieces_preset(path: str, preset: PiecesPreset) -> None:
    """Save or update a pieces preset. If there is a preset with the same name it will be overwritten."""
    data = {}
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                data = {}

    data[preset.name] = preset.model_dump()

    with open(path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)

def get_pieces_preset(path: str, preset_name: str) -> Optional[PiecesPreset]:
    """Get a pieces preset using the name. Returns None if it doesn't exist."""
    if not os.path.exists(path):
        return None

    with open(path, 'r', encoding='utf-8') as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError:
            return None

    if preset_name not in data:
        return None

    return PiecesPreset(**data[preset_name])

def get_all_pieces_presets(path: str) -> list[PiecesPreset]:
    """Get all pieces presets in the file. Returns an empty list if file doesn't exist or is empty."""
    if not os.path.exists(path):
        return []
        
    with open(path, 'r', encoding='utf-8') as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError:
            return []
            
    return [PiecesPreset(**preset_data) for name, preset_data in data.items()]

def get_all_pieces_presets_names(path: str) -> list[str]:
    """Get all piece preset names in the file. Returns an empty list if file doesn't exist or is empty."""
    if not os.path.exists(path):
        return []
        
    with open(path, 'r', encoding='utf-8') as file:
        try:
            data = json.load(file)
            return list(data.keys())
        except json.JSONDecodeError:
            return []

def delete_pieces_preset(path: str, preset_name: str) -> bool:
    """Delete a pieces preset by name. Returns True if successfully deleted, False otherwise."""
    if not os.path.exists(path):
        return False

    with open(path, 'r', encoding='utf-8') as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError:
            return False

    if preset_name in data:
        del data[preset_name]
        with open(path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4)
        return True

    return False
