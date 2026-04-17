from typing import Optional

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtNetwork import QNetworkReply

from frontend.pyqt.app.api_client.base_api_client import BaseApiClient
from frontend.pyqt.app.config.urls import Endpoint, build_url
from frontend.pyqt.app.models.generated_models import PiecesPresetCreate

class PiecesPresetsApiClient(QObject):
    """
    API Client for interacting with Pieces Presets endpoints.
    """

    presets_loaded = pyqtSignal(list)
    presets_error = pyqtSignal(str)

    presets_names_loaded = pyqtSignal(list)
    presets_names_error = pyqtSignal(str)

    preset_created = pyqtSignal(object)
    preset_create_error = pyqtSignal(str)

    def __init__(self, base_client: BaseApiClient, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.client = base_client

    def get_all_presets(self):
        """
        Initiates a network request to fetch all pieces presets.
        """
        url = build_url(Endpoint.PIECE_PRESETS)
        reply = self.client.get(url)
        reply.finished.connect(lambda r=reply: self._on_get_presets_finished(r))

    def _on_get_presets_finished(self, reply: QNetworkReply):
        """
        Callback handler when the presets fetch request finishes.
        """
        data = self.client.parse_reply(reply)

        if data is not None:
            if isinstance(data, list):
                self.presets_loaded.emit(data)
            else:
                self.presets_error.emit("Unexpected data format returned for presets.")
        else:
            if reply.error() != QNetworkReply.NetworkError.NoError:
                self.presets_error.emit("Failed to load presets.")

        reply.deleteLater()

    def get_preset_names(self):
        """
        Initiates a network request to fetch all pieces preset names.
        """
        url = build_url(Endpoint.PIECE_PRESETS_NAMES)
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

    def create_preset(self, preset: PiecesPresetCreate):
        """
        Initiates a network request to create a new pieces preset.
        """
        url = build_url(Endpoint.PIECE_PRESETS)
        reply = self.client.post(url, data=preset)
        reply.finished.connect(lambda r=reply: self._on_create_preset_finished(r))

    def _on_create_preset_finished(self, reply: QNetworkReply):
        """
        Callback handler when the create preset request finishes.
        """
        data = self.client.parse_reply(reply)

        if data is not None:
            if isinstance(data, dict):
                self.preset_created.emit(data)
            else:
                self.preset_create_error.emit("Unexpected data format returned after creating preset.")
        else:
            if reply.error() != QNetworkReply.NetworkError.NoError:
                error_msg = reply.errorString()
                # Attempt to get detail from server response if available
                raw_data = reply.readAll().data()
                if raw_data:
                    try:
                        import json
                        json_err = json.loads(raw_data.decode('utf-8'))
                        if "detail" in json_err:
                            error_msg = json_err["detail"]
                    except:
                        pass
                self.preset_create_error.emit(f"Failed to create preset: {error_msg}")

        reply.deleteLater()
