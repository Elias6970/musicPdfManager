

from app.api_client.base_api_client_factory import get_base_client
from app.config.session_manager import SessionManager
from app.score_classifier.piece_selector.piece_selector_view import PieceSelectorView
from app.api_client.pieces_api_client import PiecesApiClient
from app.score_classifier.score_classifier_view import ScoreClassifierView
from app.score_classifier.score_classifier_controller import ScoreClassifierController
from app.models.generated_models import PiecePublic
from PyQt6 import QtWidgets, QtCore

class PieceSelectorController(QtCore.QObject):
    def __init__(self, view: PieceSelectorView,) -> None:
        super().__init__()
        self.view = view
        self.session = SessionManager()
        
        self.archive_id = self.session.get_archive_id()
        self.pieces:list[str] = []
        self.added_pieces:list[tuple[str, str]] = [] #[(id, piece_std_name)]
        self.current_classifying_index: int = 0

        self.view.add_piece_signal.connect(self.add_piece)
        self.view.classify_signal.connect(self.classify)

        self.pieces_api_client = PiecesApiClient(get_base_client())
        self.pieces_api_client.pieces_loaded.connect(self._on_pieces_names_fetched)
        self.pieces_api_client.pieces_error.connect(lambda err: print(f"Error fetching pieces: {err}")) #TODO: Show a window
        self.pieces_api_client.piece_scores_and_page_counts_loaded.connect(self._on_piece_scores_and_page_counts_loaded)
        self.pieces_api_client.piece_scores_and_page_counts_error.connect(lambda err: print(f"Error fetching piece scores and page counts: {err}")) #TODO: Show a window

        self.get_pieces()

    
    def remove_piece_from_list(self, id:str):
        """
        Remove a piece from the list of pieces to classify. 
        The view call this function but already had deleted the item from the view
        """
        for i in self.added_pieces:
            if i[1] == id:
                self.added_pieces.remove(i)
                break
    
    def add_piece(self, piece:str):
        """Add a piece to the list of pieces to classify"""
        if piece in self.pieces:
            for i in self.added_pieces:
                if i[1] == piece:
                    return #Already added
            id = self.pieces.index(piece)
            self.added_pieces.append((str(id), piece))
            self.view.add_item(piece, str(id), self.remove_piece_from_list)
            self.view.search_bar.setText("")

    def classify(self):
        """Classify the next piece in the list of added pieces. It fetches the scores and page counts of the piece and opens the ScoreClassifierView to classify it."""
        if self.current_classifying_index >= len(self.added_pieces):
            QtWidgets.QMessageBox.information(self.view, self.view.tr("Info"), self.view.tr("No more pieces to classify."))
            self.view.accept()
            return
        
        _, piece_std_name = self.added_pieces[self.current_classifying_index]
        self.pieces_api_client.get_piece_scores_and_page_counts(self.archive_id, piece_std_name)



    def _on_piece_scores_and_page_counts_loaded(self, archive_id: int, piece_std_name: str, scores_and_page_counts: list):
        """Handle the successful fetching of piece scores and page counts by opening the ScoreClassifierView to classify the piece."""
        if self.added_pieces[self.current_classifying_index][1] != piece_std_name:
            return
        
        view = ScoreClassifierView()
        controller = ScoreClassifierController(view, piece_std_name, scores_and_page_counts)
        result = view.exec()

        if result == QtWidgets.QDialog.DialogCode.Accepted:
            self.current_classifying_index += 1
            self.classify()
        else:
            self.view.reject()
        
    def get_pieces(self):
        """Fetch the list of pieces from the backend and update the search bar autocompleter."""
        self.pieces_api_client.get_pieces(self.archive_id)
        print("Fetching pieces...")

    def _on_pieces_names_fetched(self, pieces:list[PiecePublic]):
        """Handle the successful fetching of pieces by updating the search bar autocompleter and storing the pieces in the controller."""
        print("Pieces fetched successfully.")
        self.pieces = [piece.std_name for piece in pieces]
        self.view.update_search_bar_autocompleter(self.pieces)