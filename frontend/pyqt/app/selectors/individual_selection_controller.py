from frontend.pyqt.app.elements.previwer.previewer_controller import PreviewerController
from PyQt6.QtCore import QObject
from frontend.pyqt.app.selectors.individual_selection_view import IndividualSelectionView
import frontend.pyqt.app.models.generated_models as generated_models
from uuid import uuid4

class PrinteableFile(generated_models.PrinteableFile):
    id:str

class IndividualSelectionController(QObject):    
    def __init__(self,view:IndividualSelectionView):
        super().__init__()
        self.view = view
        self.preview_controller = PreviewerController(self.view.preview)

        self.job:generated_models.SimplePrintJob = generated_models.SimplePrintJob(files=[])
        self.selected_piece:str|None = None
        self.selected_instrument:str|None = None
        self.pieces:list[str] = [] #List of pieces std names.

        # Connect signals
        self.view.add_score_signal.connect(self.add_score)
        self.view.generate_pdf_signal.connect(self.generate_pdf)

        self.view.piece_search_bar.textChanged.connect(self.set_option_of_instruments)
        self.view.instrument_changed.connect(self.instrument_changed)
        self.view.refresh_requested.connect(self.refresh)
        self.view.only_digitalized_changed.connect(self.update_pieces_list)
        
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
        path = self.view.dialog_window_select_new_pdf()
        if path == "": 
            return 
        
        exportable_list = [generated_models.PrinteableFile(
            archive_id=file.archive_id,
            piece_std_name=file.piece_std_name,
            file_name=file.file_name,
            copies=file.copies
        ) for file in self.job.files]

        #TODO: Call the API to generate the PDF with the exportable_list and the options selected in the view.
        print("Generating PDF with the following scores:")
        for file in exportable_list:
            print(f"Piece: {file.piece_std_name}, Instrument: {file.file_name}, Copies: {file.copies}")
        

    def add_score(self, piece_name:str, instrument:str, copies:int):
        """
        Add the score to the list of added scores and to the scroll area in the view.
        """
        piece = PrinteableFile(
            id=str(uuid4()),  # Generate a unique ID for each file
            archive_id=0,  # TODO: Get the archive id from the SessionManager
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
        if piece_name != self.selected_piece and piece_name in self.pieces:
            self.selected_piece = piece_name
            self.view.set_piece_lbl(piece_name)

            #TODO:Get the scores from the api.
            scores = ["OPCION 1","OPCION 2"]
            if scores:
                self.view.set_combo_box_instruments(scores)
            else:    
                self.view.disable_instruments_combo_box_no_scores()
        else:
            self.selected_piece = None    
            self.view.set_piece_lbl("")
            self.view.clean_instruments_combo_box()
    

    def instrument_changed(self,instrument:str):
        """
        Set the selected instrument to add to the PDF.
        """
        self.selected_instrument = instrument
        # TODO: Get archive id from the sessionmanager'
        if self.selected_piece and self.selected_instrument: #To avoid removing the image when the user is typing another piece
            self.preview_controller.load_document(archive_id=0, piece_std_name=self.selected_piece, file=instrument)

    def get_pieces(self, digitalized:bool=False):
        """
        Get the pieces from the API and update the autocompleter of the search bar.
        """
        if digitalized:
            return ["PIEZA DIGITAL 1", "PIEZA DIGITAL 2"]
        return ["PIEZA 1","PIEZA 2","PIEZA 3", "PIEZA DIGITAL 1", "PIEZA DIGITAL 2"]

    def update_pieces_list(self, only_digitalized: bool):
        """
        Updates the internal pieces list and the autocompleter according to the checkbox.
        """
        self.pieces = self.get_pieces(digitalized=only_digitalized)
        self.view.update_search_bar_autocompleter(self.pieces)

    def refresh(self):
        self.view.refresh()
        # Initial piece load
        self.update_pieces_list(self.view.is_only_digitalized())