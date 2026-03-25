import os
import json
import pytest

from backend.app.models.presets.instruments_preset import InstrumentsPreset, InstrumentConfig
from backend.app.crud.instruments_preset_crud import (
    save_instruments_preset,
    get_instruments_preset,
    delete_instruments_preset
)

@pytest.fixture
def test_json_path(tmp_path):
    # Pytest's tmp_path provides a temporary directory unique to the test invocation
    return str(tmp_path / "test_presets.json")

@pytest.fixture
def sample_preset():
    return InstrumentsPreset(
        name="test_preset",
        instruments={
            "oboe": InstrumentConfig(copies=3, other_options=["flauta_1", "clarinete_1"]),
            "clarinete principal": InstrumentConfig(copies=1, other_options=[])
        }
    )

def test_save_instruments_preset_creates_file(test_json_path, sample_preset):
    # Test saving a new preset when the file doesn't exist
    save_instruments_preset(test_json_path, sample_preset)
    
    # Verify the file was created and contains the right data
    assert os.path.exists(test_json_path)
    with open(test_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    assert "test_preset" in data
    assert "oboe" in data["test_preset"]
    assert data["test_preset"]["oboe"]["copies"] == 3
    assert data["test_preset"]["oboe"]["other_options"] == ["flauta_1", "clarinete_1"]

def test_save_instruments_preset_updates_existing(test_json_path, sample_preset):
    # Save the initial preset
    save_instruments_preset(test_json_path, sample_preset)
    
    # Modify the preset's data and save it again
    sample_preset.instruments["oboe"].copies = 5
    sample_preset.instruments["clarinete principal"].copies = 2
    save_instruments_preset(test_json_path, sample_preset)
    
    # Verify the contents were updated
    with open(test_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    assert data["test_preset"]["oboe"]["copies"] == 5
    assert data["test_preset"]["clarinete principal"]["copies"] == 2

def test_get_instruments_preset_exists(test_json_path, sample_preset):
    # First save the preset so it exists
    save_instruments_preset(test_json_path, sample_preset)
    
    # Retrieve it using the name
    retrieved_preset = get_instruments_preset(test_json_path, sample_preset.name)
    
    assert retrieved_preset is not None
    assert retrieved_preset.name == "test_preset"
    assert "oboe" in retrieved_preset.instruments
    assert isinstance(retrieved_preset.instruments["oboe"], InstrumentConfig)
    assert retrieved_preset.instruments["oboe"].copies == 3

def test_get_instruments_preset_not_exists(test_json_path):
    # Retrieve a preset that doesn't exist
    retrieved_preset = get_instruments_preset(test_json_path, "nonexistent")
    assert retrieved_preset is None

def test_delete_instruments_preset_exists(test_json_path, sample_preset):
    # First save the preset
    save_instruments_preset(test_json_path, sample_preset)
    
    # Delete the preset
    result = delete_instruments_preset(test_json_path, sample_preset.name)
    assert result is True
    
    # Verify the preset is no longer retrievable
    retrieved_preset = get_instruments_preset(test_json_path, sample_preset.name)
    assert retrieved_preset is None

def test_delete_instruments_preset_not_exists(test_json_path, sample_preset):
    # Create the file with some other preset
    save_instruments_preset(test_json_path, sample_preset)
    
    # Try deleting a preset that isn't in the file
    result = delete_instruments_preset(test_json_path, "nonexistent")
    assert result is False
