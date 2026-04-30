from PyQt6 import QtCore, QtWidgets

from frontend.pyqt.app.config.session_manager import SessionManager
from frontend.pyqt.app.models.generated_models import PiecePublic
from frontend.pyqt.app.api_client.pieces_api_client import PiecesApiClient
from frontend.pyqt.app.api_client.base_api_client_factory import get_base_client
from frontend.pyqt.app.piece_crud.delete_piece.delete_piece_view import DeletePieceView

class DeletePieceController(QtCore.QObject):
    def __init__(self, view: DeletePieceView):
        super().__init__()
        self.view = view
        self.session = SessionManager()
        
        self.client = PiecesApiClient(get_base_client(), self)
        
        self.view.confirm_signal.connect(self._on_confirm_clicked)
        self.view.cancel_signal.connect(self.view.reject)
        
        self.client.piece_deleted_success.connect(self._on_delete_success)
        self.client.piece_deleted_error.connect(self._on_delete_error)
        
        self.client.pieces_loaded.connect(self._on_fetch_pieces_success)
        self.client.pieces_error.connect(self._on_fetch_pieces_error)

        # Start loading the available pieces
        self.client.get_pieces(self.session.get_archive_id())

    def _on_fetch_pieces_success(self, pieces: list[PiecePublic]):
        self.view.piece_combobox.blockSignals(True)
        self.view.piece_combobox.clear()
        
        for piece in pieces:
            # Store piece ID as user data
            self.view.piece_combobox.addItem(piece.std_name, userData=piece.id)
            
        self.view.piece_combobox.blockSignals(False)

        if self.view.piece_combobox.count() == 0:
            self.view.piece_combobox.addItem(self.tr("No pieces available"))
            self.view.piece_combobox.setEnabled(False)
            self.view.delete_button.setEnabled(False)

    def _on_fetch_pieces_error(self, error: str):
        QtWidgets.QMessageBox.critical(self.view, self.tr("Error"), self.tr(f"Failed to load pieces: {error}"))
        self.view.reject()

    def _on_confirm_clicked(self):
        index = self.view.piece_combobox.currentIndex()
        if index < 0 or not self.view.piece_combobox.isEnabled():
            return  # Nothing selected or disabled

        piece_id = self.view.piece_combobox.itemData(index)
        piece_name = self.view.piece_combobox.currentText()
        
        # Confirm deletion with the user
        reply = QtWidgets.QMessageBox.warning(
            self.view,
            self.tr("Confirm Delete"),
            self.tr(f"Are you sure you want to permanently delete the piece '{piece_name}'?"),
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
            QtWidgets.QMessageBox.StandardButton.No
        )
        
        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            self.delete_piece(piece_id)

    def delete_piece(self, piece_id: int):
        self.client.delete_piece(self.session.get_archive_id(), piece_id)

    def _on_delete_success(self, piece_id: int):
        print("Piece deleted successfully.")
        QtWidgets.QMessageBox.information(self.view, self.tr("Success"), self.tr("Piece deleted successfully."))
        #self.view.accept()

    def _on_delete_error(self, error: str):
        QtWidgets.QMessageBox.critical(self.view, self.tr("Error"), f"Failed to delete piece: {error}")
