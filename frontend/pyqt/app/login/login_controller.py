from PyQt6.QtCore import QObject, pyqtSignal
from app.api_client.base_api_client_factory import get_base_client
from app.login.login_view import LoginView
from app.api_client.users_api_client import UsersApiClient
from app.config.session_manager import SessionManager
from app.models.generated_models import UserConfigPublic

class LoginController(QObject):
    is_admin_signal = pyqtSignal(bool)
    def __init__(self, view: LoginView, parent=None):
        super().__init__(parent)
        self.view = view
        base_client = get_base_client()
        self.api_client = UsersApiClient(base_client, self)
        self.session = SessionManager()

        self.view.login_requested.connect(self.handle_login_requested)
        self.api_client.login_success.connect(self.on_login_success)
        self.api_client.login_error.connect(self.on_login_error)
        
        self.api_client.get_user_config_success.connect(self.on_get_user_config_success)
        self.api_client.get_user_config_error.connect(self.on_get_user_config_error)

    def handle_login_requested(self, email, password):
        self.api_client.login(email, password)

    def on_login_success(self, data: dict):
        token = data.get("access_token")
        if token:
            self.session.set_jwt(token)
            # Update base client's token manually to subsequent calls
            self.api_client.base_client.set_token(token)
            self.api_client.get_user_config()
        else:
            self.view.show_error("Invalid token received.")

    def on_login_error(self, error: str):
        self.view.show_error(error)

    def on_get_user_config_success(self, user_config: UserConfigPublic):
        self.session.set_language(user_config.language)
        self.is_admin_signal.emit(user_config.is_admin)
        self.view.accept()

    def on_get_user_config_error(self, error: str):
        self.view.show_error("Could not fetch user config.")
