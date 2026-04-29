from typing import Optional

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtNetwork import QNetworkReply

from frontend.pyqt.app.api_client.base_api_client import BaseApiClient
from frontend.pyqt.app.config.urls import Endpoint, build_url
import frontend.pyqt.app.models.generated_models as generated_models

class AuthorsApiClient(QObject):
    """
    API Client for interacting with global Author endpoints.
    """

    get_authors_success = pyqtSignal(list)
    get_authors_error = pyqtSignal(str)

    def __init__(self, base_client: BaseApiClient, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.client = base_client

    def get_all_authors(self):
        """Fetches all authors in the application."""
        url = build_url(Endpoint.AUTHORS)
        reply = self.client.get(url)
        reply.finished.connect(lambda r=reply: self._on_get_all_authors_finished(r))

    def _on_get_all_authors_finished(self, reply: QNetworkReply):
        data = self.client.parse_reply(reply)
        if data is not None:
            try:
                authors = [generated_models.AuthorPublic(**item) for item in data]
                self.get_authors_success.emit(authors)
            except Exception as e:
                self.get_authors_error.emit(f"Data parsing error: {str(e)}")
        else:
            err = reply.errorString() if reply.errorString() else "Failed to fetch authors."
            self.get_authors_error.emit(err)
        reply.deleteLater()
