from uuid import uuid4
from PyQt6 import QtWidgets
from PyQt6.QtCore import QObject, QByteArray, pyqtSignal
from frontend.pyqt.app.api_client.base_api_client_factory import get_base_client
from frontend.pyqt.app.api_client.pieces_api_client import PiecesApiClient
from frontend.pyqt.app.api_client.pieces_presets_api_client import PiecesPresetsApiClient
from frontend.pyqt.app.api_client.preview_api_client import PreviewApiClient
from frontend.pyqt.app.api_client.instruments_presets_api_client import InstrumentsPresetsApiClient
from frontend.pyqt.app.api_client.printers_api_client import PrintersApiClient
from frontend.pyqt.app.config.session_manager import SessionManager
from frontend.pyqt.app.elements.previwer.previewer_controller import PreviewerController
from frontend.pyqt.app.pop_up_windows.resolve_unmached_presets.resolve_unmatched_presets_controller import ResolveUnmatchedPresetsController
from frontend.pyqt.app.pop_up_windows.resolve_unmached_presets.resolve_unmatched_presets_view import  ResolveUnmatchedPresetsView, ResolveUnmatchedPresetsView
from frontend.pyqt.app.pop_up_windows.type_of_export.type_of_export_controller import TypeOfExportController
from frontend.pyqt.app.pop_up_windows.type_of_export.type_of_export_view import TypeOfExportView
from frontend.pyqt.app.selectors.multiple_selection_view import MultipleSelectionView
from frontend.pyqt.app.models.generated_models import PiecesPresetCreate, PresetPrintJobPublic, PresetPrintJobConfig, PiecePublic, PrinteablePiece, PiecesPreset
from frontend.pyqt.app.pop_up_windows.error.error_window import ShowError
import zipfile, io, os

class PrinteablePieceWithId(PrinteablePiece):
    """
    Created to be able to delete the pieces from the list of added pieces in the PDF generation, 
    because the PrinteablePiece model doesn't have an id, so it is extended to have it and be able to identify it in the list.   
    The id is generated with uuid4 when a piece is added to the list.
    """
    id:str

