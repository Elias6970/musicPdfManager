from typing import Optional

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtNetwork import QNetworkReply

from frontend.pyqt.app.api_client.base_api_client import BaseApiClient
from frontend.pyqt.app.config.urls import Endpoint, build_url


class InstrumentsPresetsApiClient(QObject):
    """
    API Client for interacting with Instrument Presets endpoints.
    """

    presets_names_loaded = pyqtSignal(list)
    presets_names_error = pyqtSignal(str)

    def __init__(self, base_client: BaseApiClient, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.client = base_client

    def get_preset_names(self):
        """
        Initiates a network request to fetch all instrument preset names.
        """
        url = build_url(Endpoint.INSTRUMENT_PRESETS_NAMES)
        reply = self.client.get(url)
        reply.finished.connect(lambda r=reply: self._on_get_preset_names_finished(r))

    def _on_get_preset_names_finished(self, reply: QNetworkReply):
        """
        Callback handler when the preset names fetch request finishes.
        """
        data = self.client.parse_reply(reply)

        if data is not None:
            if isinstance(data, list):
                self.presets_names_loaded.emit(data)
            else:
                self.presets_names_error.emit("Unexpected data format returned for preset names.")
        else:
            if reply.error() != QNetworkReply.NetworkError.NoError:
                self.presets_names_error.emit("Failed to load preset names.")

        reply.deleteLater()
