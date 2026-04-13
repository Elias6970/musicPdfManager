"""
SessionManager to hold the application's current session state.
Utilizes PyQt6 QSettings to manage session memory.
"""
from PyQt6.QtCore import QSettings

class SessionManager:
    def __init__(self):
        # QSettings natively behaves exactly like a singleton regarding the 
        # actual data across different instantiations when using the same args
        self.settings = QSettings("MusicPdfManager", "Session")
        
        # Hardcoded default values for testing
        if not self.settings.contains("jwt"):
            self.settings.setValue("jwt", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NzYwODczMDgsInN1YiI6IjEifQ.ESlbfvOA2NfdEK2LVBqK5yusMLi7wRPSCNbIq-0dbrA")
        if not self.settings.contains("archive_id"):
            self.settings.setValue("archive_id", 1)
        if not self.settings.contains("language"):
            self.settings.setValue("language", "en_US")

    def get_jwt(self) -> str:
        return self.settings.value("jwt", type=str)

    def set_jwt(self, token: str):
        self.settings.setValue("jwt", token)

    def get_archive_id(self) -> int:
        return self.settings.value("archive_id", type=int)

    def set_archive_id(self, archive_id: int):
        self.settings.setValue("archive_id", archive_id)

    def get_language(self) -> str:
        return self.settings.value("language", type=str)

    def set_language(self, language: str):
        self.settings.setValue("language", language)

    def is_logged_in(self) -> bool:
        jwt = self.get_jwt()
        return bool(jwt and jwt != "dummy_jwt_token_12345")
    
    def clear_session(self):
        self.settings.clear()