class MultipleSelectionController(QObject):
    update_pieces_presets_menu_list = pyqtSignal(list)

    @property
    def FOLDER_EXPORTING_NAME(self) -> str:
        from datetime import datetime
        return f"export_{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}"
        
    def __init__(self, view:MultipleSelectionView):
        super().__init__()
        self.view = view
        self.session = SessionManager()
        base_client = get_base_client()
        base_client.set_token(self.session.get_jwt())

        self.pieces_api = PiecesApiClient(base_client)
        self.preview_api = PreviewApiClient(base_client)
        self.instruments_presets_api = InstrumentsPresetsApiClient(base_client)
        self.pieces_presets_api = PiecesPresetsApiClient(base_client)
        self.printing_api = PrintersApiClient(base_client)
        
        self.preview_controller = PreviewerController(self.view.preview, self.preview_api)
        # Connect preview controller signals to view buttons
        self.view.btn_mv_back_preview.clicked.connect(self.preview_controller.previous_page)
        self.view.btn_mv_forward_preview.clicked.connect(self.preview_controller.next_page)
        
        self.preview_controller.enable_previous.connect(self.view.btn_mv_back_preview.setEnabled)
        self.preview_controller.enable_next.connect(self.view.btn_mv_forward_preview.setEnabled)


        self.type_of_export_window = TypeOfExportView()
        self.type_of_export_controller = TypeOfExportController(self.type_of_export_window)
        self.type_of_export_controller.export_signal.connect(self.export)
        
        self.resolve_unmatched_presets_view = ResolveUnmatchedPresetsView()
        self.resolve_unmatched_presets_controller = ResolveUnmatchedPresetsController(self.resolve_unmatched_presets_view)
        self.resolve_unmatched_presets_controller.resolved_signal.connect(self.handle_resolved_unmatched_presets)

        self.added_pieces: list[PrinteablePieceWithId] = [] #List of pieces added to the PDF with their id to be able to delete them from the list.
        self.pieces: list[PiecePublic] = [] #List of pieces public objects.
        self.selected_piece: str | None = None
        self.instruments_preset: list[str] = [] #List of preset names.
        self.pieces_presets: list[PiecesPreset] = [] #List of pieces presets objects.
        self.selected_instruments_preset: str | None = None
        self.solved_fails: dict[str, dict[str, str]] = {}
        self.last_config_export: PresetPrintJobConfig | None = None

        self._preset_to_load: str | None = None
        self._pending_preset_loads: set[str] = set()

        # Connect pieces api signals
        self.pieces_api.pieces_loaded.connect(self._on_pieces_fetched)
        self.pieces_api.pieces_error.connect(lambda err: print(f"Error fetching pieces: {err}")) #TODO: Show a window
        
        self.pieces_api.piece_scores_loaded.connect(self._on_scores_fetched)
        self.pieces_api.piece_scores_error.connect(lambda err: print(f"Error fetching scores: {err}")) #TODO: Show a window

        self.instruments_presets_api.presets_names_loaded.connect(self._on_instruments_presets_names_loaded)
        self.instruments_presets_api.presets_names_error.connect(lambda err: print(f"Error fetching presets: {err}"))
        
        self.pieces_presets_api.presets_loaded.connect(self._on_pieces_presets_fetched)
        self.pieces_presets_api.presets_error.connect(lambda err: print(f"Error fetching pieces presets: {err}"))
        self.pieces_presets_api.preset_created.connect(self._on_pieces_preset_saved_success)
        self.pieces_presets_api.preset_create_error.connect(lambda err: print(f"Error creating preset: {err}"))
        self.pieces_presets_api.presets_names_loaded.connect(self.update_pieces_presets_menu_list.emit) #To update the pieces presets names in the menu when a new preset is created

        self.printing_api.preset_print_success.connect(self._on_exportation_success)
        self.printing_api.preset_print_unresolved.connect(self._on_exportation_unresolved)

        # Connect view signals
        self.view.piece_search_bar.textChanged.connect(self.set_option_of_instruments)
        self.view.only_digitalized_changed.connect(self.get_pieces)
        self.view.instrument_changed.connect(self.instrument_changed)
        self.view.add_piece_signal.connect(self.add_piece)
        self.view.generate_pdf_signal.connect(self.launch_exporting_configuration_window)
        self.view.instruments_preset_changed.connect(self.instruments_preset_changed)
        self.view.refresh_requested.connect(self.refresh)
        self.view.save_pieces_preset_signal.connect(self._save_pieces_preset)


    def export(self, config: PresetPrintJobConfig):
        """Export the PDF with the selected pieces, preset and configuration."""
        if not self.selected_instruments_preset:
            ShowError.show_tooltip_error(self.tr("You need to select a preset"),5000,self.view.presets_combo_box)
            return
        
        if len(self.added_pieces) == 0:
            ShowError.show_tooltip_error(self.tr("You need to add at least one piece"),5000,self.view.piece_search_bar)
            return

        preset_print_job = PresetPrintJobPublic(
            preset_name=self.selected_instruments_preset,
            archive_id=self.session.get_archive_id(),
            pieces=[PrinteablePiece(std_name=piece.std_name, copies=piece.copies) for piece in self.added_pieces],
            config=config,
            solved_fails=self.solved_fails
        )
        self.last_config_export = config

        self.printing_api.generate_preset_print(preset_print_job)
    
    
    def add_piece(self, piece_name:str, preset_name:str, copies:int):
        """
        Add a piece to the list of pieces to be printed, with the preset and copies information.
        """
        piece = PrinteablePieceWithId(std_name = piece_name, copies=copies, id=str(uuid4()))
        self.added_pieces.append(piece)

        self.view.add_item_to_status_console(
            piece.id,
            piece_name,
            preset_name,
            copies,
            self.remove_piece
        )
        self.view.btn_create_pdf.setEnabled(True)
        self.view.presets_combo_box.setEnabled(False)


    def remove_piece(self, id:str):
        """
        Remove the piece from the list of added pieces.
        The widget it is removed in the StatusConsoleItemWithTwoTexts class.
        """
        self.added_pieces = [piece for piece in self.added_pieces if piece.id != id]
        if len(self.added_pieces) == 0:
            self.view.btn_create_pdf.setEnabled(False)
            self.view.presets_combo_box.setEnabled(True)


    def get_instruments_presets_names(self):
        """
        Trigger an API request to get the array of preset instruments names.
        """
        self.instruments_presets_api.get_preset_names()


    def get_pieces_presets_names(self):
        """
        Trigger an API request to get the array of pieces presets names.
        The result is handled via signal _on_pieces_presets_names_fetched.
        """
        self.pieces_presets_api.get_preset_names()


    def get_pieces_presets(self):
        """
        Trigger an API request to get the array of pieces presets.
        """
        self.pieces_presets_api.get_all_presets()


    def get_pieces(self):
        """
        Trigger an API request to get the pieces for the current archive.
        The result is handled via signal _on_pieces_fetched.
        """
        archive_id = self.session.get_archive_id()
        self.pieces_api.get_pieces(archive_id=archive_id)


    def launch_exporting_configuration_window(self):
        self.type_of_export_controller.show()


    def instruments_preset_changed(self, preset_name:str):
        """
        Set the selected preset to add to the PDF.
        """
        self.selected_instruments_preset = preset_name
        
        if self.selected_piece:
            self.view.btn_add_piece.setEnabled(True)

    
    def instrument_changed(self,instrument:str):
        """
        Set the selected instrument to add to the PDF.
        """
        self.selected_instrument = instrument
        if self.selected_piece and self.selected_instrument: #To avoid removing the image when the user is typing another piece
            self.preview_controller.load_document(archive_id=self.session.get_archive_id(), piece_std_name=self.selected_piece, file=instrument)


    def set_option_of_instruments(self,piece_name:str):
        """
        Set the options of the instruments combo box according to the piece selected in the search bar.
        If the piece doesn't have scores, it disables the combo box
        """
        # Validate string exists by ensuring it's in our cached self.pieces names
        valid_names = [piece.std_name for piece in self.pieces]
        
        if piece_name != self.selected_piece and piece_name in valid_names:
            self.selected_piece = piece_name
            self.view.set_piece_lbl(piece_name)

            archive_id = self.session.get_archive_id()
            self.pieces_api.get_piece_scores(archive_id=archive_id, piece_std_name=piece_name)
        else:
            self.selected_piece = None    
            self.view.set_piece_lbl("")
            self.view.clean_instruments_combo_box()
   
    
    def load_pieces_preset(self, preset_name:str):
        self._preset_to_load = preset_name
        self._pending_preset_loads = {"pieces", "instruments_presets", "pieces_presets"}
        self.refresh() #To clear the current state and fetch resources

    
    def _check_pending_preset_load(self, loaded_resource: str):
        """
        Check if the loaded resource is one of the pending preset loads, and if so, remove it from the pending list. 
        If there are no more pending loads, apply the preset load logic.
        """
        if not self._preset_to_load or loaded_resource not in self._pending_preset_loads:
            return
        
        self._pending_preset_loads.discard(loaded_resource)
        
        if not self._pending_preset_loads:
            self._apply_preset_load_logic(self._preset_to_load)


    def _apply_preset_load_logic(self, preset_name: str):
        """
        Apply the load of the preset with the given name, setting the selected preset and adding the pieces to the PDF according to the preset configuration.
        """
        preset = next((preset for preset in self.pieces_presets if preset.name == preset_name), None)
        if not preset:
            QtWidgets.QMessageBox.warning(self.view, self.tr("Error"), self.tr("Preset not found"))
            self._preset_to_load = None
            return
        
        self.selected_instruments_preset = preset.instruments_preset_name
        self.view.set_instrument_preset_in_combo_box(preset.instruments_preset_name)
        for piece in preset.pieces:
            self.add_piece(piece.std_name, preset.instruments_preset_name, piece.copies or 1)
        self._preset_to_load = None


    def _on_pieces_fetched(self, pieces: list[PiecePublic]):
        """
        Slot called when the piece data finishes loading from API.
        """
        self.pieces = pieces
        
        # Depending on checkbox, update names in autocompleter
        only_digitalized = self.view.is_only_digitalized()
        
        if only_digitalized:
            names = [piece.std_name for piece in self.pieces if piece.digitalized]
        else:
            names = [piece.std_name for piece in self.pieces]

        self.view.update_search_bar_autocompleter(names)
        self._check_pending_preset_load("pieces")

    
    def _on_scores_fetched(self, scores: list[str]):
        """
        Slot connected to piece_scores_loaded emitted by pieces_api.
        Updates the combo box or disables it if empty.
        """
        if scores:
            self.view.set_combo_box_instruments(scores)
        else:    
            self.view.disable_instruments_combo_box_no_scores()
    

    def _on_instruments_presets_names_loaded(self, presets: list[str]):
        """
        Slot connected to presets_names_loaded emitted by instruments_presets_api.
        Updates the combo box with the presets names or disables it if empty.
        """
        self.instruments_preset = presets
        if presets:
            self.view.set_combo_box_presets(presets)
        else:    
            self.view.disable_presets_combo_box_no_presets()
        self._check_pending_preset_load("instruments_presets")

    def _on_pieces_presets_fetched(self, presets: list[dict]):
        """
        Slot connected to presets_loaded emitted by pieces_presets_api.
        It receives the list of pieces and save them in the controller.
        """
        try:
            self.pieces_presets = [PiecesPreset(**preset) for preset in presets]
        except Exception as e:
            print(f"Error parsing pieces presets: {e}")
            self.pieces_presets = []
        self._check_pending_preset_load("pieces_presets")

    def _on_exportation_success(self, data:QByteArray):
        """
        Slot connected to preset_print_success emitted by printing_api.
        It receives the ZIP bytes and should trigger the download of the file.
        It also handles one pdf file.
        """
        self.save_path = self.view.dialog_window_select_exporting_path()
        if not self.save_path:
            return
        #Create the folder
        self.save_path = os.path.join(self.save_path, self.FOLDER_EXPORTING_NAME)
        os.makedirs(self.save_path, exist_ok=True)

        byte_data = data.data()

        try:
            with zipfile.ZipFile(io.BytesIO(byte_data)) as zip_ref:
                zip_ref.extractall(self.save_path)
        except zipfile.BadZipFile:
            # Fallback if it's a PDF (ExportStrategyType.ALL_IN_ONE)
            pdf_path = os.path.join(self.save_path, self.FOLDER_EXPORTING_NAME + ".pdf")
            with open(pdf_path, "wb") as f:
                f.write(byte_data)

        self.view.show_message(self.tr("Export successful!"), self.tr(f"Files saved to {self.save_path}"))

    def _on_exportation_unresolved(self, unresolved: list[dict]):
        """
        Slot connected to preset_print_unresolved emitted by printing_api.
        Handles the case when the exportation fails and the user need to
        manually solve the unresolved instruments.
        """
        try:
            unresolved_items = []
            for i in unresolved:
                #We ignore archive_id because it is not needed in the frontend, and it is always the same for all the items because they belong to the same preset print job.
                unresolved_items.append((i["piece_std_name"], i["missing_instrument"], i["options"]))
        
            self.resolve_unmatched_presets_controller.set_unresolved_instruments(unresolved_items)
            self.resolve_unmatched_presets_controller.show()

        except Exception as e:
            print(f"Error parsing unresolved instruments: {e}")

    def handle_resolved_unmatched_presets(self, resolved: list[tuple[str,str,str]]):
        """
        Slot connected to resolved_signal emitted by resolve_unmatched_presets_controller.
        It receives the list of resolved instruments and updates the solved_fails attribute with the resolution, then it triggers the exportation again with the new resolution.
        """
        if self.solved_fails is None:
            self.solved_fails = {}
            
        for i in resolved:
            if i[0] not in self.solved_fails:
                self.solved_fails[i[0]] = {}
            self.solved_fails[i[0]][i[1]] = i[2]
        
        if self.last_config_export is not None:
            self.export(self.last_config_export) #In theory last_config_export is not None because the user can't see the window to resolve unmatched presets if they haven't tried to export before.

    def _on_pieces_preset_saved_success(self, preset: dict):
        """
        Slot connected to preset_created emitted by pieces_presets_api.
        It receives the saved preset and updates the view.
        """
        self.view.show_message(self.tr("Preset saved successfully!"), self.tr(f"Preset saved: {preset['name']}"))

    def refresh(self):
        """
        Refresh the view to the initial state.
        """
        self.added_pieces = []
        self.selected_piece = None
        self.selected_instrument = None
        self.selected_instruments_preset = None
        self.solved_fails = {}
        
        self.preview_controller.clear()
        self.view.refresh()

        self.get_pieces()
        self.get_instruments_presets_names()
        self.get_pieces_presets()
        self.get_pieces_presets_names()


    def save_pieces_preset(self):
        """
        Trigger the saving of a pieces preset with the current added pieces.
        """
        self.view.show_get_piece_preset_name()

    def _save_pieces_preset(self, pieces_preset_name:str):
        """
        Trigger an API request to save a pieces preset with the current added pieces and the given name.
        """
        if not pieces_preset_name:
            QtWidgets.QMessageBox.warning(self.view, self.tr("Error"), self.tr("Preset name cannot be empty"))
            return
        
        if len(self.added_pieces) == 0:
            QtWidgets.QMessageBox.warning(self.view, self.tr("Error"), self.tr("You need to add at least one piece to save a preset"))
            return

        if not self.selected_instruments_preset:
            QtWidgets.QMessageBox.warning(self.view, self.tr("Error"), self.tr("You need to select an instruments preset to save a pieces preset"))
            return

        pieces=[PrinteablePiece(std_name=piece.std_name, copies=piece.copies or 1) for piece in self.added_pieces]
        preset = PiecesPresetCreate(name = pieces_preset_name, instruments_preset_name=self.selected_instruments_preset, pieces=pieces)
        self.pieces_presets_api.create_preset(preset)
    

        