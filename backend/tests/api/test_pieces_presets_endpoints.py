import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from fastapi import FastAPI

from backend.main import app
from backend.app.models.presets.pieces_preset import PiecesPreset, PiecesPresetCreate
from backend.app.models.printers.elements.printeable_piece import PrinteablePiece
from backend.app.models.user import User
from backend.api.dependencies.database import get_session
from backend.api.dependencies.permissions import require_user
from backend.app.error import UserConfigNotFoundError, PresetNotFoundError, PresetAlreadyExistsError

client = TestClient(app)

@pytest.fixture
def sample_preset():
    return PiecesPreset(
        name="Test Preset",
        instruments_preset_name="Standard Orch",
        user_id=1,
        pieces=[PrinteablePiece(std_name="pieceA", copies=1), PrinteablePiece(std_name="pieceB", copies=1)]
    )

@pytest.fixture
def sample_preset_create():
    return PiecesPresetCreate(
        name="Test Preset",
        instruments_preset_name="Standard Orch",
        pieces=[PrinteablePiece(std_name="pieceA", copies=1), PrinteablePiece(std_name="pieceB", copies=1)]
    )

@pytest.fixture
def mock_user():
    user = MagicMock(spec=User)
    user.id = 1
    return user

# Override the dependency for all tests
@pytest.fixture(autouse=True)
def override_dependencies(mock_user):
    app.dependency_overrides[require_user] = lambda: mock_user
    app.dependency_overrides[get_session] = lambda: MagicMock()
    yield
    app.dependency_overrides.clear()

@patch("backend.api.routes.pieces_presets.get_all_presets")
def test_get_all_pieces_presets(mock_get_all, sample_preset):
    mock_get_all.return_value = [sample_preset]
    response = client.get("/api/v1/presets/pieces")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Test Preset"

@patch("backend.api.routes.pieces_presets.get_all_preset_names")
def test_get_all_pieces_preset_names(mock_get_names):
    mock_get_names.return_value = ["Test Preset"]
    response = client.get("/api/v1/presets/pieces/names")
    assert response.status_code == 200
    assert response.json() == ["Test Preset"]

@patch("backend.api.routes.pieces_presets.get_preset")
def test_get_pieces_preset(mock_get_preset, sample_preset):
    mock_get_preset.return_value = sample_preset
    response = client.get("/api/v1/presets/pieces/Test Preset")
    assert response.status_code == 200
    assert response.json()["name"] == "Test Preset"

@patch("backend.api.routes.pieces_presets.get_preset")
def test_get_pieces_preset_not_found(mock_get_preset):
    mock_get_preset.side_effect = PresetNotFoundError("Not found")
    response = client.get("/api/v1/presets/pieces/Ghost")
    assert response.status_code == 404

@patch("backend.api.routes.pieces_presets.add_preset")
def test_create_pieces_preset(mock_add_preset, sample_preset, sample_preset_create):
    mock_add_preset.return_value = sample_preset
    response = client.post("/api/v1/presets/pieces", json=sample_preset_create.model_dump())
    assert response.status_code == 201
    assert response.json()["name"] == "Test Preset"

@patch("backend.api.routes.pieces_presets.add_preset")
def test_create_pieces_preset_conflict(mock_add_preset, sample_preset_create):
    mock_add_preset.side_effect = PresetAlreadyExistsError("Already exists")
    response = client.post("/api/v1/presets/pieces", json=sample_preset_create.model_dump())
    assert response.status_code == 409

@patch("backend.api.routes.pieces_presets.update_preset")
def test_update_pieces_preset(mock_update_preset, sample_preset, sample_preset_create):
    mock_update_preset.return_value = sample_preset
    response = client.put("/api/v1/presets/pieces", json=sample_preset_create.model_dump())
    assert response.status_code == 200
    assert response.json()["name"] == "Test Preset"

@patch("backend.api.routes.pieces_presets.delete_preset")
def test_delete_pieces_preset(mock_delete_preset):
    mock_delete_preset.return_value = None
    response = client.delete("/api/v1/presets/pieces/Test Preset")
    assert response.status_code == 204
