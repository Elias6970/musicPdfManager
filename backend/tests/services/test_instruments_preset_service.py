import os
import pytest
from unittest.mock import MagicMock, patch

from backend.app.models.presets.instruments_preset import InstrumentsPreset, InstrumentConfig
from backend.app.error import UserConfigNotFoundError, PresetNotFoundError, PresetAlreadyExistsError
from backend.app.services.instruments_preset_service import (
    _get_user_preset_file_path,
    get_preset,
    get_all_presets,
    get_all_presets_names,
    add_preset,
    update_preset,
    delete_preset
)

@pytest.fixture
def sample_preset():
    return InstrumentsPreset(
        name="test_preset",
        instruments={
            "oboe": InstrumentConfig(copies=3, other_options=["flauta_1", "clarinete_1"])
        }
    )

@pytest.fixture
def mock_session():
    return MagicMock()

# ---------------------------------------------------------
# Tests for _get_user_preset_file_path
# ---------------------------------------------------------

@patch("backend.app.services.instruments_preset_service.get_server_settings")
@patch("backend.app.services.instruments_preset_service.os.makedirs")
def test_get_user_preset_file_path_success(mock_makedirs, mock_get_settings, mock_session):
    # Arrange
    mock_user_config = MagicMock()
    mock_user_config.presets_instruments_path = "user1_presets.json"
    mock_session.exec.return_value.first.return_value = mock_user_config
    
    mock_settings = MagicMock()
    mock_settings.base_presets_instruments_path = "/mock/base/path"
    mock_get_settings.return_value = mock_settings
    
    # Act
    result_path = _get_user_preset_file_path(mock_session, user_id=1)
    
    # Assert
    expected_path = os.path.join("/mock/base/path", "user1_presets.json")
    assert result_path == expected_path
    mock_makedirs.assert_called_once_with("/mock/base/path", exist_ok=True)

def test_get_user_preset_file_path_not_found(mock_session):
    # Arrange
    mock_session.exec.return_value.first.return_value = None
    
    # Act & Assert
    with pytest.raises(UserConfigNotFoundError, match="User configuration not found"):
        _get_user_preset_file_path(mock_session, user_id=1)

# ---------------------------------------------------------
# Tests for get_preset
# ---------------------------------------------------------

@patch("backend.app.services.instruments_preset_service.instruments_preset_crud.get_instruments_preset")
@patch("backend.app.services.instruments_preset_service._get_user_preset_file_path")
def test_get_preset_success(mock_get_path, mock_crud_get, mock_session, sample_preset):
    # Arrange
    mock_get_path.return_value = "/dummy/presets.json"
    mock_crud_get.return_value = sample_preset

    # Act
    result = get_preset(mock_session, 1, "test_preset")

    # Assert
    assert result == sample_preset
    mock_get_path.assert_called_once_with(mock_session, 1)
    mock_crud_get.assert_called_once_with("/dummy/presets.json", "test_preset")

@patch("backend.app.services.instruments_preset_service.instruments_preset_crud.get_instruments_preset")
@patch("backend.app.services.instruments_preset_service._get_user_preset_file_path")
def test_get_preset_not_found(mock_get_path, mock_crud_get, mock_session):
    # Arrange
    mock_get_path.return_value = "/dummy/presets.json"
    mock_crud_get.return_value = None

    # Act & Assert
    with pytest.raises(PresetNotFoundError, match="Preset 'test_preset' not found"):
        get_preset(mock_session, 1, "test_preset")

# ---------------------------------------------------------
# Tests for get_all_presets
# ---------------------------------------------------------

@patch("backend.app.services.instruments_preset_service.instruments_preset_crud.get_all_instruments_presets")
@patch("backend.app.services.instruments_preset_service._get_user_preset_file_path")
def test_get_all_presets(mock_get_path, mock_crud_get_all, mock_session, sample_preset):
    # Arrange
    mock_get_path.return_value = "/dummy/presets.json"
    mock_crud_get_all.return_value = [sample_preset, InstrumentsPreset(name="preset_2", instruments={})]

    # Act
    results = get_all_presets(mock_session, 1)

    # Assert
    assert len(results) == 2
    assert results[0] == sample_preset
    assert results[1].name == "preset_2"
    mock_get_path.assert_called_once_with(mock_session, 1)
    mock_crud_get_all.assert_called_once_with("/dummy/presets.json")

