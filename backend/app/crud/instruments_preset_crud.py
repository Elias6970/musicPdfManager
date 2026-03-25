import json
import os
from typing import Optional

from backend.app.models.presets.instruments_preset import InstrumentsPreset

def save_instruments_preset(path: str, preset: InstrumentsPreset) -> None:
    """Save or update a preset. If there is a preset with the same name it will be overwritten."""
    data = {}
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                data = {}

    # Dump the instruments dictionary to a native python dictionary using Pydantic v2
    data[preset.name] = {
        instrument_name: config.model_dump()
        for instrument_name, config in preset.instruments.items()
    }

    with open(path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)

def get_instruments_preset(path: str, preset_name: str) -> Optional[InstrumentsPreset]:
    """Get a preset using the name. Returns None if it doesn't exist."""
    if not os.path.exists(path):
        return None

    with open(path, 'r', encoding='utf-8') as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError:
            return None

    if preset_name not in data:
        return None

    return InstrumentsPreset(name=preset_name, instruments=data[preset_name])

def get_all_instruments_presets(path: str) -> list[InstrumentsPreset]:
    """Get all presets in the file. Returns an empty list if file doesn't exist or is empty."""
    if not os.path.exists(path):
        return []
        
    with open(path, 'r', encoding='utf-8') as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError:
            return []
            
    return [InstrumentsPreset(name=name, instruments=instrs) for name, instrs in data.items()]

def delete_instruments_preset(path: str, preset_name: str) -> bool:
    """Delete a preset by name. Returns True if successfully deleted, False otherwise."""
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
