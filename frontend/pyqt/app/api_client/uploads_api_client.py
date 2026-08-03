import os
import time
from urllib.parse import quote
import httpx
from PyQt6.QtCore import QObject, pyqtSignal

from app.config.urls import Endpoint, build_url
from app.config.session_manager import SessionManager
import app.models.generated_models as generated_models

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
                r = httpx.post(url=url, content=f, headers=headers, timeout=300.0)
            
            if r.status_code == 201:
                return generated_models.UploadStagingResponse(**r.json())
            else:
                print(f"Upload failed: {r.status_code} - {r.text}")
                return None
        except Exception as e:
            print(f"Exception during upload for file '{file_path}': {e}")
            return None

    def upload_folder_to_staging(self, filename:str, data:bytes, folder_id:str|None = None) -> generated_models.UploadToFolderResponse | None:
            """
            Uploads a folder compresed as a zip file to a staging folder (folder_id).
            Params:
                - filename: The original name of the folder being uploaded (used for naming the zip file in staging).
                - data: The bytes of the compressed zip file.
                - folder_id: The identifier of the staging folder where the file should be uploaded.
            Returns:
                - UploadToFolderResponse: Contains the `folder_id` where the file was uploaded, the `original_filename`, and the size in bytes.
            """
            url = build_url(Endpoint.UPLOADS_STAGING_COMPRESSED, path_params={"folder_id": folder_id})
            filename = os.path.basename(filename)
            
            headers = {
                'filename': quote(filename)
            }
            
            token = self.session.get_jwt()
            if token:
                headers['Authorization'] = f"Bearer {token}"

            max_retries = 3
            for attempt in range(1, max_retries + 1):
                try:
                    r = httpx.post(url=url, content=data, headers=headers, timeout=300.0)
                    
                    if r.status_code == 201:
                        return generated_models.UploadToFolderResponse(**r.json())

                    print(f"Upload failed for '{filename}' (status {r.status_code}) on attempt {attempt}/{max_retries}: {r.text}")
                except Exception as e:
                    print(f"Exception during upload for file '{filename}' on attempt {attempt}/{max_retries}: {e}")

                if attempt < max_retries:
                    time.sleep(1)

            return None