from PyQt6.QtCore import QObject, pyqtSignal

from app.api_client.base_api_client import BaseApiClient
from app.api_client.users_api_client import UsersApiClient
from app.config.session_manager import SessionManager
from app.models.generated_models import UserConfigPublic


class StartupAuthChecker(QObject):
    authenticated = pyqtSignal(UserConfigPublic)
    authentication_required = pyqtSignal(str)

    def __init__(
        self,
        base_client: BaseApiClient,
        session: SessionManager,
        parent: QObject | None = None,
    ):
        super().__init__(parent)
        self.session = session
        self.api_client = UsersApiClient(base_client, self)
        self._check_in_progress = False

        self.api_client.get_user_config_success.connect(self._on_success)
        self.api_client.get_user_config_error.connect(self._on_error)
        base_client.unauthorized.connect(self._on_unauthorized)

    def check(self) -> bool:
        if not self.session.is_logged_in():
            return False

        self._check_in_progress = True
        self.api_client.get_user_config()
        return True

    def _on_success(self, user_config: UserConfigPublic):
        if not self._check_in_progress:
            return

        self._check_in_progress = False
        self.authenticated.emit(user_config)

    def _on_error(self, error: str):
        if not self._check_in_progress:
            return

        self._check_in_progress = False
        self.authentication_required.emit(error)

    def _on_unauthorized(self):
        if not self._check_in_progress:
            return

        self._check_in_progress = False
        self.session.clear_session()
        self.authentication_required.emit(
            "Your session has expired. Please log in again."
        )
