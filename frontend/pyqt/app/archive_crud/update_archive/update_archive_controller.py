from PyQt6 import QtCore, QtWidgets

from app.archive_crud.update_archive.update_archive_view import UpdateArchiveView
from app.models.generated_models import ArchiveCreate, ArchivePublic
from app.api_client.archives_api_client import ArchivesApiClient
from app.api_client.base_api_client_factory import get_base_client

class UpdateArchiveController(QtCore.QObject):
    def __init__(self, view: UpdateArchiveView):
        super().__init__()
        self.view = view
        self.client = ArchivesApiClient(get_base_client(), self)
        
        self.view.confirm_signal.connect(self._on_confirm_clicked)
        self.view.cancel_signal.connect(self.view.reject)
        
        # We need to detect when user selects an archive in combobox to update name label
        self.view.archive_combobox.currentIndexChanged.connect(self._on_archive_selected)
        
        self.client.update_archive_success.connect(self._on_update_success)
        self.client.update_archive_error.connect(self._on_update_error)
        
        self.client.get_all_archives_success.connect(self._on_fetch_archives_success)
        self.client.get_all_archives_error.connect(self._on_fetch_archives_error)

        # Start loading the available archives
        self.client.get_all_archives()

    def _on_fetch_archives_success(self, archives: list[ArchivePublic]):
        self.view.archive_combobox.blockSignals(True)  # Prevent early triggering
        self.view.archive_combobox.clear()
        
        for archive in archives:
            # Store archive ID as user data
            self.view.archive_combobox.addItem(archive.name, userData=archive.id)
            
        self.view.archive_combobox.blockSignals(False)

        # Pre-fill data if anything exists
        # if self.view.archive_combobox.count() > 0:
        #     self.view.name_input.setText(self.view.archive_combobox.currentText())

    def _on_fetch_archives_error(self, error: str):
        QtWidgets.QMessageBox.critical(self.view, "Error", f"Failed to load archives: {error}")
        self.view.reject()

    def _on_archive_selected(self, index: int):
        if index >= 0:
            self.view.name_input.setText(self.view.archive_combobox.itemText(index))
        
    def _on_confirm_clicked(self):
        index = self.view.archive_combobox.currentIndex()
        if index < 0:
            return  # Nothing selected

        archive_id = self.view.archive_combobox.itemData(index)
        archive_name = self.view.name_input.text()
        
        if not archive_name.strip():
            QtWidgets.QMessageBox.warning(self.view, "Warning", "Archive name cannot be empty.")
            return

        self.update_archive(archive_id, archive_name)
    
    def update_archive(self, archive_id: int, archive_name: str):
        archive_data = ArchiveCreate(name=archive_name)
        self.client.update_archive(archive_id, archive_data)

    def _on_update_success(self, archive: ArchivePublic):
        print(f"Archive updated successfully: {archive.name}")
        self.view.accept()

    def _on_update_error(self, error: str):
        QtWidgets.QMessageBox.critical(self.view, "Error", f"Failed to update archive: {error}")
