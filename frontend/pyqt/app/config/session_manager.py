"""
SessionManager to hold the application's current session state.
Utilizes PyQt6 QSettings to manage session memory.
"""
from PyQt6.QtCore import QSettings

JWT_SESSION_KEY = "jwt"
ARCHIVE_ID_SESSION_KEY = "archive_id"
LANGUAGE_SESSION_KEY = "language"

class SessionManager:
    def __init__(self):
        # QSettings natively behaves exactly like a singleton regarding the 
        # actual data across different instantiations when using the same args
        self.settings = QSettings("MusicPdfManager", "Session")

    def get_jwt(self) -> str:
        return self.settings.value(JWT_SESSION_KEY, type=str)

    def set_jwt(self, token: str):
        self.settings.setValue(JWT_SESSION_KEY, token)

    def get_archive_id(self) -> int:
        return self.settings.value(ARCHIVE_ID_SESSION_KEY, type=int, defaultValue=-1)

    def set_archive_id(self, archive_id: int):
        self.settings.setValue(ARCHIVE_ID_SESSION_KEY, archive_id)

    def get_language(self) -> str:
        return self.settings.value(LANGUAGE_SESSION_KEY, type=str)

    def set_language(self, language: str):
        self.settings.setValue(LANGUAGE_SESSION_KEY, language)

    def is_logged_in(self) -> bool:
        jwt = self.get_jwt()
        return bool(jwt and jwt != "dummy_jwt_token_12345")
    
    def has_archive_id(self) -> bool:
        archive_id = self.get_archive_id()
        return archive_id is not None and archive_id != -1

    def clear_session(self):
        self.settings.clear()