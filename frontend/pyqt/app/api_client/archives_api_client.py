import json
from typing import Any, Optional, Dict, List
from PyQt6.QtCore import pyqtSignal, QObject
from PyQt6.QtNetwork import QNetworkReply

from frontend.pyqt.app.api_client.base_api_client import BaseApiClient
from frontend.pyqt.app.config.urls import Endpoint, build_url
from frontend.pyqt.app.models.generated_models import ArchiveCreate, ArchivePublic

class ArchivesApiClient(QObject):
    """
    API client for standard CRUD operations and user association for Archives.
    """

    # Signals for create_archive
    create_archive_success = pyqtSignal(ArchivePublic)
    create_archive_error = pyqtSignal(str)

    # Signals for get_archive
    get_archive_success = pyqtSignal(ArchivePublic)
    get_archive_error = pyqtSignal(str)

    # Signals for get_all_archives
    get_all_archives_success = pyqtSignal(list)
    get_all_archives_error = pyqtSignal(str)

    # Signals for update_archive
    update_archive_success = pyqtSignal(ArchivePublic)
    update_archive_error = pyqtSignal(str)

    # Signals for delete_archive
    delete_archive_success = pyqtSignal(dict)
    delete_archive_error = pyqtSignal(str)

    # Signals for add_user_to_archive
    add_user_to_archive_success = pyqtSignal(dict)
    add_user_to_archive_error = pyqtSignal(str)

    def __init__(self, base_client: BaseApiClient, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.client = base_client

    def create_archive(self, archive_data: ArchiveCreate):
        """POST /archives/"""
        url = build_url(Endpoint.ARCHIVES)
        reply = self.client.post(url, data=archive_data)
        reply.finished.connect(lambda r=reply: self._on_create_archive_finished(r))

    def _on_create_archive_finished(self, reply: QNetworkReply):
        data = self.client.parse_reply(reply)
        if data is not None:
            try:
                archive = ArchivePublic(**data)
                self.create_archive_success.emit(archive)
            except Exception as e:
                self.create_archive_error.emit(f"Data parsing error: {str(e)}")
        else:
            self.create_archive_error.emit(reply.errorString())
        reply.deleteLater()

    def get_archive(self, archive_id: int):
        """GET /archives/{archive_id}"""
        url = build_url(Endpoint.ARCHIVE_BY_ID, path_params={"archive_id": archive_id})
        reply = self.client.get(url)
        reply.finished.connect(lambda r=reply: self._on_get_archive_finished(r))

    def _on_get_archive_finished(self, reply: QNetworkReply):
        data = self.client.parse_reply(reply)
        if data is not None:
            try:
                archive = ArchivePublic(**data)
                self.get_archive_success.emit(archive)
            except Exception as e:
                self.get_archive_error.emit(f"Data parsing error: {str(e)}")
        else:
            self.get_archive_error.emit(reply.errorString())
        reply.deleteLater()

    def get_all_archives(self):
        """GET /archives/"""
        url = build_url(Endpoint.ARCHIVES)
        reply = self.client.get(url)
        reply.finished.connect(lambda r=reply: self._on_get_all_archives_finished(r))

    def _on_get_all_archives_finished(self, reply: QNetworkReply):
        data = self.client.parse_reply(reply)
        if data is not None:
            try:
                archives = [ArchivePublic(**item) for item in data]
                print(data)
                self.get_all_archives_success.emit(archives)
            except Exception as e:
                self.get_all_archives_error.emit(f"Data parsing error: {str(e)}")
        else:
            self.get_all_archives_error.emit(reply.errorString())
        reply.deleteLater()

    def update_archive(self, archive_id: int, archive_data: ArchiveCreate):
        """PUT /archives/{archive_id}"""
        url = build_url(Endpoint.ARCHIVE_BY_ID, path_params={"archive_id": archive_id})
        reply = self.client.put(url, data=archive_data)
        reply.finished.connect(lambda r=reply: self._on_update_archive_finished(r))

    def _on_update_archive_finished(self, reply: QNetworkReply):
        data = self.client.parse_reply(reply)
        if data is not None:
            try:
                archive = ArchivePublic(**data)
                self.update_archive_success.emit(archive)
            except Exception as e:
                self.update_archive_error.emit(f"Data parsing error: {str(e)}")
        else:
            self.update_archive_error.emit(reply.errorString())
        reply.deleteLater()

    def delete_archive(self, archive_id: int):
        """DELETE /archives/{archive_id}"""
        url = build_url(Endpoint.ARCHIVE_BY_ID, path_params={"archive_id": archive_id})
        reply = self.client.delete(url)
        reply.finished.connect(lambda r=reply: self._on_delete_archive_finished(r))

    def _on_delete_archive_finished(self, reply: QNetworkReply):
        data = self.client.parse_reply(reply)
        if data is not None:
            self.delete_archive_success.emit(data)
        else:
            self.delete_archive_error.emit(reply.errorString())
        reply.deleteLater()

    def add_user_to_archive(self, archive_id: int, user_id: int, role: str):
        """POST /archives/{archive_id}/users/{user_id}"""
        url = build_url(
            Endpoint.ARCHIVE_USER_BY_ID, 
            path_params={"archive_id": archive_id, "user_id": user_id},
            query_params={"role": role}
        )
        reply = self.client.post(url, data=None)
        reply.finished.connect(lambda r=reply: self._on_add_user_to_archive_finished(r))

    def _on_add_user_to_archive_finished(self, reply: QNetworkReply):
        data = self.client.parse_reply(reply)
        if data is not None:
            self.add_user_to_archive_success.emit(data)
        else:
            self.add_user_to_archive_error.emit(reply.errorString())
        reply.deleteLater()
