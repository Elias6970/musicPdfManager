from PyQt6 import QtCore, QtWidgets

from frontend.pyqt.app.archive_crud.delete_archive.delete_archive_view import DeleteArchiveView
from frontend.pyqt.app.models.generated_models import ArchivePublic
from frontend.pyqt.app.api_client.archives_api_client import ArchivesApiClient
from frontend.pyqt.app.api_client.base_api_client_factory import get_base_client

class DeleteArchiveController(QtCore.QObject):
    def __init__(self, view: DeleteArchiveView):
        super().__init__()
        self.view = view
        self.client = ArchivesApiClient(get_base_client(), self)
        
        self.view.confirm_signal.connect(self._on_confirm_clicked)
        self.view.cancel_signal.connect(self.view.reject)
        
        self.client.delete_archive_success.connect(self._on_delete_success)
        self.client.delete_archive_error.connect(self._on_delete_error)
        
        self.client.get_all_archives_success.connect(self._on_fetch_archives_success)
        self.client.get_all_archives_error.connect(self._on_fetch_archives_error)

        # Start loading the available archives
        self.client.get_all_archives()

    def _on_fetch_archives_success(self, archives: list[ArchivePublic]):
        self.view.archive_combobox.blockSignals(True)
        self.view.archive_combobox.clear()
        
        for archive in archives:
            # Store archive ID as user data
            self.view.archive_combobox.addItem(archive.name, userData=archive.id)
            
        self.view.archive_combobox.blockSignals(False)

        if self.view.archive_combobox.count() == 0:
            self.view.archive_combobox.addItem(self.tr("No archives available"))
            self.view.archive_combobox.setEnabled(False)
            self.view.delete_button.setEnabled(False)

    def _on_fetch_archives_error(self, error: str):
        QtWidgets.QMessageBox.critical(self.view, self.tr("Error"), self.tr(f"Failed to load archives: {error}"))
        self.view.reject()

    def _on_confirm_clicked(self):
        index = self.view.archive_combobox.currentIndex()
        if index < 0 or not self.view.archive_combobox.isEnabled():
            return  # Nothing selected or disabled

        archive_id = self.view.archive_combobox.itemData(index)
        archive_name = self.view.archive_combobox.currentText()
        
        # Confirm deletion with the user
        reply = QtWidgets.QMessageBox.warning(
            self.view,
            self.tr("Confirm Delete"),
            self.tr(f"Are you sure you want to permanently delete the archive '{archive_name}'?"),
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
            QtWidgets.QMessageBox.StandardButton.No
        )
        
        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            self.delete_archive(archive_id)
    
    def delete_archive(self, archive_id: int):
        self.client.delete_archive(archive_id)

    def _on_delete_success(self, response: dict):
        print("Archive deleted successfully.")
        self.view.accept()

    def _on_delete_error(self, error: str):
        QtWidgets.QMessageBox.critical(self.view, self.tr("Error"), f"Failed to delete archive: {error}")
