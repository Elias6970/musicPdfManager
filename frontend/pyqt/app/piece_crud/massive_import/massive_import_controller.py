from PyQt6 import QtCore, QtWidgets
import zipfile, io, os

from frontend.pyqt.app.api_client.base_api_client_factory import get_base_client
from frontend.pyqt.app.api_client.massive_import_api_client import MassiveImportApiClient
from frontend.pyqt.app.api_client.uploads_api_client import UploadsApiClient
from frontend.pyqt.app.piece_crud.massive_import.massive_import_view import MassiveImportView
from frontend.pyqt.app.models.generated_models import ArchivePublic, MassiveImportResponse
from frontend.pyqt.app.pop_up_windows.error.error_window import ShowError

class MassiveImportController(QtCore.QObject):
    
    def __init__(self, view: MassiveImportView, archive: ArchivePublic, parent=None):
        super().__init__(parent)
        self.view = view
        self.archive = archive

        # Progress tracking variables
        self.total_pieces:int = 0
        self.imported_pieces:int = 0
       
        self.folder_id:str|None = None # Folder id for staging for all the pieces in the archive
        
        self.import_data_file_path:str|None = None # The path of the data file being imported, used for progress tracking and error messages.
        self.import_folder_path:str|None = None # The path of the folder being imported, used for progress tracking and error messages.

        self.upload_api_client = UploadsApiClient()
        self.massive_import_api_client = MassiveImportApiClient(get_base_client())
        self.massive_import_api_client.make_import_success.connect(self._on_make_import_success)
        self.massive_import_api_client.make_import_error.connect(self._on_make_import_error)

        self.view.import_data_file_signal.connect(self._on_import_data_file_clicked)
        self.view.import_archive_signal.connect(self._on_import_clicked)
        self.view.confirm_signal.connect(self._on_confirm_clicked)

    def _on_import_clicked(self):
        """Select the folder to import as an archive."""
        # Open a file dialog to select the folder to import as an archive
        folder_path = QtWidgets.QFileDialog.getExistingDirectory(self.view, self.tr("Select Folder to Import as Archive"))
        
        if folder_path:
            self.import_folder_path = folder_path
            self.view.set_archive_path_lbl(folder_path)


    def _on_import_data_file_clicked(self):
        """Select the data file to import."""
        # Open a file dialog to select the data file to import
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self.view, self.tr("Select Data File"), filter="Data Files (*.xls *.xlsx *.csv)")
        
        if file_path:
            self.import_data_file_path = file_path
            self.view.set_data_file_lbl(file_path)   


    def _on_confirm_clicked(self):
        if not self.import_data_file_path:
            ShowError.show_tooltip_error(self.tr("You need to select a data file to import."),5000, self.view.data_file_button)
            return
        if not self.import_folder_path:
            ShowError.show_tooltip_error(self.tr("You need to select a folder to import as an archive."),5000, self.view.import_button)
            return
        
        data_file_id = self.upload_data_file(self.import_data_file_path)
        if not data_file_id:
            QtWidgets.QMessageBox.critical(self.view, self.tr("Error"), self.tr("Failed to upload the data file. Please try again."))
            return
        
        self.upload_archive(self.import_folder_path)
        self.view.set_finished_uploading()

        if not self.folder_id:
            QtWidgets.QMessageBox.critical(self.view, self.tr("Error"), self.tr("Failed to upload the archive files. Please try again."))
            return
        
        self.massive_import_api_client.make_import(
            archive_id=self.archive.id,
            excel_name_path=data_file_id,
            archive_name_path=self.folder_id
        )

    def _on_make_import_success(self, response: MassiveImportResponse):
        message = self.tr("Massive import completed successfully.\n\n")
        if response.full_added_pieces:
            message += self.tr("Pieces fully added with their files:\n") + "\n".join(response.full_added_pieces) + "\n\n"
        if response.pieces_without_files:
            message += self.tr("Pieces added without files:\n") + "\n".join(response.pieces_without_files) + "\n\n"
        if response.not_added_pieces:
            message += self.tr("Pieces not added due to errors:\n") + "\n".join([f"{item['std_name']}: {item['error']}" for item in response.not_added_pieces])
        
        QtWidgets.QMessageBox.information(self.view, self.tr("Import Result"), message)
        self.view.accept()

    def _on_make_import_error(self, error: str):
        QtWidgets.QMessageBox.critical(self.view, self.tr("Error"), self.tr(f"Failed to import the archive: {error}"))


    def upload_data_file(self, file_path: str) -> str | None:
        """Uploads a data file and returns the file_id in staging"""
        print(f"Uploading data file: {file_path}")
        response = self.upload_api_client.upload_file_to_staging(file_path)
        if response:
            return response.file_id
        return None
    
    def upload_archive(self, archive_path:str):
        self.total_pieces = len(os.listdir(archive_path)) #It is inprecise because it counts folders as pieces, but it is just for progress tracking, so it is good enough.
         
        for i in os.listdir(archive_path):
            if os.path.isdir(os.path.join(archive_path, i)):
                file_name, zip_data = self._compress_folder_to_zip(os.path.join(archive_path, i))
                file_name = f"{file_name}.zip" # The backend expects a zip file, so we add the extension to the original folder name.
                response = self.upload_api_client.upload_folder_to_staging(
                    filename=file_name, 
                    data=zip_data, 
                    folder_id=self.folder_id
                )
                if response:
                    self.folder_id = response.folder_id # Set the folder_id for the next uploads, so all the pieces in the archive are uploaded to the same staging folder.
                    self.imported_pieces += 1
                    print(f"Uploaded {response.original_filename} to staging folder {self.folder_id}. Progress: {self.imported_pieces}/{self.total_pieces} ({(self.imported_pieces/self.total_pieces)*100:.2f}%)")
                    self.view.set_progress(int((self.imported_pieces/self.total_pieces)*100))
    
    
    def _compress_folder_to_zip(self, folder_path: str) -> tuple[str, bytes]:
        """
        Compresses a folder and its content into a zip file in memory.
        Params:
            - folder_path: The path to the folder to compress.
        Returns:
            - A tuple containing the original folder name and the bytes of the compressed zip file.
        """
        try:
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(folder_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, start=folder_path)
                        zipf.write(file_path, arcname)
            return os.path.basename(folder_path), zip_buffer.getvalue()
        except Exception as e:
            print(f"Error compressing folder: {e}")
            raise

    def reset(self):
        self.total_pieces = 0
        self.imported_pieces = 0
        self.folder_id = None