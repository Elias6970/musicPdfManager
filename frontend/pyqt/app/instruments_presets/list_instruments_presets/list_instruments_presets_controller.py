from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QObject

from frontend.pyqt.app.api_client.base_api_client_factory import get_base_client
from frontend.pyqt.app.api_client.instruments_presets_api_client import InstrumentsPresetsApiClient
from frontend.pyqt.app.models.generated_models import InstrumentsPreset
from frontend.pyqt.app.instruments_presets.list_instruments_presets.list_instruments_presets_view import ListInstrumentsPresetsView
from frontend.pyqt.app.instruments_presets.instruments_preset_view import InstrumentsPresetView
from frontend.pyqt.app.instruments_presets.create_instruments_preset_controller import CreateInstrumentsPresetController

class ListInstrumentsPresetsController(QObject):
    def __init__(self, view: ListInstrumentsPresetsView):
        super().__init__()
        self.view = view
        self.presets: list[InstrumentsPreset] = []

        self.api_client = InstrumentsPresetsApiClient(get_base_client())
        
        # Connect view signals
        self.view.add_signal.connect(self._on_add_signal)
        self.view.delete_item_signal.connect(self._on_delete_item_signal)
        self.view.edit_item_signal.connect(self._on_edit_item_signal)

        # Connect API client signals
        self.api_client.presets_loaded.connect(self._on_presets_loaded)
        self.api_client.presets_error.connect(self._on_presets_error)
        self.api_client.preset_deleted.connect(self._on_preset_deleted)
        self.api_client.preset_delete_error.connect(self._on_preset_delete_error)

        # Load data initially
        self._load_presets()

    def _load_presets(self):
        self.view.setEnabled(False)
        self.api_client.get_all_presets()

    def _on_presets_loaded(self, presets: list[InstrumentsPreset]):
        self.view.setEnabled(True)
        self.presets = presets
        self._populate_view()

    def _on_presets_error(self, error: str):
        self.view.setEnabled(True)
        QMessageBox.critical(self.view, self.tr("Error"), self.tr(f"Could not load presets:\n{error}"))

    def _populate_view(self):
        self.view.status_console.clear()
        for preset in self.presets:
            # We add instrument summary as tooltip
            tooltip = self.tr(f"Preset: {preset.instruments}")
            self.view.add_item(preset.name, tooltip)

    def _on_add_signal(self):
        create_view = InstrumentsPresetView(self.tr("Create New Preset"), parent=self.view)
        create_controller = CreateInstrumentsPresetController(create_view)
        
        if create_view.exec():
            # If accepted, refresh the list
            self._load_presets()

    def _on_delete_item_signal(self, preset_name: str):
        # Check if the preset name exists in the list
        preset_exists = any(p.name == preset_name for p in self.presets)
        if not preset_exists:
            QMessageBox.warning(self.view, self.tr("Warning"), self.tr(f"Preset '{preset_name}' not found."))
            return

        reply = QMessageBox.question(
            self.view,
            self.tr("Confirm Deletion"),
            self.tr(f"Are you sure you want to delete the preset '{preset_name}'?"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.view.setEnabled(False)
            self.api_client.delete_preset(preset_name)

    def _on_preset_deleted(self, preset_name: str):
        self.view.setEnabled(True)
        self._load_presets()

    def _on_preset_delete_error(self, error: str):
        self.view.setEnabled(True)
        QMessageBox.critical(self.view, self.tr("Error"), self.tr(f"Could not delete preset:\n{error}"))

    def _on_edit_item_signal(self, preset_name: str):
        # TODO: Implement edit button logic in the future
        pass
