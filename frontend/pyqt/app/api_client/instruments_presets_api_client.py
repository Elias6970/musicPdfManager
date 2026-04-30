from typing import Optional

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtNetwork import QNetworkReply, QNetworkRequest

from frontend.pyqt.app.api_client.base_api_client import BaseApiClient
from frontend.pyqt.app.config.urls import Endpoint, build_url
from frontend.pyqt.app.models.generated_models import InstrumentsPreset


class InstrumentsPresetsApiClient(QObject):
    """
    API Client for interacting with Instrument Presets endpoints.
    """

    presets_names_loaded = pyqtSignal(list)
    presets_names_error = pyqtSignal(str)

    presets_loaded = pyqtSignal(list)
    presets_error = pyqtSignal(str)

    preset_created = pyqtSignal(InstrumentsPreset)
    preset_create_error = pyqtSignal(str)

    preset_updated = pyqtSignal(InstrumentsPreset)
    preset_update_error = pyqtSignal(str)
    preset_name_already_exists_error = pyqtSignal(str)

    preset_loaded_single = pyqtSignal(InstrumentsPreset)
    preset_load_error = pyqtSignal(str)

    preset_deleted = pyqtSignal(str)
    preset_delete_error = pyqtSignal(str)

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

    def create_preset(self, preset_data):
        """
        Initiates a network request to create a new instrument preset.
        """
        url = build_url(Endpoint.INSTRUMENT_PRESETS)
        reply = self.client.post(url, data=preset_data)
        reply.finished.connect(lambda r=reply: self._on_create_preset_finished(r))

    def _on_create_preset_finished(self, reply: QNetworkReply):
        status_code = reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute)
        data = self.client.parse_reply(reply)

        # BaseApiClient parse_reply returns parsed dict or empty dict on 204 or None on error
        if data is not None:
            preset = InstrumentsPreset(**data)  # Validate data format
            self.preset_created.emit(preset)
        else:
            if status_code == 400:
                self.preset_name_already_exists_error.emit("A preset with this name already exists")
            elif reply.error() != QNetworkReply.NetworkError.NoError:
                # Basic error handling
                msg = reply.errorString()
                # You might parse the server's error message from reply.readAll() if BaseApiClient doesn't, but here's a default
                self.preset_create_error.emit(msg if msg else "Failed to create preset.")

        reply.deleteLater()

    def get_preset(self, preset_name: str):
        """
        Initiates a network request to fetch a specific instrument preset.
        """
        url = build_url(Endpoint.INSTRUMENT_PRESET_BY_NAME, path_params={"preset_name": preset_name})
        reply = self.client.get(url)
        reply.finished.connect(lambda r=reply: self._on_get_preset_finished(r))

    def _on_get_preset_finished(self, reply: QNetworkReply):
        data = self.client.parse_reply(reply)
        if data is not None:
            preset = InstrumentsPreset(**data)  # Validate data format
            self.preset_loaded_single.emit(preset)
        else:
            msg = reply.errorString()
            self.preset_load_error.emit(msg if msg else "Failed to load preset.")

        reply.deleteLater()

    def update_preset(self, preset_name: str, preset_data):
        """
        Initiates a network request to update an existing instrument preset.
        """
        url = build_url(Endpoint.INSTRUMENT_PRESET_BY_NAME, path_params={"preset_name": preset_name})
        reply = self.client.put(url, data=preset_data)
        reply.finished.connect(lambda r=reply: self._on_update_preset_finished(r))

    def _on_update_preset_finished(self, reply: QNetworkReply):
        status_code = reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute)
        data = self.client.parse_reply(reply)
        if data is not None:
            updated = InstrumentsPreset(**data)  # Validate data format
            self.preset_updated.emit(updated)
        else:
            if status_code == 400:
                # The backend returns HTTP_400_BAD_REQUEST when the PresetAlreadyExistsError is caught
                self.preset_name_already_exists_error.emit("A preset with this name already exists")
            elif reply.error() != QNetworkReply.NetworkError.NoError:
                msg = reply.errorString()
                self.preset_update_error.emit(msg if msg else "Failed to update preset.")

        reply.deleteLater()

    def get_all_presets(self):
        """
        Initiates a network request to fetch all instrument presets.
        """
        url = build_url(Endpoint.INSTRUMENT_PRESETS)
        reply = self.client.get(url)
        reply.finished.connect(lambda r=reply: self._on_get_all_presets_finished(r))
        
    def _on_get_all_presets_finished(self, reply: QNetworkReply):
        data = self.client.parse_reply(reply)

        if data is not None:
            from frontend.pyqt.app.models.generated_models import InstrumentsPreset
            res = []
            if isinstance(data, list):
                for item in data:
                    try:
                        res.append(InstrumentsPreset(**item))
                    except Exception as e:
                        pass
                self.presets_loaded.emit(res)
            else:
                self.presets_error.emit("Unexpected data format returned for presets.")
        else:
            if reply.error() != QNetworkReply.NetworkError.NoError:
                self.presets_error.emit("Failed to load presets.")

        reply.deleteLater()

    def delete_preset(self, preset_name: str):
        """
        Initiates a network request to delete an instrument preset.
        """
        url = build_url(Endpoint.INSTRUMENT_PRESET_BY_NAME, path_params={"preset_name": preset_name})
        reply = self.client.delete(url)
        reply.finished.connect(lambda r=reply, n=preset_name: self._on_delete_preset_finished(r, n))

    def _on_delete_preset_finished(self, reply: QNetworkReply, preset_name: str):
        # We expect 204 No Content for a successful deletion
        if reply.error() == QNetworkReply.NetworkError.NoError:
            self.preset_deleted.emit(preset_name)
        else:
            msg = reply.errorString()
            self.preset_delete_error.emit(msg if msg else "Failed to delete preset.")

        reply.deleteLater()
