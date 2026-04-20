import pytest
from unittest.mock import MagicMock, patch
from sqlmodel import Session

from backend.app.services.user_config_services import (
    create_user_config,
    get_user_config,
    get_user_config_by_user_id,
    update_user_config,
    delete_user_config,
)
from backend.app.models.user_config import UserConfig, UserConfigCreate


@pytest.fixture
def mock_session():
    return MagicMock(spec=Session)


@patch("backend.app.services.user_config_services.user_config_crud")
def test_create_user_config(mock_crud, mock_session):
    user_config_in = UserConfigCreate(
        language="en",
        user_id=1,
    )
    
    expected_returned_config = UserConfig(
        id=1,
        language="en",
        user_id=1,
        presets_instruments_path="mock.json",
        presets_pieces_path="mock.json",
        dossier_cover_path="mock.json"
    )
    mock_crud.create_user_config.return_value = expected_returned_config

    result = create_user_config(mock_session, user_config_in)

    assert result == expected_returned_config
    mock_crud.create_user_config.assert_called_once()
    
    # Extract the argument passed to the CRUD object
    call_args = mock_crud.create_user_config.call_args[1]
    db_obj_passed = call_args["user_config_in"]
    
    assert db_obj_passed.language == "en"
    assert db_obj_passed.user_id == 1
    assert db_obj_passed.presets_instruments_path.endswith(".json")
    assert db_obj_passed.presets_pieces_path.endswith(".json")
    assert db_obj_passed.dossier_cover_path.endswith(".json")


@patch("backend.app.services.user_config_services.user_config_crud")
def test_get_user_config(mock_crud, mock_session):
    expected_config = UserConfig(
        id=1, language="en", user_id=1, 
        presets_instruments_path="a", presets_pieces_path="b", dossier_cover_path="c"
    )
    mock_crud.get_user_config.return_value = expected_config

    result = get_user_config(mock_session, 1)

    assert result == expected_config
    mock_crud.get_user_config.assert_called_once_with(mock_session, 1)


@patch("backend.app.services.user_config_services.user_config_crud")
def test_get_user_config_by_user_id(mock_crud, mock_session):
    expected_config = UserConfig(
        id=2, language="es", user_id=99,
        presets_instruments_path="a", presets_pieces_path="b", dossier_cover_path="c"
    )
    mock_crud.get_user_config_by_user_id.return_value = expected_config

    result = get_user_config_by_user_id(mock_session, 99)

    assert result == expected_config
    mock_crud.get_user_config_by_user_id.assert_called_once_with(mock_session, 99)


@patch("backend.app.services.user_config_services.user_config_crud")
def test_update_user_config_success(mock_crud, mock_session):
    existing_db_obj = UserConfig(
        id=1,
        language="en",
        user_id=5,
        presets_instruments_path="inst.json",
        presets_pieces_path="pieces.json",
        dossier_cover_path="cover.json"
    )
    mock_crud.get_user_config.return_value = existing_db_obj
    mock_crud.update_user_config.return_value = existing_db_obj

    update_in = UserConfigCreate(language="fr", user_id=5)

    result = update_user_config(mock_session, 1, update_in)

    assert result is not None
    assert result.language == "fr"
    # Ensure paths remained unchanged
    assert result.presets_instruments_path == "inst.json"
    
    mock_crud.get_user_config.assert_called_once_with(mock_session, 1)
    mock_crud.update_user_config.assert_called_once()


@patch("backend.app.services.user_config_services.user_config_crud")
def test_update_user_config_not_found(mock_crud, mock_session):
    mock_crud.get_user_config.return_value = None

    update_in = UserConfigCreate(language="fr", user_id=5)
    result = update_user_config(mock_session, 404, update_in)

    assert result is None
    mock_crud.get_user_config.assert_called_once_with(mock_session, 404)
    mock_crud.update_user_config.assert_not_called()


@patch("backend.app.services.user_config_services.user_config_crud")
def test_delete_user_config(mock_crud, mock_session):
    mock_crud.delete_user_config.return_value = True

    result = delete_user_config(mock_session, 1)

    assert result is True
    mock_crud.delete_user_config.assert_called_once_with(mock_session, 1)