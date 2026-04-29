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

    # Emits a list of lists/tuples (archive_id, piece_std_name, [["instrument", pages], ...])
    piece_scores_and_page_counts_loaded = pyqtSignal(int, str, list)
    piece_scores_and_page_counts_error = pyqtSignal(str)

    # Emits upon piece creation
    piece_created_success = pyqtSignal(generated_models.PiecePublic)
    piece_created_error = pyqtSignal(str)

    # Emits upon piece update
    piece_updated_success = pyqtSignal(generated_models.PiecePublic)
    piece_updated_error = pyqtSignal(str)

    # Emits upon adding files to existing piece
    files_added_success = pyqtSignal(generated_models.PiecePublic)
    files_added_error = pyqtSignal(str)

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

    def get_piece_scores_and_page_counts(self, archive_id: int, piece_std_name: str):
        """
        Fetches the specific instrument scores available for a piece along with their page counts.
        """
        url = build_url(
            Endpoint.PIECE_SCORES_PAGE_COUNTS, 
            path_params={"archive_id": archive_id, "piece_std_name": piece_std_name}
        )
        reply = self.client.get(url)
        reply.finished.connect(lambda r=reply,a=archive_id,p=piece_std_name: self._on_get_piece_scores_and_page_counts_finished(r, a, p))

    def _on_get_piece_scores_and_page_counts_finished(self, reply: QNetworkReply, archive_id: int, piece_std_name: str):
        data = self.client.parse_reply(reply)
        if data is not None:
            if isinstance(data, list):
                self.piece_scores_and_page_counts_loaded.emit(archive_id, piece_std_name, data)
            else:
                self.piece_scores_and_page_counts_error.emit("Unexpected data format returned for scores and page counts.")
                
        reply.deleteLater()

    def create_piece(self, archive_id: int, payload: generated_models.BodyAddPieceToArchiveApiV1ArchivesArchiveIdPiecesPost):
        """
        Creates a new piece with assigned files in the archive.
        """
        url = build_url(Endpoint.PIECES, path_params={"archive_id": archive_id})
        reply = self.client.post(url, data=payload)
        reply.finished.connect(lambda r=reply: self._on_create_piece_finished(r))

    def _on_create_piece_finished(self, reply: QNetworkReply):
        data = self.client.parse_reply(reply)
        if data is not None:
            try:
                piece = generated_models.PiecePublic(**data)
                self.piece_created_success.emit(piece)
            except Exception as e:
                self.piece_created_error.emit(f"Data parsing error on creation: {str(e)}")
        else:
            self.piece_created_error.emit(reply.errorString() if reply.errorString() else "Failed to create piece.")
        reply.deleteLater()

    def update_piece(self, archive_id: int, piece_id: int, payload: generated_models.BodyUpdatePieceApiV1ArchivesArchiveIdPiecesPieceIdPut):
        """
        Updates an existing piece in the archive.
        """
        url = build_url(Endpoint.PIECE_BY_ID, path_params={"archive_id": archive_id, "piece_id": piece_id})
        reply = self.client.put(url, data=payload)
        reply.finished.connect(lambda r=reply: self._on_update_piece_finished(r))

    def _on_update_piece_finished(self, reply: QNetworkReply):
        data = self.client.parse_reply(reply)
        if data is not None:
            try:
                piece = generated_models.PiecePublic(**data)
                self.piece_updated_success.emit(piece)
            except Exception as e:
                self.piece_updated_error.emit(f"Parsing error: {str(e)}")
        else:
            self.piece_updated_error.emit(reply.errorString() if reply.errorString() else "Failed to update piece.")
        reply.deleteLater()

    def add_files_to_existing_piece(self, archive_id: int, piece_id: int, files: list[str]):
        """
        Adds additional files to an existing piece in the archive.
        """
        url = build_url(Endpoint.PIECE_FILES, path_params={"archive_id": archive_id, "piece_id": piece_id})
        reply = self.client.post(url, data=files)
        reply.finished.connect(lambda r=reply: self._on_add_files_finished(r))

    def _on_add_files_finished(self, reply: QNetworkReply):
        data = self.client.parse_reply(reply)
        if data is not None:
            try:
                piece = generated_models.PiecePublic(**data)
                self.files_added_success.emit(piece)
            except Exception as e:
                self.files_added_error.emit(f"Parsing error: {str(e)}")
        else:
            self.files_added_error.emit(reply.errorString() if reply.errorString() else "Failed to add files.")
        reply.deleteLater()

