from typing import Optional

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtNetwork import QNetworkReply

from frontend.pyqt.app.api_client.base_api_client import BaseApiClient
from frontend.pyqt.app.config.urls import Endpoint, build_url
import urllib.parse

class PreviewApiClient(QObject):
    """
    API Client for handling document previews via QNetworkAccessManager.
    Replaces the old requests-based QThread worker.
    """

    # Emits (page_num, image_bytes, total_pages)
    preview_loaded = pyqtSignal(str, str, bytes, int, int)
    preview_error = pyqtSignal(str)

    def __init__(self, base_client: BaseApiClient, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.client = base_client
        self._current_reply: Optional[QNetworkReply] = None

    def fetch_preview(
        self,
        archive_id: int,
        piece_std_name: str,
        file: str,
        page_number: int,
        dpi: int = 150,
        abort_previous: bool = True
    ) -> None:
        """
        Initiates a network request to fetch the preview image bytes.
        If a previous request is still running, it is aborted to prevent race conditions.
        """
        # Cancel any pending preview fetch
        if abort_previous:
            self.abort_current_request()

        # Build URL with query params
        url = build_url(
            Endpoint.PREVIEW,
            query_params={
                "archive_id": archive_id,
                "piece_std_name": piece_std_name,
                "file": file,
                "page_number": page_number,
                "dpi": dpi,
            },
        )

        # Start the GET request
        self._current_reply = self.client.get(url)

        # Connect the finished signal to our handler, injecting page_number
        self._current_reply.finished.connect(
            lambda r=self._current_reply: self._on_fetch_finished(r)
        )

    def abort_current_request(self) -> None:
        """Aborts the currently running request if it exists."""
        if self._current_reply and self._current_reply.isRunning():
            self._current_reply.abort()
        self._current_reply = None

    def _on_fetch_finished(self, reply: QNetworkReply) -> None:
        # Clear the reference since it's finished
        if self._current_reply == reply:
            self._current_reply = None

        error_code = reply.error()

        # If the request was deliberately aborted by quick page clicking, ignore silently
        if error_code == QNetworkReply.NetworkError.OperationCanceledError:
            reply.deleteLater()
            return

        if error_code == QNetworkReply.NetworkError.NoError:
            # We don't use parse_reply here because the content is raw image bytes, not JSON
            img_bytes = reply.readAll().data()
            
            #Headers
            piece_std_name = urllib.parse.unquote(reply.rawHeader(b"X-Piece_Std-Name").data().decode())
            file_name = urllib.parse.unquote(reply.rawHeader(b"X-File-Name").data().decode())
            page_number = int(reply.rawHeader(b"X-Page-Number")) if reply.rawHeader(b"X-Page-Number") else 0
            total_pages = int(reply.rawHeader(b"X-Total-Pages")) if reply.rawHeader(b"X-Total-Pages") else 1
            
            self.preview_loaded.emit(piece_std_name, file_name,
                                     img_bytes, page_number, total_pages)
        else:
            if error_code == QNetworkReply.NetworkError.AuthenticationRequiredError:
                self.preview_error.emit("Unauthorized access. Please log in again.")
            else:
                self.preview_error.emit(f"HTTP Error: {reply.errorString()}")

        reply.deleteLater()
