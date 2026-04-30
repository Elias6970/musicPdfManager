import os
from urllib.parse import quote
import httpx
from PyQt6.QtCore import QObject, pyqtSignal

from frontend.pyqt.app.config.urls import Endpoint, build_url
from frontend.pyqt.app.config.session_manager import SessionManager
import frontend.pyqt.app.models.generated_models as generated_models

class UploadsApiClient(QObject):
    """
    Special API client that uses httpx directly instead of QNetworkAccessManager 
    for streaming file uploads to the staging area.
    """

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)
        self.session = SessionManager()

    def upload_file_to_staging(self, file_path: str) -> generated_models.UploadStagingResponse | None:
        """
        Uploads a single file to staging and returns the response synchronously.
        """
        url = build_url(Endpoint.UPLOADS_STAGING)
        filename = os.path.basename(file_path)
        
        headers = {
            'filename': quote(filename)
        }
        
        token = self.session.get_jwt()
        if token:
            headers['Authorization'] = f"Bearer {token}"

        try:
            with open(file_path, "rb") as f:
                r = httpx.post(url=url, data=f, headers=headers)
            
            if r.status_code == 201:
                return generated_models.UploadStagingResponse(**r.json())
            else:
                print(f"Upload failed: {r.status_code} - {r.text}")
                return None
        except Exception as e:
            print(f"Exception during upload: {e}")
            return None
