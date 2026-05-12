import json
from typing import Optional, List, Dict, Any
from PyQt6.QtCore import pyqtSignal, QObject
from PyQt6.QtNetwork import QNetworkReply, QNetworkRequest

from app.api_client.base_api_client import BaseApiClient
from app.config.urls import Endpoint, build_url

class ClassificationApiClient(QObject):
    """
    API client for executing classifications.
    """

    # Emitted when the classification succeeds
    classification_success = pyqtSignal(dict)
    
    # Emitted when a file collision (400) occurs with a list of missing names
    classification_file_exists_error = pyqtSignal(list)
    
    # Emitted on other errors
    classification_error = pyqtSignal(str)

    def __init__(self, base_client: BaseApiClient, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.client = base_client

    def execute_classification(self, archive_id: int, job_data: Any):
        """
        POST /classification/{archive_id}
        `job_data` can be a Pydantic model (like ClassificationJob) or a standard dictionary.
        """
        url = build_url(Endpoint.CLASSIFICATION_BY_ID, path_params={"archive_id": archive_id})
        reply = self.client.post(url, data=job_data)
        reply.finished.connect(lambda r=reply: self._on_execute_classification_finished(r))

    def _on_execute_classification_finished(self, reply: QNetworkReply):
        error = reply.error()
        if error == QNetworkReply.NetworkError.NoError:
            # Re-use base client method to safely parse successful response
            data = self.client.parse_reply(reply)
            if data is not None:
                self.classification_success.emit(data)
            else:
                self.classification_error.emit("Unknown error occurred during classification parsing.")
        else:
            status_code = reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute)
            
            # Handle the specific 400 Bad Request error to extract missing_names
            if status_code == 400:
                raw_data = reply.readAll().data()
                if raw_data:
                    try:
                        error_json = json.loads(raw_data.decode('utf-8'))
                        detail = error_json.get("detail", {})
                        
                        # When detail is a dict, it contains the 'missing_names' sent by backend
                        if isinstance(detail, dict) and "missing_names" in detail:
                            self.classification_file_exists_error.emit(detail["missing_names"])
                            reply.deleteLater()
                            return
                        # If detail is just a string, it's a generic 400 error
                        elif isinstance(detail, str):
                            self.classification_error.emit(detail)
                            reply.deleteLater()
                            return
                    except json.JSONDecodeError:
                        pass
            
            # Fallback for other errors (500, 404, etc.)
            self.classification_error.emit(reply.errorString())
            
        reply.deleteLater()
