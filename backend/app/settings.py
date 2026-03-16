import json
import os
from typing import Literal
from pydantic import BaseModel, Field, ValidationError

DATA_FOLDER = os.path.join("data")
SERVER_SETTINGS_PATH = os.path.join(DATA_FOLDER, "server_settings.json")
SERVER_SETTINGS_VERSION = 1


class ServerSettings(BaseModel):
    """Server-side configuration values used by the FastAPI backend."""

    app_name: str = "musicPdfManager API"
    app_version: str = "1.0.0"
    environment: Literal["development", "staging", "production"] = "development" #Unused for now
    debug: bool = True #Unused for now

    host: str = "127.0.0.1" #Unused for now
    port: int = Field(default=8000, ge=1, le=65535) #Unused for now
    api_prefix: str = "/api/v1"

    database_url: str = "sqlite:///data/global.db"
    archive_root: str = ""

    jwt_secret_key: str = "change-this-secret-key"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = Field(default=60 * 24 * 7, ge=1)

    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    base_presets_instruments_path: str = "data/presets/instruments"
    base_presets_pieces_path: str = "data/presets/pieces"
    base_dossier_cover_path: str = "data/dossier_covers"

class ServerSettingsRepository:
    """Load/save/validate ServerSettings from a versioned JSON file."""

    def __init__(self, settings_path: str = SERVER_SETTINGS_PATH) -> None:
        self._settings_path = settings_path
        self._cache: ServerSettings | None = None

    def _ensure_data_folder(self) -> None:
        os.makedirs(DATA_FOLDER, exist_ok=True)

    @staticmethod
    def defaults() -> ServerSettings:
        return ServerSettings()

    def exists(self) -> bool:
        return os.path.exists(self._settings_path)

    def load(self, force_reload: bool = False) -> ServerSettings:
        if self._cache is not None and not force_reload:
            return self._cache

        self._ensure_data_folder()

        if not self.exists():
            settings = self.defaults()
            self.save(settings)
            return settings

        try:
            with open(self._settings_path, "r", encoding="utf-8") as file:
                payload = json.load(file)

            raw_settings = payload.get("settings", payload)
            settings = ServerSettings.model_validate(raw_settings)
        except (OSError, json.JSONDecodeError, ValidationError):
            settings = self.defaults()
            self.save(settings)
            return settings

        self._cache = settings
        return settings

    def save(self, settings: ServerSettings) -> None:
        self._ensure_data_folder()

        payload = {
            "version": SERVER_SETTINGS_VERSION,
            "settings": settings.model_dump(),
        }

        temp_path = f"{self._settings_path}.tmp"
        with open(temp_path, "w", encoding="utf-8") as file:
            json.dump(payload, file, indent=2)

        os.replace(temp_path, self._settings_path)
        self._cache = settings

    def validate(self, settings: ServerSettings | None = None) -> list[str]:
        current = settings or self.load()
        errors: list[str] = []

        if current.environment == "production" and current.jwt_secret_key == "change-this-secret-key":
            errors.append("jwt_secret_key")

        if current.archive_root and not os.path.isdir(current.archive_root):
            errors.append("archive_root")

        return errors


_repository = ServerSettingsRepository()


def get_server_settings(force_reload: bool = False) -> ServerSettings:
    return _repository.load(force_reload=force_reload)


def save_server_settings(settings: ServerSettings) -> None:
    _repository.save(settings)


def validate_server_settings(settings: ServerSettings | None = None) -> list[str]:
    return _repository.validate(settings)
