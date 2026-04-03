import os
import pytest
from unittest.mock import MagicMock, patch

from backend.app.error import UserConfigNotFoundError, PresetNotFoundError, PresetAlreadyExistsError
from backend.app.models.presets.pieces_preset import PiecesPreset
from backend.app.models.user_config import UserConfig
from backend.app.services.pieces_preset_service import (
    _get_user_preset_file_path,
    get_preset,
    get_all_presets,
    get_all_preset_names,
    add_preset,
    update_preset,
    delete_preset
)


@pytest.fixture
def mock_session():
    return MagicMock()


@pytest.fixture
def mock_user_config():
    config = UserConfig(user_id=1, presets_pieces_path="user_1_pieces.json") # type: ignore
    return config


@pytest.fixture
def sample_preset():
    return PiecesPreset(
        name="Test Preset",
        instruments_preset_name="Standard Orch",
        user_id=1,
        pieces=["pieceA"]
    )


@patch("backend.app.services.pieces_preset_service.get_server_settings")
@patch("backend.app.services.pieces_preset_service.os.makedirs")
def test_get_user_preset_file_path_success(mock_makedirs, mock_get_settings, mock_session, mock_user_config):
    # Setup
    mock_settings = MagicMock()
    mock_settings.base_presets_pieces_path = "/base/path"
    mock_get_settings.return_value = mock_settings
    
    mock_result = MagicMock()
    mock_result.first.return_value = mock_user_config
    mock_session.exec.return_value = mock_result
    
    # Execute
    filepath = _get_user_preset_file_path(mock_session, 1)
    
    # Assert
    expected_path = os.path.join("/base/path", "user_1_pieces.json")
    assert filepath == expected_path
    mock_makedirs.assert_called_once_with(os.path.dirname(expected_path), exist_ok=True)


def test_get_user_preset_file_path_user_not_found(mock_session):
    mock_result = MagicMock()
    mock_result.first.return_value = None
    mock_session.exec.return_value = mock_result
    
    with pytest.raises(UserConfigNotFoundError):
        _get_user_preset_file_path(mock_session, 999)


@patch("backend.app.services.pieces_preset_service._get_user_preset_file_path")
@patch("backend.app.services.pieces_preset_service.pieces_preset_crud")
def test_get_preset_success(mock_crud, mock_get_path, mock_session, sample_preset):
    mock_get_path.return_value = "/dummy/path.json"
    mock_crud.get_pieces_preset.return_value = sample_preset
    
    result = get_preset(mock_session, 1, "Test Preset")
    
    assert result == sample_preset
    mock_crud.get_pieces_preset.assert_called_once_with("/dummy/path.json", "Test Preset")


@patch("backend.app.services.pieces_preset_service._get_user_preset_file_path")
@patch("backend.app.services.pieces_preset_service.pieces_preset_crud")
def test_get_preset_not_found(mock_crud, mock_get_path, mock_session):
    mock_get_path.return_value = "/dummy/path.json"
    mock_crud.get_pieces_preset.return_value = None
    
    with pytest.raises(PresetNotFoundError):
        get_preset(mock_session, 1, "Ghost Preset")


@patch("backend.app.services.pieces_preset_service._get_user_preset_file_path")
@patch("backend.app.services.pieces_preset_service.pieces_preset_crud")
def test_get_all_presets(mock_crud, mock_get_path, mock_session, sample_preset):
    mock_get_path.return_value = "/dummy/path.json"
    mock_crud.get_all_pieces_presets.return_value = [sample_preset]
    
    results = get_all_presets(mock_session, 1)
    assert results == [sample_preset]


@patch("backend.app.services.pieces_preset_service._get_user_preset_file_path")
@patch("backend.app.services.pieces_preset_service.pieces_preset_crud")
def test_get_all_preset_names(mock_crud, mock_get_path, mock_session):
    mock_get_path.return_value = "/dummy/path.json"
    mock_crud.get_all_pieces_presets_names.return_value = ["Preset1", "Preset2"]
    
    results = get_all_preset_names(mock_session, 1)
    assert results == ["Preset1", "Preset2"]


@patch("backend.app.services.pieces_preset_service._get_user_preset_file_path")
@patch("backend.app.services.pieces_preset_service.pieces_preset_crud")
def test_add_preset_success(mock_crud, mock_get_path, mock_session, sample_preset):
    mock_get_path.return_value = "/dummy/path.json"
    mock_crud.get_pieces_preset.return_value = None  # Doesn't exist yet
    
    result = add_preset(mock_session, 1, sample_preset)
    
    assert result == sample_preset
    mock_crud.save_pieces_preset.assert_called_once_with("/dummy/path.json", sample_preset)


@patch("backend.app.services.pieces_preset_service._get_user_preset_file_path")
@patch("backend.app.services.pieces_preset_service.pieces_preset_crud")
def test_add_preset_already_exists(mock_crud, mock_get_path, mock_session, sample_preset):
    mock_get_path.return_value = "/dummy/path.json"
    mock_crud.get_pieces_preset.return_value = sample_preset  # Already exists
    
    with pytest.raises(PresetAlreadyExistsError):
        add_preset(mock_session, 1, sample_preset)


@patch("backend.app.services.pieces_preset_service._get_user_preset_file_path")
@patch("backend.app.services.pieces_preset_service.pieces_preset_crud")
def test_update_preset_success(mock_crud, mock_get_path, mock_session, sample_preset):
    mock_get_path.return_value = "/dummy/path.json"
    mock_crud.get_pieces_preset.return_value = sample_preset  # Exists
    
    result = update_preset(mock_session, 1, sample_preset)
    
    assert result == sample_preset
    mock_crud.save_pieces_preset.assert_called_once_with("/dummy/path.json", sample_preset)


@patch("backend.app.services.pieces_preset_service._get_user_preset_file_path")
@patch("backend.app.services.pieces_preset_service.pieces_preset_crud")
def test_update_preset_not_found(mock_crud, mock_get_path, mock_session, sample_preset):
    mock_get_path.return_value = "/dummy/path.json"
    mock_crud.get_pieces_preset.return_value = None  # Doesn't exist
    
    with pytest.raises(PresetNotFoundError):
        update_preset(mock_session, 1, sample_preset)


@patch("backend.app.services.pieces_preset_service._get_user_preset_file_path")
@patch("backend.app.services.pieces_preset_service.pieces_preset_crud")
def test_delete_preset_success(mock_crud, mock_get_path, mock_session):
    mock_get_path.return_value = "/dummy/path.json"
    mock_crud.delete_pieces_preset.return_value = True
    
    delete_preset(mock_session, 1, "Test Preset")
    mock_crud.delete_pieces_preset.assert_called_once_with("/dummy/path.json", "Test Preset")


@patch("backend.app.services.pieces_preset_service._get_user_preset_file_path")
@patch("backend.app.services.pieces_preset_service.pieces_preset_crud")
def test_delete_preset_not_found(mock_crud, mock_get_path, mock_session):
    mock_get_path.return_value = "/dummy/path.json"
    mock_crud.delete_pieces_preset.return_value = False
    
    with pytest.raises(PresetNotFoundError):
        delete_preset(mock_session, 1, "Ghost Preset")