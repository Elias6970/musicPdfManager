import pytest
from unittest.mock import MagicMock, patch
from sqlmodel import Session

from backend.app.crud.user_config_crud import (
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


def test_create_user_config_success(mock_session):
    user_config_in = UserConfigCreate(
        language="en",
        presets_instruments_path="data/presets/instruments",
        presets_pieces_path="data/presets/pieces",
        dossier_cover_path="data/covers/default.pdf",
        user_id=1,
    )
    created_obj = UserConfig(
        id=10,
        language="en",
        presets_instruments_path="data/presets/instruments",
        presets_pieces_path="data/presets/pieces",
        dossier_cover_path="data/covers/default.pdf",
        user_id=1,
    )

    with patch("backend.app.crud.user_config_crud.UserConfig.model_validate", return_value=created_obj) as mock_validate:
        result = create_user_config(mock_session, user_config_in)

    assert result == created_obj
    mock_validate.assert_called_once_with(user_config_in)
    mock_session.add.assert_called_once_with(created_obj)
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(created_obj)


def test_get_user_config_success(mock_session):
    config = UserConfig(
        id=1,
        language="es",
        presets_instruments_path="a",
        presets_pieces_path="b",
        dossier_cover_path="c",
        user_id=7,
    )
    mock_session.get.return_value = config

    result = get_user_config(mock_session, 1)

    assert result == config
    mock_session.get.assert_called_once_with(UserConfig, 1)


def test_get_user_config_by_user_id_found(mock_session):
    config = UserConfig(
        id=2,
        language="en",
        presets_instruments_path="inst",
        presets_pieces_path="pieces",
        dossier_cover_path="cover",
        user_id=99,
    )
    exec_result = MagicMock()
    exec_result.first.return_value = config
    mock_session.exec.return_value = exec_result

    result = get_user_config_by_user_id(mock_session, 99)

    assert result == config
    mock_session.exec.assert_called_once()
    exec_result.first.assert_called_once()


def test_get_user_config_by_user_id_not_found(mock_session):
    exec_result = MagicMock()
    exec_result.first.return_value = None
    mock_session.exec.return_value = exec_result

    result = get_user_config_by_user_id(mock_session, 1234)

    assert result is None
    mock_session.exec.assert_called_once()
    exec_result.first.assert_called_once()


def test_update_user_config_success(mock_session):
    existing = UserConfig(
        id=3,
        language="es",
        presets_instruments_path="old_inst",
        presets_pieces_path="old_pieces",
        dossier_cover_path="old_cover",
        user_id=5,
    )
    mock_session.get.return_value = existing

    update_in = UserConfigCreate(
        language="en",
        presets_instruments_path="new_inst",
        presets_pieces_path="new_pieces",
        dossier_cover_path="new_cover",
        user_id=5,
    )

    result = update_user_config(mock_session, 3, update_in)

    assert result == existing
    assert existing.language == "en"
    assert existing.presets_instruments_path == "new_inst"
    assert existing.presets_pieces_path == "new_pieces"
    assert existing.dossier_cover_path == "new_cover"
    assert existing.user_id == 5
    mock_session.get.assert_called_once_with(UserConfig, 3)
    mock_session.add.assert_called_once_with(existing)
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(existing)


def test_update_user_config_not_found(mock_session):
    mock_session.get.return_value = None
    update_in = UserConfigCreate(
        language="en",
        presets_instruments_path="x",
        presets_pieces_path="y",
        dossier_cover_path="z",
        user_id=1,
    )

    result = update_user_config(mock_session, 999, update_in)

    assert result is None
    mock_session.get.assert_called_once_with(UserConfig, 999)
    mock_session.add.assert_not_called()
    mock_session.commit.assert_not_called()
    mock_session.refresh.assert_not_called()


def test_delete_user_config_success(mock_session):
    existing = UserConfig(
        id=4,
        language="en",
        presets_instruments_path="inst",
        presets_pieces_path="pieces",
        dossier_cover_path="cover",
        user_id=2,
    )
    mock_session.get.return_value = existing

    result = delete_user_config(mock_session, 4)

    assert result is True
    mock_session.get.assert_called_once_with(UserConfig, 4)
    mock_session.delete.assert_called_once_with(existing)
    mock_session.commit.assert_called_once()


def test_delete_user_config_not_found(mock_session):
    mock_session.get.return_value = None

    result = delete_user_config(mock_session, 404)

    assert result is False
    mock_session.get.assert_called_once_with(UserConfig, 404)
    mock_session.delete.assert_not_called()
    mock_session.commit.assert_not_called()
