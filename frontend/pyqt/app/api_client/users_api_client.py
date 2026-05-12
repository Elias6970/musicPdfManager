import json
from PyQt6.QtCore import QObject, pyqtSignal, QByteArray
from PyQt6.QtNetwork import QNetworkReply, QNetworkRequest
from app.api_client.base_api_client import BaseApiClient
from app.api_client.base_api_client_factory import get_base_client
from app.config.urls import build_url, Endpoint
from app.models.generated_models import UserConfigCreatePublic, UserConfigPublic, UserPublic, UserCreate

class UsersApiClient(QObject):
    login_success = pyqtSignal(dict)
    login_error = pyqtSignal(str)
    
    get_user_config_success = pyqtSignal(UserConfigPublic)
    get_user_config_error = pyqtSignal(str)

    get_all_users_success = pyqtSignal(list)
    get_all_users_error = pyqtSignal(str)

    register_success = pyqtSignal(UserPublic)
    register_error = pyqtSignal(str)

    update_user_success = pyqtSignal(UserPublic)
    update_user_error = pyqtSignal(str)

    update_user_config_success = pyqtSignal(UserConfigPublic)
    update_user_config_error = pyqtSignal(str)

    delete_user_success = pyqtSignal()
    delete_user_error = pyqtSignal(str)

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
        reply = self.base_client.manager.post(request, post_data)
        reply.finished.connect(lambda r=reply: self._handle_login_finished(r))

    def _handle_login_finished(self, reply: QNetworkReply):
        data = self.base_client.parse_reply(reply)
        if data is None:
            self.login_error.emit("Login failed")
        else:
            self.login_success.emit(data)
        reply.deleteLater()


    def get_user_config(self):
        url = build_url(Endpoint.USERS_CONFIG)
        reply = self.base_client.get(url)
        reply.finished.connect(lambda r=reply: self._handle_get_user_config_finished(r))

    def _handle_get_user_config_finished(self, reply: QNetworkReply):
        data = self.base_client.parse_reply(reply)
        if data is not None:
            try:
                user_config = UserConfigPublic(**data)
                self.get_user_config_success.emit(user_config)
            except Exception as e:
                self.get_user_config_error.emit(f"Data parsing error: {str(e)}")
        else:
            self.get_user_config_error.emit(reply.errorString())
        reply.deleteLater()


    def get_all_users(self):
        url = build_url(Endpoint.USERS)
        reply = self.base_client.get(url)
        reply.finished.connect(lambda r=reply: self._handle_get_all_users_finished(r))

    def _handle_get_all_users_finished(self, reply: QNetworkReply):
        """Handle the response for get_all_users. Emits a list of UserConfigPublic on success."""
        data = self.base_client.parse_reply(reply)
        if data is not None:
            list_of_users = [UserPublic(**user_data) for user_data in data]
            self.get_all_users_success.emit(list_of_users)
        else:
            self.get_all_users_error.emit(reply.errorString())
        reply.deleteLater()

    def register(self, user: UserCreate):
        url = build_url(Endpoint.USERS_REGISTER)
        reply = self.base_client.post(url, user)
        reply.finished.connect(lambda r=reply: self._handle_register_finished(r))

    def _handle_register_finished(self, reply: QNetworkReply):
        data = self.base_client.parse_reply(reply)
        if data is not None:
            try:
                user_public = UserPublic(**data)
                self.register_success.emit(user_public)
            except Exception as e:
                self.register_error.emit(f"Data parsing error: {str(e)}")
        else:
            self.register_error.emit(reply.errorString())
        reply.deleteLater()

    def update_user(self, user_id: int, user: UserCreate):
        url = build_url(Endpoint.USER_BY_ID, path_params={"user_id": user_id})
        reply = self.base_client.put(url, user)
        reply.finished.connect(lambda r=reply: self._handle_update_user_finished(r))

    def _handle_update_user_finished(self, reply: QNetworkReply):
        data = self.base_client.parse_reply(reply)
        if data is not None:
            try:
                user_public = UserPublic(**data)
                self.update_user_success.emit(user_public)
            except Exception as e:
                self.update_user_error.emit(f"Data parsing error: {str(e)}")
        else:
            self.update_user_error.emit(reply.errorString())
        reply.deleteLater()

    def delete_user(self, user_id: int):
        url = build_url(Endpoint.USER_BY_ID, path_params={"user_id": user_id})
        reply = self.base_client.delete(url)
        reply.finished.connect(lambda r=reply: self._handle_delete_user_finished(r))

    def _handle_delete_user_finished(self, reply: QNetworkReply):
        if reply.error() == QNetworkReply.NetworkError.NoError:
            self.delete_user_success.emit()
        else:
            self.delete_user_error.emit(reply.errorString())
        reply.deleteLater()

    def update_user_config(self, user_config: UserConfigCreatePublic):
        """Update the current user's configuration.
        
        Args:
            user_config (UserConfigCreatePublic): The user configuration data to update
        """
        url = build_url(Endpoint.USERS_CONFIG)
        reply = self.base_client.put(url, user_config)
        reply.finished.connect(lambda r=reply: self._handle_update_user_config_finished(r))

    def _handle_update_user_config_finished(self, reply: QNetworkReply):
        """Handle the response for update_user_config."""
        data = self.base_client.parse_reply(reply)
        if data is not None:
            try:
                user_config = UserConfigPublic(**data)
                self.update_user_config_success.emit(user_config)
            except Exception as e:
                self.update_user_config_error.emit(f"Data parsing error: {str(e)}")
        else:
            self.update_user_config_error.emit(reply.errorString())
        reply.deleteLater()
