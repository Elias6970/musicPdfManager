import json
from PyQt6.QtCore import QObject, pyqtSignal, QByteArray
from PyQt6.QtNetwork import QNetworkRequest
from frontend.pyqt.app.api_client.base_api_client import BaseApiClient
from frontend.pyqt.app.api_client.base_api_client_factory import get_base_client
from frontend.pyqt.app.config.urls import build_url, Endpoint
from frontend.pyqt.app.models.generated_models import UserConfigPublic

class UsersApiClient(QObject):
    login_success = pyqtSignal(dict)
    login_error = pyqtSignal(str)
    
    get_user_config_success = pyqtSignal(UserConfigPublic)
    get_user_config_error = pyqtSignal(str)

    def __init__(self, base_client:BaseApiClient, parent=None):
        super().__init__(parent)
        self.base_client = base_client
        # Ensure we connect errors from base client just in case needed

    def login(self, email: str, password: str):
        url = build_url(Endpoint.USERS_LOGIN)
        
        # login expects form data (OAuth2PasswordRequestForm)
        post_data = QByteArray()
        post_data.append(f"username={email}&password={password}".encode('utf-8'))
        
        request = self.base_client._create_request(url)
        # OAuth2PasswordRequestForm requires application/x-www-form-urlencoded
        request.setHeader(
            QNetworkRequest.KnownHeaders.ContentTypeHeader, 
            "application/x-www-form-urlencoded"
        )
        # Avoid using self.base_client.post since it overrides ContentType to json
        self._login_reply = self.base_client.manager.post(request, post_data)
        self._login_reply.finished.connect(self._handle_login_finished)

    def _handle_login_finished(self):
        data = self.base_client.parse_reply(self._login_reply)
        if data is None:
            self.login_error.emit("Login failed")
        else:
            self.login_success.emit(data)
        self._login_reply.deleteLater()

    def get_user_config(self):
        url = build_url(Endpoint.USERS_CONFIG)
        self._get_user_config_reply = self.base_client.get(url)
        self._get_user_config_reply.finished.connect(self._handle_get_user_config_finished)

    def _handle_get_user_config_finished(self):
        data = self.base_client.parse_reply(self._get_user_config_reply)
        if data is None:
            self.get_user_config_error.emit("Could not fetch user config")
        else:
            self.get_user_config_success.emit(UserConfigPublic.model_validate(data))
        self._get_user_config_reply.deleteLater()
