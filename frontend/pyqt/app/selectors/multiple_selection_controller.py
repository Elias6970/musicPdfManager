from uuid import uuid4

from PyQt6.QtCore import QObject
from frontend.pyqt.app.api_client.base_api_client_factory import get_base_client
from frontend.pyqt.app.api_client.pieces_api_client import PiecesApiClient
from frontend.pyqt.app.api_client.preview_api_client import PreviewApiClient
from frontend.pyqt.app.api_client.instruments_presets_api_client import InstrumentsPresetsApiClient
from frontend.pyqt.app.config.session_manager import SessionManager
from frontend.pyqt.app.elements.previwer.previewer_controller import PreviewerController
from frontend.pyqt.app.selectors.multiple_selection_view import MultipleSelectionView
from frontend.pyqt.app.models.generated_models import PresetPrintJobPublic, PresetPrintJobConfig, ExportStrategyType, PiecePublic, PrinteablePiece

class PrinteablePieceWithId(PrinteablePiece):
    """
    Created to be able to delete the pieces from the list of added pieces in the PDF generation, 
    because the PrinteablePiece model doesn't have an id, so it is extended to have it and be able to identify it in the list.   
    The id is generated with uuid4 when a piece is added to the list.
    """
    id:str

class MultipleSelectionController(QObject):
    def __init__(self, view:MultipleSelectionView):
        super().__init__()
        self.view = view
        self.session = SessionManager()
        base_client = get_base_client()
        base_client.set_token(self.session.get_jwt())

        self.pieces_api = PiecesApiClient(base_client)
        self.preview_api = PreviewApiClient(base_client)
        self.instruments_presets_api = InstrumentsPresetsApiClient(base_client)

        self.preview_controller = PreviewerController(self.view.preview, self.preview_api)

        
        self.added_pieces: list[PrinteablePieceWithId] = [] #List of pieces added to the PDF with their id to be able to delete them from the list.
        self.pieces: list[PiecePublic] = [] #List of pieces public objects.
        self.selected_piece: str | None = None
        self.presets: list[str] = [] #List of preset names.
        self.selected_preset: str | None = None
        
        # Connect pieces api signals
        self.pieces_api.pieces_loaded.connect(self._on_pieces_fetched)
        self.pieces_api.pieces_error.connect(lambda err: print(f"Error fetching pieces: {err}")) #TODO: Show a window
        
        self.pieces_api.piece_scores_loaded.connect(self._on_scores_fetched)
        self.pieces_api.piece_scores_error.connect(lambda err: print(f"Error fetching scores: {err}")) #TODO: Show a window

        self.instruments_presets_api.presets_names_loaded.connect(self._on_presets_names_loaded)
        self.instruments_presets_api.presets_names_error.connect(lambda err: print(f"Error fetching presets: {err}"))

        # Connect view signals
        self.view.piece_search_bar.textChanged.connect(self.set_option_of_instruments)
        self.view.only_digitalized_changed.connect(self.get_pieces)
        self.view.instrument_changed.connect(self.instrument_changed)
        self.view.add_piece_signal.connect(self.add_piece)
        self.view.preset_changed.connect(self.preset_changed)
        self.view.refresh_requested.connect(self.refresh)


        #Set presets in combo box
        self.get_presets()

    def get_presets(self):
        """
        Trigger an API request to get the array of preset names.
        """
        self.instruments_presets_api.get_preset_names()

    def launch_exporting_configuration_window(self):
        

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


    def get_pieces(self):
        """
        Trigger an API request to get the pieces for the current archive.
        The result is handled via signal _on_pieces_fetched.
        """
        archive_id = self.session.get_archive_id()
        self.pieces_api.get_pieces(archive_id=archive_id)


    def preset_changed(self, preset_name:str):
        """
        Set the selected preset to add to the PDF.
        """
        self.selected_preset = preset_name

    
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

    
    def _on_scores_fetched(self, scores: list[str]):
        """
        Slot connected to piece_scores_loaded emitted by pieces_api.
        Updates the combo box or disables it if empty.
        """
        if scores:
            self.view.set_combo_box_instruments(scores)
        else:    
            self.view.disable_instruments_combo_box_no_scores()
    

    def _on_presets_names_loaded(self, presets: list[str]):
        """
        Slot connected to presets_names_loaded emitted by instruments_presets_api.
        Updates the combo box with the presets names or disables it if empty.
        """
        self.presets = presets
        if presets:
            self.view.set_combo_box_presets(presets)
        else:    
            self.view.disable_presets_combo_box_no_presets()

    def refresh(self):
        """
        Refresh the view to the initial state.
        """
        self.added_pieces = []
        self.selected_piece = None
        self.selected_instrument = None
        #self.view.refresh()

        self.get_pieces()
        self.get_presets()
