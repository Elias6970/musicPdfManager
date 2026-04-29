

from typing import Optional

from frontend.pyqt.app.api_client.base_api_client import BaseApiClient
from frontend.pyqt.app.models.generated_models import RolePublic, RoleCreate
from frontend.pyqt.app.config.urls import Endpoint, build_url
from PyQt6.QtCore import pyqtSignal, QObject
from PyQt6.QtNetwork import QNetworkReply

class RolesApiClient(QObject):
    get_roles_success = pyqtSignal(list)
    get_roles_error = pyqtSignal(str)

    def __init__(self, base_client: BaseApiClient, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.client = base_client


    def get_roles(self):
        """GET /roles/"""
        url = build_url(Endpoint.ROLES)
        reply = self.client.get(url)
        reply.finished.connect(lambda r=reply: self._on_get_roles_finished(r))


    def _on_get_roles_finished(self, reply:QNetworkReply):
        """Handle the response for get_roles."""
        data = self.client.parse_reply(reply)
        if data is not None:
            roles = [RolePublic(**role_data) for role_data in data]
            self.get_roles_success.emit(roles)
        else:
            self.get_roles_error.emit(reply.errorString())
        reply.deleteLater()