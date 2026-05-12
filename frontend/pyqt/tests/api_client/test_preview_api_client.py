import pytest
from unittest.mock import MagicMock

from PyQt6.QtCore import QByteArray
from PyQt6.QtNetwork import QNetworkReply

from app.api_client.preview_api_client import PreviewApiClient


@pytest.fixture
def preview_client():
    mock_base_client = MagicMock()
    return PreviewApiClient(base_client=mock_base_client)


@pytest.fixture
def mock_reply():
    reply = MagicMock(spec=QNetworkReply)
    return reply


def test_on_fetch_finished_success(preview_client, mock_reply):
    # Setup mock reply
    mock_reply.error.return_value = QNetworkReply.NetworkError.NoError
    
    mock_read_all = MagicMock()
    mock_read_all.data.return_value = b"fake_image_bytes"
    mock_reply.readAll.return_value = mock_read_all
    
    def side_effect(header):
        if header == b"X-Piece_Std-Name":
            return QByteArray(b"Test Piece")
        elif header == b"X-File-Name":
            return QByteArray(b"test_file.pdf")
        elif header == b"X-Page-Number":
            return QByteArray(b"2")
        elif header == b"X-Total-Pages":
            return QByteArray(b"5")
        return QByteArray()

    mock_reply.rawHeader.side_effect = side_effect
    
    # Setup signal interception
    loaded_slot = MagicMock()
    preview_client.preview_loaded.connect(loaded_slot)
    
    # Execute
    preview_client._on_fetch_finished(mock_reply)
    
    # Assert
    loaded_slot.assert_called_once_with("Test Piece", "test_file.pdf", b"fake_image_bytes", 2, 5)
    mock_reply.deleteLater.assert_called_once()


def test_on_fetch_finished_success_no_header_defaults_to_one(preview_client, mock_reply):
    mock_reply.error.return_value = QNetworkReply.NetworkError.NoError
    
    mock_read_all = MagicMock()
    mock_read_all.data.return_value = b"fake_image_bytes"
    mock_reply.readAll.return_value = mock_read_all
    
    def side_effect(header):
        if header == b"X-Piece_Std-Name":
            return QByteArray(b"Test Piece")
        elif header == b"X-File-Name":
            return QByteArray(b"test_file.pdf")
        return QByteArray()

    mock_reply.rawHeader.side_effect = side_effect
    
    loaded_slot = MagicMock()
    preview_client.preview_loaded.connect(loaded_slot)
    
    preview_client._on_fetch_finished(mock_reply)
    
    loaded_slot.assert_called_once_with("Test Piece", "test_file.pdf", b"fake_image_bytes", 0, 1)


def test_on_fetch_finished_operation_canceled_ignored(preview_client, mock_reply):
    mock_reply.error.return_value = QNetworkReply.NetworkError.OperationCanceledError
    
    loaded_slot = MagicMock()
    error_slot = MagicMock()
    preview_client.preview_loaded.connect(loaded_slot)
    preview_client.preview_error.connect(error_slot)
    
    preview_client._on_fetch_finished(mock_reply)
    
    # Assert nothing was emitted
    loaded_slot.assert_not_called()
    error_slot.assert_not_called()
    mock_reply.deleteLater.assert_called_once()


def test_on_fetch_finished_unauthorized_error(preview_client, mock_reply):
    mock_reply.error.return_value = QNetworkReply.NetworkError.AuthenticationRequiredError
    
    error_slot = MagicMock()
    preview_client.preview_error.connect(error_slot)
    
    preview_client._on_fetch_finished(mock_reply)
    
    error_slot.assert_called_once_with("Unauthorized access. Please log in again.")
    mock_reply.deleteLater.assert_called_once()


def test_on_fetch_finished_generic_error(preview_client, mock_reply):
    mock_reply.error.return_value = QNetworkReply.NetworkError.InternalServerError
    mock_reply.errorString.return_value = "Server explosion"
    
    error_slot = MagicMock()
    preview_client.preview_error.connect(error_slot)
    
    preview_client._on_fetch_finished(mock_reply)
    
    error_slot.assert_called_once_with("HTTP Error: Server explosion")
    mock_reply.deleteLater.assert_called_once()


def test_on_fetch_finished_clears_current_reply(preview_client, mock_reply):
    preview_client._current_reply = mock_reply
    mock_reply.error.return_value = QNetworkReply.NetworkError.OperationCanceledError
    
    preview_client._on_fetch_finished(mock_reply)
    
    assert preview_client._current_reply is None