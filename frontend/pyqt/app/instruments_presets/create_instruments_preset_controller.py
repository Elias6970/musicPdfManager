

from PyQt6.QtWidgets import QMessageBox
from frontend.pyqt.app.api_client.base_api_client_factory import get_base_client
from frontend.pyqt.app.instruments_presets.instruments_preset_view import InstrumentsPresetView
from frontend.pyqt.app.api_client.instruments_presets_api_client import InstrumentsPresetsApiClient
from frontend.pyqt.app.api_client.instruments_names_api_client import InstrumentsNamesApiClient
from frontend.pyqt.app.models.generated_models import InstrumentsPreset, InstrumentConfig
from frontend.pyqt.app.pop_up_windows.error.error_window import ShowError

class CreateInstrumentsPresetController:
    def __init__(self, view: InstrumentsPresetView):
        self.view = view

        # View signals
        self.view.confirmed.connect(self._on_confirmed)
        self.view.cancelled.connect(self.view.reject)
        self.view.change_detected.connect(self._on_change_detected)

        # Names API Client signals
        self.names_api_client = InstrumentsNamesApiClient(get_base_client())
        self.names_api_client.get_shortcuts_and_instruments_success.connect(self._on_instruments_loaded)
        self.names_api_client.get_shortcuts_and_instruments_error.connect(self._on_instruments_error)

        # Presets API Client signals
        self.presets_api_client = InstrumentsPresetsApiClient(get_base_client())
        self.presets_api_client.preset_created.connect(self._on_preset_created)
        self.presets_api_client.preset_create_error.connect(self._on_preset_create_error)
        
        # Load available instrument names initially
        self.names_api_client.get_shortcuts_and_instruments()

    def _on_instruments_loaded(self, data: dict):
        """Called when the instruments map is successfully loaded."""
        # Typically the map has instrument names as values or keys. Using list of values/keys
        instruments = sorted(list(set(data.values()))) if isinstance(data, dict) else []
        self.view.set_instruments_options(instruments)
        self.view.add_emtpy_item() # Start with one empty item


    def _on_instruments_error(self, error: str):
        print(f"Error loading instruments: {error}")
        QMessageBox.critical(self.view, self.tr("Error"), self.tr(f"Could not load instrument names:\n{error}"))


    def _on_change_detected(self):
        """Called anytime an item inside the console combo boxes changes."""
        # If the last item is no longer empty, add a new row
        if self.view.items and not self.view.items[-1].is_empty():
            self.view.add_emtpy_item()


    def _on_confirmed(self):
        """Handle preset confirmation."""
        preset_name = self.view.get_name().strip()
        if not preset_name:
            ShowError.show_tooltip_error(self.view.preset_name, self.tr("Preset name cannot be empty."))
            return

        raw_data = self.view.get_data()
        instruments_payload:dict[str, InstrumentConfig] = {}

        for copies, instruments_selected in raw_data:
            if not instruments_selected:
                continue

            # Assuming the first instrument tuple is the primary, and the rest are "other_options"
            main_inst, main_num = instruments_selected[0]
            main_std = main_inst if not main_num else f"{main_inst}_{main_num}"

            other_options = []
            for inst, num in instruments_selected[1:]:
                opt_std = inst if not num else f"{inst}_{num}"
                other_options.append(opt_std)

            instruments_payload[main_std] = InstrumentConfig(
                copies=int(copies),
                other_options=other_options
            )

        if not instruments_payload:
            ShowError.show_tooltip_error(self.view.btn_confirm, self.tr("You must provide at least one instrument."))
            return

        preset_data = InstrumentsPreset(
            name=preset_name,
            instruments=instruments_payload
        )
        
        self.view.setEnabled(False) # Disable view while requesting
        self.presets_api_client.create_preset(preset_data)

    def _on_preset_created(self, response: dict):
        """Handle successful API creation."""
        QMessageBox.information(self.view, self.tr("Success"), self.tr("Preset created successfully!"))
        self.view.accept()

    def _on_preset_create_error(self, error: str):
        """Handle preset creation failure."""
        self.view.setEnabled(True)
        QMessageBox.critical(self.view, self.tr("Error"), self.tr(f"Failed to create preset:\n{error}"))
