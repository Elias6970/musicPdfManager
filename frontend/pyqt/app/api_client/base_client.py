import json
from typing import Any, Optional

from PyQt6.QtCore import QObject, pyqtSignal, QUrl, QByteArray
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply


class BaseApiClient(QObject):
    """
    A foundational networking layer that wraps QNetworkAccessManager.
    
    Responsibilities:
    - Maintains the QNetworkAccessManager instance.
    - Attaches common HTTP headers (like Authorization tokens, Content-Type).
    - Exposes convenient HTTP methods (get, post, put, delete).
    - Provides a centralized `parse_reply` function for unified JSON and error handling.
    """

    # Signals for global API events that multiple UI components might care about
    unauthorized = pyqtSignal()         # Emitted on 401, useful to trigger a Login screen
    connection_error = pyqtSignal(str)  # Emitted on timeouts, DNS issues, or 500s

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.manager = QNetworkAccessManager(self)
        self._token: Optional[str] = None

    def set_token(self, token: Optional[str]):
        """Store the JWT token to be injected into subsequent requests."""
        self._token = token

    def _create_request(self, url: str) -> QNetworkRequest:
        """Helper to create a QNetworkRequest with standard headers."""
        request = QNetworkRequest(QUrl(url))
        request.setHeader(
            QNetworkRequest.KnownHeaders.ContentTypeHeader, 
            "application/json"
        )
        
        if self._token:
            # Add Bearer token for FastAPI dependencies
            request.setRawHeader(b"Authorization", f"Bearer {self._token}".encode('utf-8'))
            
        return request

    def get(self, url: str) -> QNetworkReply:
        """Execute a GET request."""
        return self.manager.get(self._create_request(url))

    def post(self, url: str, data: Any = None) -> QNetworkReply:
        """Execute a POST request with optional JSON data or Pydantic model."""
        request = self._create_request(url)
        payload = QByteArray()
        if data is not None:
            # Handle Pydantic models automatically
            if hasattr(data, "model_dump"):
                data_dict = data.model_dump()
            elif hasattr(data, "dict"):
                data_dict = data.dict()  # Pydantic v1 fallback
            else:
                data_dict = data
                
            payload.append(json.dumps(data_dict).encode('utf-8'))
            
        return self.manager.post(request, payload)

    def put(self, url: str, data: Any = None) -> QNetworkReply:
        """Execute a PUT request with optional JSON data or Pydantic model."""
        request = self._create_request(url)
        payload = QByteArray()
        if data is not None:
            if hasattr(data, "model_dump"):
                data_dict = data.model_dump()
            elif hasattr(data, "dict"):
                data_dict = data.dict()
            else:
                data_dict = data
                
            payload.append(json.dumps(data_dict).encode('utf-8'))
            
        return self.manager.put(request, payload)

    def delete(self, url: str) -> QNetworkReply:
        """Execute a DELETE request."""
        return self.manager.deleteResource(self._create_request(url))

    def parse_reply(self, reply: QNetworkReply) -> Optional[Any]:
        """
        Safely attempts to parse the JSON output from a QNetworkReply.
        Also handles global error checks.
        
        Returns:
            The parsed JSON (dict/list) if successful, otherwise None.
        """
        error = reply.error()
        
        if error == QNetworkReply.NetworkError.NoError:
            raw_data = reply.readAll().data()
            if not raw_data:
                return {} # Empty response (e.g., 204 No Content)
            try:
                return json.loads(raw_data.decode('utf-8'))
            except json.JSONDecodeError:
                self.connection_error.emit("Failed to parse server response as JSON.")
                return None
                
        # Intercept Authentication errors
        elif error == QNetworkReply.NetworkError.AuthenticationRequiredError or reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute) == 401:
            self.unauthorized.emit()
            return None
            
        # Optional: You can handle 404s, 400s here or let the specific Service handle them
        else:
            # Fallback error mapping
            status_code = reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute)
            error_msg = reply.errorString()
            self.connection_error.emit(f"HTTP {status_code}: {error_msg}")
            return None
