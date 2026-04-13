from typing import Callable, Optional

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtNetwork import QNetworkReply

from frontend.pyqt.app.api_client.base_client import BaseApiClient
from frontend.pyqt.app.config.urls import Endpoint, build_url


class PreviewApiClient(QObject):
    """
    API Client for handling document previews via QNetworkAccessManager.
    Replaces the old requests-based QThread worker.
    """

    # Emits (page_num, image_bytes, total_pages)
    preview_loaded = pyqtSignal(int, bytes, int)
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
    ) -> None:
        """
        Initiates a network request to fetch the preview image bytes.
        If a previous request is still running, it is aborted to prevent race conditions.
        """
        # Cancel any pending preview fetch
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
            lambda r=self._current_reply, p=page_number: self._on_fetch_finished(r, p)
        )

    def abort_current_request(self) -> None:
        """Aborts the currently running request if it exists."""
        if self._current_reply and self._current_reply.isRunning():
            self._current_reply.abort()
        self._current_reply = None

    def _on_fetch_finished(self, reply: QNetworkReply, page_num: int) -> None:
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
            
            # The FastAPI backend returns total pages in a custom header
            total_pages_bytes = reply.rawHeader(b"X-Total-Pages")
            total_pages = int(total_pages_bytes) if total_pages_bytes else 1
            
            self.preview_loaded.emit(page_num, img_bytes, total_pages)
        else:
            if error_code == QNetworkReply.NetworkError.AuthenticationRequiredError:
                self.preview_error.emit("Unauthorized access. Please log in again.")
            else:
                self.preview_error.emit(f"HTTP Error: {reply.errorString()}")

        reply.deleteLater()