# ---------------------------------------------------------
# Tests for get_all_presets_names
# ---------------------------------------------------------

@patch("backend.app.services.instruments_preset_service.instruments_preset_crud.get_all_instruments_presets")
@patch("backend.app.services.instruments_preset_service._get_user_preset_file_path")
def test_get_all_presets_names(mock_get_path, mock_crud_get_all, mock_session, sample_preset):
    # Arrange
    mock_get_path.return_value = "/dummy/presets.json"
    mock_crud_get_all.return_value = [sample_preset, InstrumentsPreset(name="preset_2", instruments={})]

    # Act
    results = get_all_presets_names(mock_session, 1)

    # Assert
    assert len(results) == 2
    assert results[0] == "test_preset"
    assert results[1] == "preset_2"
    mock_get_path.assert_called_once_with(mock_session, 1)
    mock_crud_get_all.assert_called_once_with("/dummy/presets.json")

# ---------------------------------------------------------
# Tests for add_preset
# ---------------------------------------------------------

@patch("backend.app.services.instruments_preset_service.instruments_preset_crud.save_instruments_preset")
@patch("backend.app.services.instruments_preset_service.instruments_preset_crud.get_instruments_preset")
@patch("backend.app.services.instruments_preset_service._get_user_preset_file_path")
def test_add_preset_success(mock_get_path, mock_crud_get, mock_crud_save, mock_session, sample_preset):
    # Arrange
    mock_get_path.return_value = "/dummy/presets.json"
    mock_crud_get.return_value = None  # No existing preset

    # Act
    result = add_preset(mock_session, 1, sample_preset)

    # Assert
    assert result == sample_preset
    mock_crud_save.assert_called_once_with("/dummy/presets.json", sample_preset)

@patch("backend.app.services.instruments_preset_service.instruments_preset_crud.save_instruments_preset")
@patch("backend.app.services.instruments_preset_service.instruments_preset_crud.get_instruments_preset")
@patch("backend.app.services.instruments_preset_service._get_user_preset_file_path")
def test_add_preset_already_exists(mock_get_path, mock_crud_get, mock_crud_save, mock_session, sample_preset):
    # Arrange
    mock_get_path.return_value = "/dummy/presets.json"
    mock_crud_get.return_value = sample_preset  # Preset already exists

    # Act & Assert
    with pytest.raises(PresetAlreadyExistsError, match="Preset 'test_preset' already exists"):
        add_preset(mock_session, 1, sample_preset)
        
    mock_crud_save.assert_not_called()

# ---------------------------------------------------------
# Tests for update_preset
# ---------------------------------------------------------

@patch("backend.app.services.instruments_preset_service.instruments_preset_crud.save_instruments_preset")
@patch("backend.app.services.instruments_preset_service.instruments_preset_crud.get_instruments_preset")
@patch("backend.app.services.instruments_preset_service._get_user_preset_file_path")
def test_update_preset_success_same_name(mock_get_path, mock_crud_get, mock_crud_save, mock_session, sample_preset):
    # Arrange
    mock_get_path.return_value = "/dummy/presets.json"
    mock_crud_get.return_value = sample_preset  # Existing preset found

    # Act
    result = update_preset(mock_session, 1, "test_preset", sample_preset)

    # Assert
    assert result == sample_preset
    mock_crud_save.assert_called_once_with("/dummy/presets.json", sample_preset)

