import json
from typing import Optional, Dict, List, Tuple
from PyQt6.QtCore import pyqtSignal, QObject
from PyQt6.QtNetwork import QNetworkReply

from app.api_client.base_api_client import BaseApiClient
from app.config.urls import Endpoint, build_url

class InstrumentsNamesApiClient(QObject):
    """
    API client for instrument names, translations, and shortcuts.
    """

    get_shortcuts_and_instruments_success = pyqtSignal(dict)
    get_shortcuts_and_instruments_error = pyqtSignal(str)

    get_instruments_and_shortcuts_success = pyqtSignal(dict)
    get_instruments_and_shortcuts_error = pyqtSignal(str)

    get_instruments_and_shortcuts_translated_success = pyqtSignal(list)
    get_instruments_and_shortcuts_translated_error = pyqtSignal(str)

    get_instruments_success = pyqtSignal(list)
    get_instruments_error = pyqtSignal(str)

    def __init__(self, base_client: BaseApiClient, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.client = base_client

    def get_shortcuts_and_instruments(self):
        """GET /instruments_names/shortcuts_and_instruments"""
        url = build_url(Endpoint.INSTRUMENTS_NAMES_SHORTCUTS_AND_INSTRUMENTS)
        reply = self.client.get(url)
        reply.finished.connect(lambda r=reply: self._on_get_shortcuts_and_instruments_finished(r))

    def _on_get_shortcuts_and_instruments_finished(self, reply: QNetworkReply):
        data = self.client.parse_reply(reply)
        if data is not None:
            self.get_shortcuts_and_instruments_success.emit(data)
        else:
            self.get_shortcuts_and_instruments_error.emit(reply.errorString())
        reply.deleteLater()

    def get_instruments_and_shortcuts(self):
        """GET /instruments_names/instruments_and_shortcuts"""
        url = build_url(Endpoint.INSTRUMENTS_NAMES_INSTRUMENTS_AND_SHORTCUTS)
        reply = self.client.get(url)
        reply.finished.connect(lambda r=reply: self._on_get_instruments_and_shortcuts_finished(r))

    def _on_get_instruments_and_shortcuts_finished(self, reply: QNetworkReply):
        data = self.client.parse_reply(reply)
        if data is not None:
            self.get_instruments_and_shortcuts_success.emit(data)
        else:
            self.get_instruments_and_shortcuts_error.emit(reply.errorString())
        reply.deleteLater()

    def get_instruments_and_shortcuts_translated(self, language_cod: str):
        """GET /instruments_names/instruments_and_shortcuts/{language_cod}"""
        url = build_url(Endpoint.INSTRUMENTS_NAMES_TRANSLATED, path_params={"language_cod": language_cod})
        reply = self.client.get(url)
        reply.finished.connect(lambda r=reply: self._on_get_instruments_and_shortcuts_translated_finished(r))

    def _on_get_instruments_and_shortcuts_translated_finished(self, reply: QNetworkReply):
        data = self.client.parse_reply(reply)
        if data is not None:
            self.get_instruments_and_shortcuts_translated_success.emit(data)
        else:
            self.get_instruments_and_shortcuts_translated_error.emit(reply.errorString())
        reply.deleteLater()

    def get_instruments(self):
        """GET /instruments_names/"""
        url = build_url(Endpoint.INSTRUMENTS_NAMES)
        reply = self.client.get(url)
        reply.finished.connect(lambda r=reply: self._on_get_instruments_finished(r))

    def _on_get_instruments_finished(self, reply: QNetworkReply):
        data = self.client.parse_reply(reply)
        if data is not None:
            self.get_instruments_success.emit(data)
        else:
            self.get_instruments_error.emit(reply.errorString())
        reply.deleteLater()
