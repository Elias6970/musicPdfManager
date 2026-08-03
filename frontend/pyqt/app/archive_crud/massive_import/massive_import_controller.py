from PyQt6 import QtCore, QtWidgets
import zipfile, io, os, threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from app.api_client.base_api_client_factory import get_base_client
from app.api_client.massive_import_api_client import MassiveImportApiClient
from app.api_client.uploads_api_client import UploadsApiClient
from app.archive_crud.massive_import.massive_import_view import MassiveImportView
from app.models.generated_models import ArchivePublic, MassiveImportResponse
from app.pop_up_windows.massive_import_result_window import MassiveImportResultWindow
from app.pop_up_windows.error.error_window import ShowError

class MassiveImportController(QtCore.QObject):
    upload_progress_signal = QtCore.pyqtSignal(int)
    upload_finished_signal = QtCore.pyqtSignal(str)
    upload_finished_noarg_signal = QtCore.pyqtSignal()
    upload_error_signal = QtCore.pyqtSignal(str)
    
    def __init__(self, view: MassiveImportView, archive: ArchivePublic, parent=None):
        super().__init__(parent)
        self.view = view
        self.archive = archive

        # Progress tracking variables
        self.total_pieces:int = 0
        self.imported_pieces:int = 0

        self._uploaded_excel_file_id:str|None = None # The file_id of the uploaded data file in staging, used for the import call.
       
        self.folder_id:str|None = None # Folder id for staging for all the pieces in the archive
        
        self.import_data_file_path:str|None = None # The path of the data file being imported, used for progress tracking and error messages.
        self.import_folder_path:str|None = None # The path of the folder being imported, used for progress tracking and error messages.

        self.upload_api_client = UploadsApiClient()
        self.massive_import_api_client = MassiveImportApiClient(get_base_client())
        self.massive_import_api_client.make_import_success.connect(self._on_make_import_success)
        self.massive_import_api_client.make_import_error.connect(self._on_make_import_error)

        # Connect internal upload signals to view and handlers
        self.upload_progress_signal.connect(self.view.set_progress)
        self.upload_finished_noarg_signal.connect(self.view.set_finished_uploading)
        self.upload_finished_signal.connect(self._on_upload_finished)
        self.upload_error_signal.connect(lambda e: QtWidgets.QMessageBox.critical(self.view, self.tr("Error"), self.tr(f"Failed to upload the archive files: {e}")))

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
        # Start the (potentially long-running) archive upload in a background thread.
        # When finished the `upload_finished_signal` will trigger the import call.
        self._uploaded_excel_file_id = data_file_id
        self.start_upload_archive(self.import_folder_path)

    def _on_make_import_success(self, response: MassiveImportResponse):
        result_window = MassiveImportResultWindow(
            full_added_pieces=response.full_added_pieces,
            pieces_without_files=response.pieces_without_files,
            not_added_pieces=response.not_added_pieces,
            parent=self.view,
        )
        result_window.exec()
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
    
    def start_upload_archive(self, archive_path: str):
        """Start uploading the archive in a background thread."""
        if not archive_path:
            return
        thread = threading.Thread(target=self._upload_archive_background, args=(archive_path,), daemon=True)
        thread.start()

    def _upload_archive_background(self, archive_path: str):
        """Background wrapper that runs the upload and emits signals."""
        try:
            self._upload_archive_task(archive_path)
            # emit finished with folder_id (or empty string on failure)
            self.upload_finished_signal.emit(self.folder_id or "")
            self.upload_finished_noarg_signal.emit()
        except Exception as e:
            self.upload_error_signal.emit(str(e))

    def _upload_archive_task(self, archive_path: str):
        directories = [os.path.join(archive_path, i) for i in os.listdir(archive_path) if os.path.isdir(os.path.join(archive_path, i))]
        self.total_pieces = len(directories) # More precise now since we only count directories

        if not directories:
            return

        # Upload the first directory sequentially to establish the folder_id
        first_dir = directories[0]
        file_name, zip_data = self._compress_folder_to_zip(first_dir)
        file_name = f"{file_name}.zip"
        response = self.upload_api_client.upload_folder_to_staging(
            filename=file_name, 
            data=zip_data, 
            folder_id=self.folder_id
        )
        if response:
            self.folder_id = response.folder_id # Set the folder_id for the next uploads
            self.imported_pieces += 1
            print(f"Uploaded {response.original_filename} to staging folder {self.folder_id}. Progress: {self.imported_pieces}/{self.total_pieces} ({(self.imported_pieces/self.total_pieces)*100:.2f}%)")
            self.upload_progress_signal.emit(int((self.imported_pieces/self.total_pieces)*100))
        
        # Upload the rest in parallel using the obtained folder_id
        remaining_dirs = directories[1:]
        if remaining_dirs:
            def upload_dir(dir_path, folder_id):
                f_name, z_data = self._compress_folder_to_zip(dir_path)
                f_name = f"{f_name}.zip" # The backend expects a zip file
                return self.upload_api_client.upload_folder_to_staging(
                    filename=f_name, 
                    data=z_data, 
                    folder_id=folder_id
                )
            
            with ThreadPoolExecutor() as executor:
                future_to_dir = {
                    executor.submit(upload_dir, d, self.folder_id): d
                    for d in remaining_dirs
                }
                
                for future in as_completed(future_to_dir):
                    dir_path = future_to_dir[future]
                    try:
                        resp = future.result()
                        if resp:
                            self.imported_pieces += 1
                            print(f"Uploaded {resp.original_filename} to staging folder {self.folder_id}. Progress: {self.imported_pieces}/{self.total_pieces} ({(self.imported_pieces/self.total_pieces)*100:.2f}%)")
                            self.upload_progress_signal.emit(int((self.imported_pieces/self.total_pieces)*100))
                    except Exception as e:
                        print(f"Failed to upload directory {dir_path}: {e}")
    
    
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

    def _on_upload_finished(self, folder_id: str):
        """Handler called when upload finishes; triggers the massive import using the previously uploaded data file id."""
        if not folder_id:
            QtWidgets.QMessageBox.critical(self.view, self.tr("Error"), self.tr("Failed to upload the archive files. Please try again."))
            return
        if not self._uploaded_excel_file_id:
            QtWidgets.QMessageBox.critical(self.view, self.tr("Error"), self.tr("Data file ID is missing. Cannot proceed with import."))
            return
        
        # call make_import now that we have folder_id and previously uploaded excel id
        self.massive_import_api_client.make_import(
            archive_id=self.archive.id,
            excel_name_path=self._uploaded_excel_file_id,
            archive_name_path=folder_id
        )