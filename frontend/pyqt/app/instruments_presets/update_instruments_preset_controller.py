from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QObject
from app.api_client.base_api_client_factory import get_base_client
from app.instruments_presets.instruments_preset_view import InstrumentsPresetView
from app.api_client.instruments_presets_api_client import InstrumentsPresetsApiClient
from app.api_client.instruments_names_api_client import InstrumentsNamesApiClient
from app.models.generated_models import InstrumentsPreset, InstrumentConfig
from app.pop_up_windows.error.error_window import ShowError

class UpdateInstrumentsPresetController(QObject):
    def __init__(self, view: InstrumentsPresetView, preset_name: str):
        super().__init__()
        self.view = view
        self.original_preset_name = preset_name
        self.preset_data: InstrumentsPreset | None = None

        # View signals
        self.view.confirmed.connect(self._on_confirmed)
        self.view.cancelled.connect(self.view.reject)
        self.view.change_detected.connect(self._on_change_detected)

        # Names API Client signals
        self.names_api_client = InstrumentsNamesApiClient(get_base_client())
        self.names_api_client.get_instruments_success.connect(self._on_instruments_loaded)
        self.names_api_client.get_instruments_error.connect(self._on_instruments_error)

        # Presets API Client signals
        self.presets_api_client = InstrumentsPresetsApiClient(get_base_client())
        self.presets_api_client.preset_loaded_single.connect(self._on_preset_loaded)
        self.presets_api_client.preset_load_error.connect(self._on_preset_load_error)
        self.presets_api_client.preset_updated.connect(self._on_preset_updated)
        self.presets_api_client.preset_update_error.connect(self._on_preset_update_error)
        self.presets_api_client.preset_name_already_exists_error.connect(self._on_preset_already_exists)
        
        self.view.setEnabled(False) # Disable view until data is loaded
        
        self.view.preset_name.setText(self.original_preset_name)

        # Start loading data
        self.names_api_client.get_instruments()

    def _on_instruments_loaded(self, data: list[str]):
        """Called when the instruments map is successfully loaded."""
        self.view.set_instruments_options(data)
        
        # Now fetch the preset data to edit
        self.presets_api_client.get_preset(self.original_preset_name)

    def _on_instruments_error(self, error: str):
        QMessageBox.critical(self.view, self.tr("Error"), self.tr(f"Could not load instrument names:\n{error}"))

    def _on_preset_loaded(self, preset: InstrumentsPreset):
        self.preset_data = preset
        self._populate_view()

    def _on_preset_load_error(self, error: str):
        QMessageBox.critical(self.view, self.tr("Error"), self.tr(f"Could not load preset '{self.original_preset_name}':\n{error}"))

    def _parse_std_instrument(self, std_name: str) -> tuple[str, str]:
        """
        Parse a standardized instrument name like 'Violin_2' into instrument and number
        Returns:
            Returns a tuple of (instrument, number) by parsing a standardized instrument name.
            If the instrument doesn't have number, the number returned is ''
        ."""
        parts = std_name.rsplit("_", 1)
        if len(parts) == 2 and parts[1].isdigit():
            return parts[0], parts[1]
        return std_name, ""

    def _populate_view(self):
        """Fill the view with the loaded preset data."""
        preset = self.preset_data
        
        if preset and preset.instruments:
            for main_std, config in preset.instruments.items():
                preset_instruments = []
                
                # Add main instrument
                preset_instruments.append(self._parse_std_instrument(main_std))
                
                # Add other options
                for opt_std in config.other_options:
                    preset_instruments.append(self._parse_std_instrument(opt_std))
                
                self.view.add_item(preset_instruments, config.copies, add_empty_at_end=True)

        
        self.view.add_emtpy_item() # Add a trailing empty InfiniteComboBoxesItem row
        self.view.setEnabled(True)

    def _on_change_detected(self):
        """Called anytime an item inside the console combo boxes changes."""
        # If the last item is no longer empty, add a new row
        if self.view.items and not self.view.items[-1].is_empty():
            self.view.add_emtpy_item()

    def _on_confirmed(self):
        """Handle preset confirmation."""
        preset_name = self.view.get_name().strip()
        if not preset_name:
            ShowError.show_tooltip_error(self.tr("Preset name cannot be empty."), 5000, self.view.preset_name)
            return

        raw_data = self.view.get_data()
        instruments_payload: dict[str, InstrumentConfig] = {}

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
            ShowError.show_tooltip_error(self.tr("You must provide at least one instrument."), 5000, self.view.btn_confirm)
            return

        updated_preset = InstrumentsPreset(
            name=preset_name,
            instruments=instruments_payload
        )
        
        self.view.setEnabled(False) # Disable view while requesting
        self.presets_api_client.update_preset(self.original_preset_name, updated_preset)

    def _on_preset_updated(self, response: InstrumentsPreset):
        """Handle successful API update."""
        QMessageBox.information(self.view, self.tr("Success"), self.tr("Preset updated successfully!"))
        self.view.accept()

    def _on_preset_update_error(self, error: str):
        """Handle preset update failure."""
        self.view.setEnabled(True)
        QMessageBox.critical(self.view, self.tr("Error"), self.tr(f"Failed to update preset:\n{error}"))

    def _on_preset_already_exists(self, error_msg: str):
        """Handle when the preset already exists."""
        self.view.setEnabled(True)
        ShowError.show_tooltip_error(self.tr("A preset with this name already exists."), 5000, self.view.preset_name)
