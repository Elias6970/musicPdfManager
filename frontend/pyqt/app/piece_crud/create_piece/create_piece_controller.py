import os
from PyQt6.QtCore import QObject, Qt
from PyQt6.QtWidgets import QFileDialog, QApplication, QMessageBox

from frontend.pyqt.app.piece_crud.create_piece.create_piece_view import CreatePieceView
from frontend.pyqt.app.api_client.uploads_api_client import UploadsApiClient
from frontend.pyqt.app.api_client.pieces_api_client import PiecesApiClient
from frontend.pyqt.app.api_client.authors_api_client import AuthorsApiClient
from frontend.pyqt.app.api_client.types_api_client import TypesApiClient
from frontend.pyqt.app.api_client.base_api_client_factory import get_base_client
from frontend.pyqt.app.config.session_manager import SessionManager
import frontend.pyqt.app.models.generated_models as generated_models

class CreatePieceController(QObject):
    def __init__(self, view: CreatePieceView, parent: QObject | None = None):
        super().__init__(parent)
        self.view = view
        self.session = SessionManager()

        # Data lists to hold existing Authors and Types (populated elsewhere/later)
        self.authors: list[generated_models.AuthorPublic] = []
        self.types: list[generated_models.TypePublic] = []

        base_client = get_base_client()
        self.pieces_api_client = PiecesApiClient(base_client, self)
        self.authors_api_client = AuthorsApiClient(base_client, self)
        self.types_api_client = TypesApiClient(base_client, self)
        self.uploads_api_client = UploadsApiClient(self)

        self.pieces_api_client.piece_created_success.connect(self._on_piece_created)
        self.pieces_api_client.piece_created_error.connect(self._on_piece_creation_error)

        self.authors_api_client.get_authors_success.connect(self._on_authors_loaded)
        self.types_api_client.get_types_success.connect(self._on_types_loaded)

        # Connect the view's signals to our controller's slot methods
        self.view.select_files_clicked.connect(self._on_select_files_clicked)
        self.view.create_clicked.connect(self._on_create_clicked)

        # Initiate fetching authors and types from the backend
        self.authors_api_client.get_all_authors()
        self.types_api_client.get_all_types()

    def _on_authors_loaded(self, authors: list[generated_models.AuthorPublic]):
        """Handler for when authors successfully load from the API."""
        self.authors = authors
        # Pass just strings to the view's completeness engine
        author_names = [a.name for a in authors]
        self.view.set_author_options(author_names)

    def _on_types_loaded(self, types: list[generated_models.TypePublic]):
        """Handler for when types successfully load from the API."""
        self.types = types
        type_names = [t.name for t in types]
        self.view.set_type_options(type_names)

    def _on_select_files_clicked(self):
        """Open a file dialog to select multiple files and add them to the view."""
        
        # Opens a multiple-file selection window
        file_paths, _ = QFileDialog.getOpenFileNames(
            self.view,
            self.tr("Select Files"),
            os.path.expanduser("~"),  # Default starting directory
            "All Files (*)"
        )
        
        if file_paths:
            # Send the retrieved paths back to the view
            self.view.add_files_to_list(file_paths)

    def _on_create_clicked(self):
        """Handle what happens when the 'Create Piece' button is clicked."""
        form_data = self.view.get_form_data()
        print("Create clicked with data:", form_data)
        
        archive_id = self.session.get_archive_id()
        if not archive_id:
            print("No archive selected!")
            return

        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        
        try:
            file_ids = []
            for file_path in form_data["files"]:
                print(f"Uploading {file_path}...")
                response = self.uploads_api_client.upload_file_to_staging(file_path)
                if response:
                    file_ids.append(response.file_id)
                else:
                    raise Exception(f"Failed to upload file: {file_path}")

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

            # Assemble PieceCreate payload
            piece_create = generated_models.PieceCreate(
                cod=int(form_data["cod"]) if form_data["cod"] else 0,
                name=form_data["name"],
                handwrited=form_data["is_handwritten"],
                parted=False, # It need to be updated when classified
                digitalized=len(file_ids) > 0,
                archive_id=archive_id,
                author_id=author_id,
                author_name=author_name,
                type_id=type_id,
                type_name=type_name
            )

            payload = generated_models.BodyAddPieceToArchiveApiV1ArchivesArchiveIdPiecesPost(
                piece=piece_create,
                files=file_ids
            )
            
            print("Submitting Piece Creation...")
            self.pieces_api_client.create_piece(archive_id, payload)
        
        except Exception as e:
            print(f"Error during creation flow: {str(e)}")
            QApplication.restoreOverrideCursor()

    def _on_piece_created(self, piece: generated_models.PiecePublic):
        print(f"Piece successfully created: {piece.name}")
        QApplication.restoreOverrideCursor()
        QMessageBox.information(self.view, self.tr("Success"), self.tr(f"Piece '{piece.name}' created successfully!"))
        self.view.clear() # Optionally clear files or close window

    def _on_piece_creation_error(self, err_msg: str):
        print(f"Failed to create piece: {err_msg}")
        QApplication.restoreOverrideCursor()
        QMessageBox.critical(self.view, self.tr("Error"), self.tr(f"Failed to create piece: {err_msg}"))