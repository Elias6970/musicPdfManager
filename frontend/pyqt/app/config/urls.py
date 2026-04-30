from enum import StrEnum
from typing import Any, Mapping
from urllib.parse import urlencode


BASE_URL = "http://127.0.0.1:8000"
API_PREFIX = "/api/v1"


class Endpoint(StrEnum):
    USERS = "/users"
    USER_BY_ID = "/users/{user_id}"
    USERS_REGISTER = "/users/register"
    USERS_LOGIN = "/users/login"
    USERS_CONFIG = "/users/config"

    ROLES = "/roles"
    ROLES_BY_ID = "/roles/{role_id}"    

    ARCHIVES = "/archives"
    ARCHIVE_BY_ID = "/archives/{archive_id}"
    ARCHIVE_USER_BY_ID = "/archives/{archive_id}/users/{user_id}"

    PIECES = "/archives/{archive_id}/pieces"
    PIECE_BY_ID = "/archives/{archive_id}/pieces/{piece_id}"
    PIECE_SCORES = "/archives/{archive_id}/pieces/{piece_std_name}/scores"
    PIECE_SCORES_PAGE_COUNTS = "/archives/{archive_id}/pieces/{piece_std_name}/scores/page_counts"
    PIECE_FILES = "/archives/{archive_id}/pieces/{piece_id}/files"
    PIECES_STD = "/archives/{archive_id}/pieces/std"
    PIECES_STD_DIGITALIZED = "/archives/{archive_id}/pieces/std/digitalized"

    PREVIEW = "/preview/"

    AUTHORS = "/authors"
    TYPES = "/types"

    UPLOADS_STAGING = "/uploads/staging"

    SIMPLE_PRINTER = "/printers/simple"
    PRESET_PRINTER = "/printers/preset"

    INSTRUMENT_PRESETS = "/presets/instruments"
    INSTRUMENT_PRESET_BY_NAME = "/presets/instruments/{preset_name}"
    INSTRUMENT_PRESETS_NAMES = "/presets/instruments/names"
    PIECE_PRESETS = "/presets/pieces"
    PIECE_PRESET_BY_NAME = "/presets/pieces/{preset_name}"
    PIECE_PRESETS_NAMES = "/presets/pieces/names"

    CLASSIFICATION_BY_ID = "/classification/{archive_id}"

    INSTRUMENTS_NAMES_SHORTCUTS_AND_INSTRUMENTS = "/instruments_names/shortcuts_and_instruments"
    INSTRUMENTS_NAMES_INSTRUMENTS_AND_SHORTCUTS = "/instruments_names/instruments_and_shortcuts"
    INSTRUMENTS_NAMES_TRANSLATED = "/instruments_names/instruments_and_shortcuts/{language_cod}"

def build_url(
    endpoint: Endpoint,
    *,
    path_params: Mapping[str, Any] | None = None,
    query_params: Mapping[str, Any] | None = None,
) -> str:
    """Build an absolute URL from an endpoint template.

    Example:
        build_url(
            Endpoint.PIECE_BY_ID,
            path_params={"archive_id": 1, "piece_id": 9},
        )
    """
    params = dict(path_params or {})
    try:
        path = endpoint.value.format(**params)
    except KeyError as exc:
        missing = exc.args[0]
        raise ValueError(
            f"Missing path param '{missing}' for endpoint '{endpoint.value}'"
        ) from exc

    url = f"{BASE_URL}{API_PREFIX}{path}"

    if query_params:
        cleaned_query = {
            key: value
            for key, value in query_params.items()
            if value is not None
        }
        if cleaned_query:
            url = f"{url}?{urlencode(cleaned_query, doseq=True)}"

    return url
