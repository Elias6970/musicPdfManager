from PyQt6 import QtCore, QtWidgets

from frontend.pyqt.app.archive_crud.create_archive.create_archive_view import CreateArchiveView
from frontend.pyqt.app.models.generated_models import ArchiveCreate, ArchivePublic
from frontend.pyqt.app.api_client.archives_api_client import ArchivesApiClient
from frontend.pyqt.app.api_client.base_api_client_factory import get_base_client

class CreateArchiveController(QtCore.QObject):
    def __init__(self, view:CreateArchiveView):
        super().__init__()
        self.view = view
        self.client = ArchivesApiClient(get_base_client(), self)

        self.view.confirm_signal.connect(self._on_confirm_clicked)
        self.view.cancel_signal.connect(self.view.close)
        
        self.client.create_archive_success.connect(self._on_create_success)
        self.client.create_archive_error.connect(self._on_create_error)
    
    def _on_confirm_clicked(self):
        archive_name = self.view.name_input.text()
        
        if not archive_name.strip():
            QtWidgets.QMessageBox.warning(self.view, self.tr("Warning"), self.tr("Archive name cannot be empty."))
            return
        
        self.create_archive(archive_name)
    def create_archive(self, archive_name: str):
        archive = ArchiveCreate(name=archive_name)
        self.client.create_archive(archive)

    def _on_create_success(self, archive: ArchivePublic):
        print(f"Archive created successfully: {archive.name}")
        QtWidgets.QMessageBox.information(self.view, self.tr("Success"), self.tr(f"Archive '{archive.name}' created successfully."))
        self.view.accept()

    def _on_create_error(self, error: str):
        QtWidgets.QMessageBox.critical(self.view, self.tr("Error"), self.tr(f"Failed to create archive: {error}"))
