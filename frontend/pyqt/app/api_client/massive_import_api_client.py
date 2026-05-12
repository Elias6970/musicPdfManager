from typing import Optional

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtNetwork import QNetworkReply

from app.api_client.base_api_client import BaseApiClient
from app.config.urls import Endpoint, build_url
from app.models.generated_models import MassiveImportResponse

class MassiveImportApiClient(QObject):
    """
    API Client for handling massive import operations.
    Manages importing multiple pieces from Excel and archive files.
    """

    # Signals for make_import
    make_import_success = pyqtSignal(MassiveImportResponse)
    make_import_error = pyqtSignal(str)

    def __init__(self, base_client: BaseApiClient, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.client = base_client

    def make_import(
        self,
        archive_id: int,
        excel_name_path: str,
        archive_name_path: str,
        ignore_first_excel_row: bool = True,
    ):
        """
        POST /massive_import/
        
        Initiates a massive import operation with an Excel file and archive path.
        
        Args:
            archive_id: The ID of the archive to import into.
            excel_name_path: Path to the Excel file containing piece information.
            archive_name_path: Path to the archive folder containing PDF files.
            ignore_first_excel_row: Whether to ignore the first row (header) in the Excel file.
        """
        # Build query parameters
        query_params = {
            "archive_id": archive_id,
            "excel_name_path": excel_name_path,
            "archive_name_path": archive_name_path,
            "ignore_first_excel_row": ignore_first_excel_row,
        }
        
        url = build_url(Endpoint.MASSIVE_IMPORT, query_params=query_params)
        reply = self.client.post(url)
        reply.finished.connect(lambda r=reply: self._on_make_import_finished(r))

    def _on_make_import_finished(self, reply: QNetworkReply):
        """
        Callback handler when the make_import request finishes.
        """
        data = self.client.parse_reply(reply)
        if data is not None:
            response = MassiveImportResponse(**data)
            self.make_import_success.emit(response)
        else:
            self.make_import_error.emit(reply.errorString())
        reply.deleteLater()
