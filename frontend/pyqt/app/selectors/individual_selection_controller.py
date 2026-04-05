from PyQt6 import QtCore
from PyQt6.QtCore import QObject
from frontend.pyqt.app.elements.score_search_bar import ScoreSearchBarIdentifiers
from frontend.pyqt.app.error import PageNotFoundError
from frontend.pyqt.app.selectors.individual_selection_view import IndividualSelectionView
import frontend.pyqt.app.models.generated_models as generated_models
from uuid import uuid4

class PrinteableFile(generated_models.PrinteableFile):
    id:int = None

class IndividualSelectionController(QObject):    
    def __init__(self,view:IndividualSelectionView):
        super().__init__()
        self.view = view

        self.job:generated_models.SimplePrintJob = generated_models.SimplePrintJob(files=[])
        self.selected_piece:str = None
        self.selected_instrument:str = None
        self.selected_page:int = 0
        self.pieces:list[str] = [] #List of pieces std names.

        # Connect signals
        self.view.add_score_signal.connect(self.add_score)
        self.view.generate_pdf_signal.connect(self.generate_pdf)

        self.view.piece_search_bar.textChanged.connect(self.set_option_of_instruments)
        self.view.instrument_changed.connect(self.instrument_changed)
        self.view.refresh_requested.connect(self.refresh)

    def generate_pdf(self):
        """
        Generate the PDF with the added scores.
        """
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
        self.view.add_item_to_scroll(piece.id, piece_name, instrument, copies, self.remove_score)


    def remove_score(self, id:str):
        """
        Remove the score from the list of added scores.
        The widget it is removed in the StatusConsoleItemWithTwoTexts class.
        """
        self.job.files = [file for file in self.job.files if file.id != id]
    
    
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
    

    def instrument_changed(self,instrument:str):
        """
        Set the selected instrument to add to the PDF.
        """
        self.selected_instrument = instrument
        self.selected_page = 0
        self.update_preview()


    def update_preview(self):
        img = None #TODO: get the bytes of the image from the api
        #Can raise page not found
        self.view.change_preview_img(None) 
        self.check_mv_btns_enableability()


    #Move to the previous preview page 
    def mv_back_preview(self):
        try:
            self.selected_page -= 1
            self.update_preview()
        except PageNotFoundError:
            self.selected_page += 1
            self.view.disable_mv_back_preview_btn()


    #Move to the next preview page
    def mv_forward_preview(self):
        try:
            self.selected_page += 1
            self.update_preview()
        except PageNotFoundError:
            self.selected_page -= 1
            self.view.disable_mv_forward_preview_btn()

    #Check if move preview buttons must be enabled or disabled
    def check_mv_btns_enableability(self):
        if self.preview_controller.is_in_first_page():
            self.btn_mv_back_preview.setEnabled(False)
        else:
            self.btn_mv_back_preview.setEnabled(True)
        if self.preview_controller.is_in_last_page():
            self.btn_mv_forward_preview.setEnabled(False)
        else:
            self.btn_mv_forward_preview.setEnabled(True)

    def refresh(self):
        self.view.refresh()
        #TODO: get pieces from api
        self.pieces = ["PIEZA 1","PIEZA 2","PIEZA 3"]
        self.view.update_search_bar_autocompleter(self.pieces)