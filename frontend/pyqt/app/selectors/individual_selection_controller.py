from frontend.pyqt.app.api_client.base_api_client_factory import get_base_client
from frontend.pyqt.app.api_client.preview_api_client import PreviewApiClient
from frontend.pyqt.app.api_client.pieces_api_client import PiecesApiClient
from frontend.pyqt.app.api_client.printers_api_client import PrintersApiClient
from frontend.pyqt.app.config.session_manager import SessionManager
from frontend.pyqt.app.elements.previwer.previewer_controller import PreviewerController
from PyQt6.QtCore import QObject
from frontend.pyqt.app.selectors.individual_selection_view import IndividualSelectionView
import frontend.pyqt.app.models.generated_models as generated_models
from uuid import uuid4

class PrinteableFile(generated_models.PrinteableFile):
    """
    Created to be able to delete the scores from the list of added scores in the PDF generation, 
    because the PrinteableFile model doesn't have an id, so it is extended to have it and be able to identify it in the list.   
    The id is generated with uuid4 when a score is added to the list.
    """
    id:str

class IndividualSelectionController(QObject):    
    def __init__(self,view:IndividualSelectionView):
        super().__init__()
        self.view = view
        self.session = SessionManager()
        base_client = get_base_client()
        base_client.set_token(self.session.get_jwt())

        self.preview_api = PreviewApiClient(base_client)
        self.pieces_api = PiecesApiClient(base_client)
        self.printers_api = PrintersApiClient(base_client)
        
        self.preview_controller = PreviewerController(self.view.preview, self.preview_api)

        self.job:generated_models.SimplePrintJob = generated_models.SimplePrintJob(files=[])
        self.selected_piece:str|None = None
        self.selected_instrument:str|None = None
        self.pieces:list[generated_models.PiecePublic] = [] #List of pieces public objects.

        # Connect pieces api signals
        self.pieces_api.pieces_loaded.connect(self._on_pieces_fetched)
        self.pieces_api.pieces_error.connect(lambda err: print(f"Error fetching pieces: {err}")) #TODO: Show a window
        
        self.pieces_api.piece_scores_loaded.connect(self._on_scores_fetched)
        self.pieces_api.piece_scores_error.connect(lambda err: print(f"Error fetching scores: {err}"))

        self.printers_api.simple_print_success.connect(self._on_pdf_generated)
        self.printers_api.simple_print_error.connect(lambda err: print(f"Error generating PDF: {err}")) #TODO: Show a window
        
        # Connect signals
        self.view.add_score_signal.connect(self.add_score)
        self.view.generate_pdf_signal.connect(self.generate_pdf)

        self.view.piece_search_bar.textChanged.connect(self.set_option_of_instruments)
        self.view.instrument_changed.connect(self.instrument_changed)
        self.view.refresh_requested.connect(self.refresh)
        self.view.only_digitalized_changed.connect(self.get_pieces)
        
        # Connect preview controller signals to view buttons
        self.view.btn_mv_back_preview.clicked.connect(self.preview_controller.previous_page)
        self.view.btn_mv_forward_preview.clicked.connect(self.preview_controller.next_page)
        
        self.preview_controller.enable_previous.connect(self.view.btn_mv_back_preview.setEnabled)
        self.preview_controller.enable_next.connect(self.view.btn_mv_forward_preview.setEnabled)

    def generate_pdf(self):
        """
        Generate the PDF with the added scores.
        """
        if not self.job.files or len(self.job.files) == 0:
            print("No scores added to generate PDF.")
            return
        
        #Get file path to save
        self.save_path = self.view.dialog_window_select_new_pdf()
        if self.save_path == "": 
            return 
        
        exportable_list = [generated_models.PrinteableFile(
            archive_id=file.archive_id,
            piece_std_name=file.piece_std_name,
            file_name=file.file_name,
            copies=file.copies
        ) for file in self.job.files] # Convert to PrinteableFile without id for the API
  
        print_job = generated_models.SimplePrintJob(files=exportable_list)
        self.printers_api.generate_simple_print(print_job)

    def _on_pdf_generated(self, pdf_bytes):
        """
        Slot called when the simple print PDF generator succeeds.
        Saves the PDF bytes to the path selected.
        """
        if hasattr(self, 'save_path') and self.save_path:
            try:
                with open(self.save_path, "wb") as f:
                    f.write(pdf_bytes.data())
                print(f"PDF successfully saved to {self.save_path}")
                self.view.show_pdf_saved_message(f"PDF successfully saved to {self.save_path}")
            except Exception as e:
                print(f"Error saving PDF to disk: {e}")
        

    def add_score(self, piece_name:str, instrument:str, copies:int):
        """
        Add the score to the list of added scores and to the scroll area in the view.
        """
        piece = PrinteableFile(
            id=str(uuid4()),  # Generate a unique ID for each file
            archive_id=self.session.get_archive_id(),
            piece_std_name=piece_name,
            file_name=instrument,
            copies=copies)
        self.job.files.append(piece)
        print(f"Added score: Piece: {piece_name}, Instrument: {instrument}, Copies: {copies}")
        self.view.add_item_to_scroll(piece.id, piece_name, instrument, copies, self.remove_score)
        self.view.btn_create_pdf.setEnabled(True)

    def remove_score(self, id:str):
        """
        Remove the score from the list of added scores.
        The widget it is removed in the StatusConsoleItemWithTwoTexts class.
        """
        self.job.files = [file for file in self.job.files if file.id != id] #type: ignore -> Because always is appended a Modified PrinteableFile with the id, so it is never None.
        if not self.job.files:
            self.view.btn_create_pdf.setEnabled(False)
    
    
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
            
    def _on_scores_fetched(self, scores: list[str]):
        """
        Slot connected to piece_scores_loaded emitted by pieces_api.
        Updates the combo box or disables it if empty.
        """
        if scores:
            self.view.set_combo_box_instruments(scores)
        else:    
            self.view.disable_instruments_combo_box_no_scores()
    

    def instrument_changed(self,instrument:str):
        """
        Set the selected instrument to add to the PDF.
        """
        self.selected_instrument = instrument
        if self.selected_piece and self.selected_instrument: #To avoid removing the image when the user is typing another piece
            self.preview_controller.load_document(archive_id=self.session.get_archive_id(), piece_std_name=self.selected_piece, file=instrument)

    def get_pieces(self):
        """
        Trigger an API request to get the pieces for the current archive.
        The result is handled via signal _on_pieces_fetched.
        """
        archive_id = self.session.get_archive_id()
        self.pieces_api.get_pieces(archive_id=archive_id)
        
    def _on_pieces_fetched(self, pieces: list[generated_models.PiecePublic]):
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


    def refresh(self):
        self.pieces = []
        self.job = generated_models.SimplePrintJob(files=[])
        self.selected_piece = None
        self.selected_instrument = None

        self.preview_controller.clear()
        self.view.refresh()

        self.get_pieces()
