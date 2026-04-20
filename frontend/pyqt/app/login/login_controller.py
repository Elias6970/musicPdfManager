from PyQt6.QtCore import QObject
from frontend.pyqt.app.login.login_view import LoginView
from frontend.pyqt.app.api_client.users_api_client import UsersApiClient
from frontend.pyqt.app.config.session_manager import SessionManager

class LoginController(QObject):
    def __init__(self, view: LoginView, parent=None):
        super().__init__(parent)
        self.view = view
        self.api_client = UsersApiClient(self)
        self.session = SessionManager()

        self.view.login_requested.connect(self.handle_login_requested)
        self.api_client.login_success.connect(self.on_login_success)
        self.api_client.login_error.connect(self.on_login_error)
        
        self.api_client.get_me_success.connect(self.on_get_me_success)
        self.api_client.get_me_error.connect(self.on_get_me_error)

    def handle_login_requested(self, email, password):
        self.api_client.login(email, password)

    def on_login_success(self, data: dict):
        token = data.get("access_token")
        if token:
            self.session.set_jwt(token)
            # Update base client's token manually so subsequent calls (like get_me) use it
            self.api_client.base_client.set_token(token)
            self.api_client.get_me()
        else:
            self.view.show_error("Invalid token received.")

    def on_login_error(self, error: str):
        self.view.show_error(error)

    def on_get_me_success(self, data: dict):
        self.session.set_language(data.get("language", "en_US"))
        self.view.accept()

    def on_get_me_error(self, error: str):
        self.view.show_error("Could not fetch user profile.")
