from typing import Optional

from PyQt6.QtCore import QObject, pyqtSignal, QByteArray
from PyQt6.QtNetwork import QNetworkReply, QNetworkRequest

from frontend.pyqt.app.api_client.base_api_client import BaseApiClient
from frontend.pyqt.app.config.urls import Endpoint, build_url
import frontend.pyqt.app.models.generated_models as generated_models


class PrintersApiClient(QObject):
    """
    API Client for interacting with Printer endpoints.
    """

    # Emitted when simple print succeeds with PDF bytes
    simple_print_success = pyqtSignal(QByteArray)
    # Emitted when simple print fails
    simple_print_error = pyqtSignal(str)

    def __init__(self, base_client: BaseApiClient, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.client = base_client

    def generate_simple_print(self, print_job: generated_models.SimplePrintJob):
        """
        Initiates a POST request to generate a combined PDF for simple print job.
        """
        url = build_url(Endpoint.SIMPLE_PRINTER)
        reply = self.client.post(url, data=print_job)
        reply.finished.connect(lambda r=reply: self._on_simple_print_finished(r))

    def _on_simple_print_finished(self, reply: QNetworkReply):
        """
        Callback handler when the simple print request finishes.
        """
        error = reply.error()
        if error == QNetworkReply.NetworkError.NoError:
            raw_data = reply.readAll()
            self.simple_print_success.emit(raw_data)
        else:
            # Emit error with details if possible
            status_code = reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute)
            error_msg = reply.errorString()
            try:
                error_body = reply.readAll().data().decode('utf-8')
                self.simple_print_error.emit(f"HTTP {status_code}: {error_msg} - {error_body}")
            except Exception:
                self.simple_print_error.emit(f"HTTP {status_code}: {error_msg}")

        reply.deleteLater()
