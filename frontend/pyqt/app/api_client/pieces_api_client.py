from typing import Optional

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtNetwork import QNetworkReply

from frontend.pyqt.app.api_client.base_api_client import BaseApiClient
from frontend.pyqt.app.config.urls import Endpoint, build_url
import frontend.pyqt.app.models.generated_models as generated_models


class PiecesApiClient(QObject):
    """
    API Client for interacting with Piece endpoints.
    """

    # Emits the list of parsed pieces
    pieces_loaded = pyqtSignal(list)
    pieces_error = pyqtSignal(str)

    # Emits a list of score strings (filenames like 'bombo.pdf') a piece has
    piece_scores_loaded = pyqtSignal(list)
    piece_scores_error = pyqtSignal(str)

    def __init__(self, base_client: BaseApiClient, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.client = base_client

    def get_pieces(self, archive_id: int):
        """
        Initiates a network request to fetch all pieces for an archive.
        """
        url = build_url(Endpoint.PIECES, path_params={"archive_id": archive_id})
        reply = self.client.get(url)
        
        reply.finished.connect(lambda r=reply: self._on_get_pieces_finished(r))

    def _on_get_pieces_finished(self, reply: QNetworkReply):
        """
        Callback handler when the pieces fetch request finishes.
        """
        data = self.client.parse_reply(reply)
        
        if data is not None:
            try:
                # Convert the raw dictionary list into Pydantic models
                pieces = [generated_models.PiecePublic(**item) for item in data]
                self.pieces_loaded.emit(pieces)
            except Exception as e:
                self.pieces_error.emit(f"Data parsing error: {str(e)}")
                
        # If data is None and it was a network/auth error, the base_client
        # will have already emitted connection_error or unauthorized.
                
        reply.deleteLater()

    def get_piece_scores(self, archive_id: int, piece_std_name: str):
        """
        Fetches the specific instrument scores available for a piece.
        """
        url = build_url(
            Endpoint.PIECE_SCORES, 
            path_params={"archive_id": archive_id, "piece_std_name": piece_std_name}
        )
        reply = self.client.get(url)
        reply.finished.connect(lambda r=reply: self._on_get_piece_scores_finished(r))

    def _on_get_piece_scores_finished(self, reply: QNetworkReply):
        data = self.client.parse_reply(reply)
        if data is not None:
            # Assuming backend returns a raw list of strings based on Route setup
            if isinstance(data, list):
                self.piece_scores_loaded.emit(data)
            else:
                self.piece_scores_error.emit("Unexpected data format returned for scores.")
                
        reply.deleteLater()
