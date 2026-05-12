import json
import pytest
from typing import Optional
from unittest.mock import MagicMock, patch

from PyQt6.QtCore import QByteArray, QUrl
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest

# Absolute import for the user's namespace package
from app.api_client.base_client import BaseApiClient


@pytest.fixture
def base_client():
    client = BaseApiClient()
    # Mock the underlying QNetworkAccessManager so we don't send real requests
    client.manager = MagicMock(spec=QNetworkAccessManager)
    return client


def test_set_token(base_client):
    base_client.set_token("test_token")
    assert base_client._token == "test_token"
    
    base_client.set_token(None)
    assert base_client._token is None


def test_create_request_no_token(base_client):
    req = base_client._create_request("http://test.local")
    assert req.url() == QUrl("http://test.local")
    
    content_type = req.header(QNetworkRequest.KnownHeaders.ContentTypeHeader)
    assert content_type == "application/json"
    assert not req.hasRawHeader(b"Authorization")


def test_create_request_with_token(base_client):
    base_client.set_token("my_secret_jwt")
    req = base_client._create_request("http://test.local")
    
    assert req.hasRawHeader(b"Authorization")
    assert req.rawHeader(b"Authorization") == b"Bearer my_secret_jwt"


def test_get(base_client):
    base_client.get("http://test.local/get")
    base_client.manager.get.assert_called_once()
    
    # Verify the request object passed to the manager
    called_request = base_client.manager.get.call_args[0][0]
    assert isinstance(called_request, QNetworkRequest)
    assert called_request.url() == QUrl("http://test.local/get")


def test_delete(base_client):
    base_client.delete("http://test.local/delete")
    base_client.manager.deleteResource.assert_called_once()


def test_post_no_payload(base_client):
    base_client.post("http://test.local/post", data=None)
    
    base_client.manager.post.assert_called_once()
    args = base_client.manager.post.call_args[0]
    request, payload = args
    
    assert request.url() == QUrl("http://test.local/post")
    assert isinstance(payload, QByteArray)
    assert payload.isEmpty()


def test_post_dict_payload(base_client):
    data = {"key": "value"}
    base_client.post("http://test.local/post", data=data)
    
    args = base_client.manager.post.call_args[0]
    payload = args[1]
    
    assert payload.data().decode("utf-8") == '{"key": "value"}'


def test_post_pydantic_v2_payload(base_client):
    mock_model = MagicMock()
    mock_model.model_dump.return_value = {"field": "v2_test"}
    del mock_model.dict  # Ensure it doesn't fallback to v1 accidentally
    
    base_client.post("http://test.local/post", data=mock_model)
    payload = base_client.manager.post.call_args[0][1]
    assert payload.data().decode("utf-8") == '{"field": "v2_test"}'


def test_post_pydantic_v1_payload(base_client):
    mock_model = MagicMock()
    mock_model.dict.return_value = {"field": "v1_test"}
    del mock_model.model_dump  # Simulate it doesn't have v2 method
    
    base_client.post("http://test.local/post", data=mock_model)
    payload = base_client.manager.post.call_args[0][1]
    assert payload.data().decode("utf-8") == '{"field": "v1_test"}'


def test_put_dict_payload(base_client):
    data = {"update": True}
    base_client.put("http://test.local/put", data=data)
    
    base_client.manager.put.assert_called_once()
    payload = base_client.manager.put.call_args[0][1]
    
    assert payload.data().decode("utf-8") == '{"update": true}'


# -- Tests for parse_reply --

@pytest.fixture
def mock_reply():
    reply = MagicMock(spec=QNetworkReply)
    return reply


def test_parse_reply_success(base_client, mock_reply):
    mock_reply.error.return_value = QNetworkReply.NetworkError.NoError
    
    expected_data = {"success": True, "id": 42}
    raw_data = json.dumps(expected_data).encode("utf-8")
    
    mock_read_all = MagicMock()
    mock_read_all.data.return_value = raw_data
    mock_reply.readAll.return_value = mock_read_all
    
    result = base_client.parse_reply(mock_reply)
    assert result == expected_data


def test_parse_reply_empty_response(base_client, mock_reply):
    mock_reply.error.return_value = QNetworkReply.NetworkError.NoError
    
    mock_read_all = MagicMock()
    mock_read_all.data.return_value = b""
    mock_reply.readAll.return_value = mock_read_all
    
    result = base_client.parse_reply(mock_reply)
    assert result == {}


def test_parse_reply_invalid_json(base_client, mock_reply):
    mock_reply.error.return_value = QNetworkReply.NetworkError.NoError
    
    mock_read_all = MagicMock()
    mock_read_all.data.return_value = b"{bad_json"
    mock_reply.readAll.return_value = mock_read_all
    
    # Attach a mock listener to the connection_error signal
    error_slot = MagicMock()
    base_client.connection_error.connect(error_slot)
    
    result = base_client.parse_reply(mock_reply)
    
    assert result is None
    error_slot.assert_called_once_with("Failed to parse server response as JSON.")


def test_parse_reply_unauthorized(base_client, mock_reply):
    mock_reply.error.return_value = QNetworkReply.NetworkError.AuthenticationRequiredError
    
    auth_slot = MagicMock()
    base_client.unauthorized.connect(auth_slot)
    
    result = base_client.parse_reply(mock_reply)
    
    assert result is None
    auth_slot.assert_called_once()


def test_parse_reply_generic_error(base_client, mock_reply):
    mock_reply.error.return_value = QNetworkReply.NetworkError.InternalServerError
    mock_reply.errorString.return_value = "Internal Server Error"
    
    # Simulate a generic HTTP Status Code extraction
    def mock_attribute(attr):
        if attr == QNetworkRequest.Attribute.HttpStatusCodeAttribute:
            return 500
        return None
        
    mock_reply.attribute.side_effect = mock_attribute
    
    error_slot = MagicMock()
    base_client.connection_error.connect(error_slot)
    
    result = base_client.parse_reply(mock_reply)
    
    assert result is None
    error_slot.assert_called_once_with("HTTP 500: Internal Server Error")