@patch("backend.app.services.instruments_preset_service.instruments_preset_crud.delete_instruments_preset")
@patch("backend.app.services.instruments_preset_service.instruments_preset_crud.save_instruments_preset")
@patch("backend.app.services.instruments_preset_service.instruments_preset_crud.get_instruments_preset")
@patch("backend.app.services.instruments_preset_service._get_user_preset_file_path")
def test_update_preset_success_different_name(mock_get_path, mock_crud_get, mock_crud_save, mock_crud_delete, mock_session, sample_preset):
    # Arrange
    mock_get_path.return_value = "/dummy/presets.json"
    # first call is for old name, second is for new name
    old_preset_mock = InstrumentsPreset(name="old_preset", instruments={})
    
    def mock_get_side_effect(path, name):
        if name == "old_preset":
            return old_preset_mock
        elif name == sample_preset.name:
            return None
        return None
        
    mock_crud_get.side_effect = mock_get_side_effect

    # Act
    result = update_preset(mock_session, 1, "old_preset", sample_preset)

    # Assert
    assert result == sample_preset
    mock_crud_save.assert_called_once_with("/dummy/presets.json", sample_preset)
    mock_crud_delete.assert_called_once_with("/dummy/presets.json", "old_preset")

@patch("backend.app.services.instruments_preset_service.instruments_preset_crud.save_instruments_preset")
@patch("backend.app.services.instruments_preset_service.instruments_preset_crud.get_instruments_preset")
@patch("backend.app.services.instruments_preset_service._get_user_preset_file_path")
def test_update_preset_not_found(mock_get_path, mock_crud_get, mock_crud_save, mock_session, sample_preset):
    # Arrange
    mock_get_path.return_value = "/dummy/presets.json"
    mock_crud_get.return_value = None  # No existing preset found

    # Act & Assert
    with pytest.raises(PresetNotFoundError, match="Preset 'old_preset' not found"):
        update_preset(mock_session, 1, "old_preset", sample_preset)
        
    mock_crud_save.assert_not_called()

@patch("backend.app.services.instruments_preset_service.instruments_preset_crud.save_instruments_preset")
@patch("backend.app.services.instruments_preset_service.instruments_preset_crud.get_instruments_preset")
@patch("backend.app.services.instruments_preset_service._get_user_preset_file_path")
def test_update_preset_already_exists_different_name(mock_get_path, mock_crud_get, mock_crud_save, mock_session, sample_preset):
    # Arrange
    mock_get_path.return_value = "/dummy/presets.json"
    old_preset_mock = InstrumentsPreset(name="old_preset", instruments={})
    
    def mock_get_side_effect(path, name):
        if name == "old_preset":
            return old_preset_mock
        elif name == sample_preset.name:
            return sample_preset
        return None
        
    mock_crud_get.side_effect = mock_get_side_effect

    # Act & Assert
    with pytest.raises(PresetAlreadyExistsError, match="Preset 'test_preset' already exists"):
        update_preset(mock_session, 1, "old_preset", sample_preset)
        
    mock_crud_save.assert_not_called()

# ---------------------------------------------------------
# Tests for delete_preset
# ---------------------------------------------------------

@patch("backend.app.services.instruments_preset_service.instruments_preset_crud.delete_instruments_preset")
@patch("backend.app.services.instruments_preset_service._get_user_preset_file_path")
def test_delete_preset_success(mock_get_path, mock_crud_delete, mock_session):
    # Arrange
    mock_get_path.return_value = "/dummy/presets.json"
    mock_crud_delete.return_value = True

    # Act
    delete_preset(mock_session, 1, "test_preset")

    # Assert
    mock_crud_delete.assert_called_once_with("/dummy/presets.json", "test_preset")

@patch("backend.app.services.instruments_preset_service.instruments_preset_crud.delete_instruments_preset")
@patch("backend.app.services.instruments_preset_service._get_user_preset_file_path")
def test_delete_preset_not_found(mock_get_path, mock_crud_delete, mock_session):
    # Arrange
    mock_get_path.return_value = "/dummy/presets.json"
    mock_crud_delete.return_value = False

    # Act & Assert
    with pytest.raises(PresetNotFoundError, match="Preset 'test_preset' not found"):
        delete_preset(mock_session, 1, "test_preset")