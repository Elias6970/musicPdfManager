from typing import Optional

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtNetwork import QNetworkReply

from app.api_client.base_api_client import BaseApiClient
from app.config.urls import Endpoint, build_url
import app.models.generated_models as generated_models

class TypesApiClient(QObject):
    """
    API Client for interacting with global Type endpoints.
    """

    get_types_success = pyqtSignal(list)
    get_types_error = pyqtSignal(str)

    def __init__(self, base_client: BaseApiClient, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.client = base_client

    def get_all_types(self):
        """Fetches all types in the application."""
        url = build_url(Endpoint.TYPES)
        reply = self.client.get(url)
        reply.finished.connect(lambda r=reply: self._on_get_all_types_finished(r))

    def _on_get_all_types_finished(self, reply: QNetworkReply):
        data = self.client.parse_reply(reply)
        if data is not None:
            try:
                types = [generated_models.TypePublic(**item) for item in data]
                self.get_types_success.emit(types)
            except Exception as e:
                self.get_types_error.emit(f"Data parsing error: {str(e)}")
        else:
            err = reply.errorString() if reply.errorString() else "Failed to fetch types."
            self.get_types_error.emit(err)
        reply.deleteLater()
