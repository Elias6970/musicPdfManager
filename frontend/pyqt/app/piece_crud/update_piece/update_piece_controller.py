import os
from PyQt6.QtWidgets import QFileDialog, QApplication, QMessageBox
from PyQt6.QtCore import QObject, Qt

from frontend.pyqt.app.config.session_manager import SessionManager
from frontend.pyqt.app.api_client.base_api_client_factory import get_base_client
from frontend.pyqt.app.api_client.pieces_api_client import PiecesApiClient
from frontend.pyqt.app.api_client.authors_api_client import AuthorsApiClient
from frontend.pyqt.app.api_client.types_api_client import TypesApiClient
from frontend.pyqt.app.api_client.uploads_api_client import UploadsApiClient
import frontend.pyqt.app.models.generated_models as generated_models

from frontend.pyqt.app.piece_crud.update_piece.update_piece_view import UpdatePieceView
from frontend.pyqt.app.pop_up_windows.error.error_window import ShowError

class UpdatePieceController(QObject):
    def __init__(self, view: UpdatePieceView, parent: QObject | None = None):
        super().__init__(parent)
        self.view = view
        self.session = SessionManager()

        self.pieces: list[generated_models.PiecePublic] = []
        self.authors: list[generated_models.AuthorPublic] = []
        self.types: list[generated_models.TypePublic] = []
        self.current_selected_piece: generated_models.PiecePublic | None = None

        base_client = get_base_client()
        self.pieces_api_client = PiecesApiClient(base_client, self)
        self.authors_api_client = AuthorsApiClient(base_client, self)
        self.types_api_client = TypesApiClient(base_client, self)
        self.uploads_api_client = UploadsApiClient(self)

        # Connect API signals
        self.pieces_api_client.pieces_loaded.connect(self._on_pieces_loaded)
        self.pieces_api_client.piece_scores_loaded.connect(self._on_piece_scores_loaded)
        self.authors_api_client.get_authors_success.connect(self._on_authors_loaded)
        self.types_api_client.get_types_success.connect(self._on_types_loaded)

        self.pieces_api_client.piece_updated_success.connect(self._on_piece_updated_success)
        self.pieces_api_client.piece_updated_error.connect(self._on_api_error)

        # Connect View signals
        self.view.piece_searched.connect(self._on_piece_searched)
        self.view.select_files_clicked.connect(self._on_select_files_clicked)
        self.view.update_clicked.connect(self._on_update_clicked)

        # Fetch initial data
        self._load_initial_data()

    def _load_initial_data(self):
        archive_id = self.session.get_archive_id()
        if archive_id:
            self.pieces_api_client.get_pieces(archive_id)
            self.authors_api_client.get_all_authors()
            self.types_api_client.get_all_types()

    def _on_pieces_loaded(self, pieces: list[generated_models.PiecePublic]):
        self.pieces = pieces
        # Populate ScoreSearchBar with std_names
        std_names = [p.std_name for p in pieces if p.std_name]
        self.view.set_pieces_options(std_names)

    def _on_authors_loaded(self, authors: list[generated_models.AuthorPublic]):
        self.authors = authors
        author_names = [a.name for a in authors]
        self.view.set_author_options(author_names)

    def _on_types_loaded(self, types: list[generated_models.TypePublic]):
        self.types = types
        type_names = [t.name for t in types]
        self.view.set_type_options(type_names)

    def _on_piece_searched(self, std_name: str):
        # Match standard name safely
        matching_piece = next((p for p in self.pieces if p.std_name.casefold() == std_name.casefold()), None)
        if matching_piece:
            self.current_selected_piece = matching_piece
            archive_id = self.session.get_archive_id()
            if archive_id:
                # Fetch the existing files assigned to this piece
                self.pieces_api_client.get_piece_scores(archive_id, matching_piece.std_name)
        else:
            ShowError.show_tooltip_error(self.tr("Piece not found"), 5000, self.view.search_bar)

    def _on_piece_scores_loaded(self, scores: list[str]):
        if not self.current_selected_piece:
            return

        # Prepare dict to populate the view's form safely
        data = {
            "cod": self.current_selected_piece.cod,
            "name": getattr(self.current_selected_piece, 'name', ''),
            "author": getattr(self.current_selected_piece.author, 'name', '') if getattr(self.current_selected_piece, 'author', None) else '',
            "type": getattr(self.current_selected_piece.type, 'name', '') if getattr(self.current_selected_piece, 'type', None) else '',
            "is_handwritten": getattr(self.current_selected_piece, 'is_handwritten', False),
            "existing_files": scores
        }
        self.view.populate_form(data)

    def _on_select_files_clicked(self):
        file_paths, _ = QFileDialog.getOpenFileNames(
            self.view,
            self.view.tr("Select New Files"),
            os.path.expanduser("~"),
            "All Files (*)"
        )
        if file_paths:
            self.view.add_new_files_to_list(file_paths)

    def _on_update_clicked(self):
        if not self.current_selected_piece:
            QMessageBox.warning(self.view, "Error", "No piece selected to update.")
            return

        form_data = self.view.get_form_data()
        
        # Validations
        if not form_data["cod"] or str(form_data["cod"]).strip() == "":
            QMessageBox.warning(self.view, "Validation Error", "Code field cannot be empty.")
            return
        if not form_data["name"] or str(form_data["name"]).strip() == "":
            QMessageBox.warning(self.view, "Validation Error", "Name field cannot be empty.")
            return

        archive_id = self.session.get_archive_id()
        if not archive_id:
            QMessageBox.warning(self.view, "Error", "No archive selected.")
            return

        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        
        try:
            # 1. Upload new files if any
            new_files_ids = []
            for new_file in form_data["new_files"]:
                response = self.uploads_api_client.upload_file_to_staging(new_file)
                if response:
                    new_files_ids.append(response.file_id)
                else:
                    raise Exception(f"Failed to upload: {new_file}")
            
                
            # 2. Make changes to the entity and send the files to add and delete to the API
            # Handle author/type
            # Check Author against known list
            author_input_text = str(form_data["author"]).strip()
            author_id = None
            author_name = None
            if author_input_text:
                # Assuming case-insensitive search
                matching_author = next((a for a in self.authors if a.name.casefold() == author_input_text.casefold()), None)
                if matching_author:
                    author_id = matching_author.id
                else:
                    author_name = author_input_text

            # Check Type against known list
            type_input_text = str(form_data["type"]).strip()
            type_id = None
            type_name = None
            if type_input_text:
                matching_type = next((t for t in self.types if t.name.casefold() == type_input_text.casefold()), None)
                if matching_type:
                    type_id = matching_type.id
                else:
                    type_name = type_input_text

            update_payload = generated_models.BodyUpdatePieceApiV1ArchivesArchiveIdPiecesPieceIdPut(
                piece=generated_models.PieceCreate(
                    archive_id=archive_id,
                    cod=form_data["cod"],
                    name=form_data["name"],
                    author_id=author_id,
                    author_name=author_name,
                    type_id=type_id,
                    type_name=type_name,
                    handwrited=form_data["is_handwritten"],
                    parted=False, # TODO: NOW IT IS NOT POSSIBLE TO UPDATE THE OBJECT WITHOUT UPDATING THE FIELD
                    digitalized=len(form_data["untouched_existing_files"]) > 0 or len(new_files_ids) > 0,
                ),
                added_files=new_files_ids,
                removed_files=form_data["removed_files"]
            )
            print("ID piece: ", self.current_selected_piece.id)
            # Proceed with the update
            self.pieces_api_client.update_piece(archive_id, self.current_selected_piece.id, update_payload)

        except Exception as e:
            QApplication.restoreOverrideCursor()
            QMessageBox.critical(self.view, "Operation Error", f"An error occurred during update: {e}")


    def _on_piece_updated_success(self, piece: generated_models.PiecePublic):
        QApplication.restoreOverrideCursor()
        # Ensure we refresh the search bar data if std_name updated
        self.current_selected_piece = piece
        self.view.clear()
        QMessageBox.information(self.view, "Success", "Piece updated successfully!")
        
        # Refresh piece list
        archive_id = self.session.get_archive_id()
        if archive_id:
            self.pieces_api_client.get_pieces(archive_id)
    

    def _on_api_error(self, error_msg: str):
        QApplication.restoreOverrideCursor()
        QMessageBox.critical(self.view, "API Error", f"Failed with server error: {error_msg}")
