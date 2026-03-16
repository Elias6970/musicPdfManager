import json

from backend.app.settings import (
    ServerSettings,
    ServerSettingsRepository,
)


def test_load_creates_defaults_when_file_missing(tmp_path, monkeypatch):
    settings_path = tmp_path / "server_settings.json"
    monkeypatch.setattr("backend.app.settings.DATA_FOLDER", str(tmp_path))

    repo = ServerSettingsRepository(settings_path=str(settings_path))
    settings = repo.load()

    assert settings == ServerSettings()
    assert settings_path.exists()

    payload = json.loads(settings_path.read_text(encoding="utf-8"))
    assert payload["version"] == 1
    assert payload["settings"]["app_name"] == "musicPdfManager API"


def test_save_then_load_persists_settings(tmp_path, monkeypatch):
    settings_path = tmp_path / "server_settings.json"
    monkeypatch.setattr("backend.app.settings.DATA_FOLDER", str(tmp_path))

    repo = ServerSettingsRepository(settings_path=str(settings_path))
    expected = ServerSettings(app_name="My API", log_level="DEBUG", api_prefix="/api/test")

    repo.save(expected)
    loaded = repo.load(force_reload=True)

    assert loaded == expected


def test_load_invalid_json_recovers_with_defaults(tmp_path, monkeypatch):
    settings_path = tmp_path / "server_settings.json"
    monkeypatch.setattr("backend.app.settings.DATA_FOLDER", str(tmp_path))
    settings_path.write_text("{ invalid json", encoding="utf-8")

    repo = ServerSettingsRepository(settings_path=str(settings_path))
    settings = repo.load()

    assert settings == ServerSettings()


def test_validate_flags_production_default_secret_and_bad_archive_root(tmp_path, monkeypatch):
    settings_path = tmp_path / "server_settings.json"
    monkeypatch.setattr("backend.app.settings.DATA_FOLDER", str(tmp_path))

    repo = ServerSettingsRepository(settings_path=str(settings_path))
    invalid = ServerSettings(
        environment="production",
        jwt_secret_key="change-this-secret-key",
        archive_root=str(tmp_path / "missing_dir"),
    )

    errors = repo.validate(invalid)

    assert "jwt_secret_key" in errors
    assert "archive_root" in errors


def test_validate_accepts_existing_archive_root(tmp_path, monkeypatch):
    settings_path = tmp_path / "server_settings.json"
    monkeypatch.setattr("backend.app.settings.DATA_FOLDER", str(tmp_path))
    archive_root = tmp_path / "archive"
    archive_root.mkdir()

    repo = ServerSettingsRepository(settings_path=str(settings_path))
    valid = ServerSettings(
        environment="development",
        jwt_secret_key="strong-secret",
        archive_root=str(archive_root),
    )

    errors = repo.validate(valid)

    assert errors == []