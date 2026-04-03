import json
import pytest

from backend.app.models.presets.pieces_preset import PiecesPreset
from backend.app.crud.pieces_preset_crud import (
    save_pieces_preset,
    get_pieces_preset,
    get_all_pieces_presets,
    get_all_pieces_presets_names,
    delete_pieces_preset
)


@pytest.fixture
def sample_preset() -> PiecesPreset:
    return PiecesPreset(
        name="Concert Set",
        instruments_preset_name="Standard Orch",
        user_id=1,
        pieces=["pieceA", "pieceB"]
    )


@pytest.fixture
def sample_preset_2() -> PiecesPreset:
    return PiecesPreset(
        name="Rehearsal Set",
        instruments_preset_name="Brass Only",
        user_id=1,
        pieces=["pieceC"]
    )


def test_save_pieces_preset_creates_file(tmp_path, sample_preset):
    filepath = tmp_path / "presets.json"
    save_pieces_preset(str(filepath), sample_preset)
    
    assert filepath.exists()
    
    data = json.loads(filepath.read_text(encoding="utf-8"))
    assert "Concert Set" in data
    assert data["Concert Set"]["pieces"] == ["pieceA", "pieceB"]
    assert data["Concert Set"]["user_id"] == 1


def test_save_pieces_preset_updates_existing_file(tmp_path, sample_preset, sample_preset_2):
    filepath = tmp_path / "presets.json"
    save_pieces_preset(str(filepath), sample_preset)
    save_pieces_preset(str(filepath), sample_preset_2)
    
    data = json.loads(filepath.read_text(encoding="utf-8"))
    assert len(data) == 2
    assert "Concert Set" in data
    assert "Rehearsal Set" in data


def test_save_pieces_preset_handles_invalid_json(tmp_path, sample_preset):
    filepath = tmp_path / "presets.json"
    filepath.write_text("{invalid: json, }", encoding="utf-8")
    
    save_pieces_preset(str(filepath), sample_preset)
    
    data = json.loads(filepath.read_text(encoding="utf-8"))
    assert "Concert Set" in data


def test_get_pieces_preset_valid(tmp_path, sample_preset):
    filepath = tmp_path / "presets.json"
    save_pieces_preset(str(filepath), sample_preset)
    
    loaded = get_pieces_preset(str(filepath), "Concert Set")
    
    assert loaded is not None
    assert loaded.name == sample_preset.name
    assert loaded.instruments_preset_name == sample_preset.instruments_preset_name
    assert loaded.user_id == sample_preset.user_id
    assert loaded.pieces == sample_preset.pieces


def test_get_pieces_preset_not_found(tmp_path, sample_preset):
    filepath = tmp_path / "presets.json"
    save_pieces_preset(str(filepath), sample_preset)
    
    loaded = get_pieces_preset(str(filepath), "Nonexistent Set")
    assert loaded is None


def test_get_pieces_preset_no_file(tmp_path):
    filepath = tmp_path / "missing.json"
    loaded = get_pieces_preset(str(filepath), "Concert Set")
    assert loaded is None


def test_get_pieces_preset_invalid_json(tmp_path):
    filepath = tmp_path / "presets.json"
    filepath.write_text("{bad, json}", encoding="utf-8")
    
    loaded = get_pieces_preset(str(filepath), "Concert Set")
    assert loaded is None


def test_get_all_pieces_presets_returns_list(tmp_path, sample_preset, sample_preset_2):
    filepath = tmp_path / "presets.json"
    save_pieces_preset(str(filepath), sample_preset)
    save_pieces_preset(str(filepath), sample_preset_2)
    
    all_presets = get_all_pieces_presets(str(filepath))
    
    assert len(all_presets) == 2
    names = [p.name for p in all_presets]
    assert "Concert Set" in names
    assert "Rehearsal Set" in names


def test_get_all_pieces_presets_no_file(tmp_path):
    filepath = tmp_path / "missing.json"
    all_presets = get_all_pieces_presets(str(filepath))
    assert all_presets == []


def test_get_all_pieces_presets_invalid_json(tmp_path):
    filepath = tmp_path / "presets.json"
    filepath.write_text("{what even is this?}", encoding="utf-8")
    
    all_presets = get_all_pieces_presets(str(filepath))
    assert all_presets == []


def test_get_all_pieces_presets_names_returns_list(tmp_path, sample_preset, sample_preset_2):
    filepath = tmp_path / "presets.json"
    save_pieces_preset(str(filepath), sample_preset)
    save_pieces_preset(str(filepath), sample_preset_2)
    
    names = get_all_pieces_presets_names(str(filepath))
    
    assert len(names) == 2
    assert "Concert Set" in names
    assert "Rehearsal Set" in names


def test_get_all_pieces_presets_names_no_file(tmp_path):
    filepath = tmp_path / "missing.json"
    names = get_all_pieces_presets_names(str(filepath))
    assert names == []


def test_get_all_pieces_presets_names_invalid_json(tmp_path):
    filepath = tmp_path / "presets.json"
    filepath.write_text("{what even is this?}", encoding="utf-8")
    
    names = get_all_pieces_presets_names(str(filepath))
    assert names == []


def test_delete_pieces_preset_success(tmp_path, sample_preset, sample_preset_2):
    filepath = tmp_path / "presets.json"
    save_pieces_preset(str(filepath), sample_preset)
    save_pieces_preset(str(filepath), sample_preset_2)
    
    result = delete_pieces_preset(str(filepath), "Concert Set")
    assert result is True
    
    data = json.loads(filepath.read_text(encoding="utf-8"))
    assert "Concert Set" not in data
    assert "Rehearsal Set" in data


def test_delete_pieces_preset_not_found(tmp_path, sample_preset):
    filepath = tmp_path / "presets.json"
    save_pieces_preset(str(filepath), sample_preset)
    
    result = delete_pieces_preset(str(filepath), "Ghost Set")
    assert result is False
    
    data = json.loads(filepath.read_text(encoding="utf-8"))
    assert "Concert Set" in data


def test_delete_pieces_preset_no_file(tmp_path):
    filepath = tmp_path / "missing.json"
    result = delete_pieces_preset(str(filepath), "Concert Set")
    assert result is False


def test_delete_pieces_preset_invalid_json(tmp_path):
    filepath = tmp_path / "presets.json"
    filepath.write_text("{corrupt[}", encoding="utf-8")
    
    result = delete_pieces_preset(str(filepath), "Concert Set")
    assert result is False