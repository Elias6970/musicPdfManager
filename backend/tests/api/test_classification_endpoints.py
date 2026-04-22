import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from backend.main import app
from backend.app.models.user import User
from backend.api.dependencies.auth import get_current_user

# Bypass authentication dependency
app.dependency_overrides[get_current_user] = lambda: User(id=1, email="test@test.com", password_hash="123")

client = TestClient(app)

@patch("backend.api.dependencies.permissions.check_archive_role")
@patch("backend.api.routes.classification.classify")
def test_classification_endpoint_success(mock_classify, mock_check_role):
    mock_check_role.return_value = MagicMock()
    mock_classify.return_value = True

    payload = {
        "piece_std_name": "Symphony_9",
        "archive_id": 1,
        "source_files": ["file1.pdf"],
        "classifications": {
            "Violin_1": {
                "config": {"overwrite": False, "rename": None},
                "pages": [{"file_name": "file1.pdf", "page": 0}]
            }
        }
    }

    response = client.post("/api/v1/classification/1", json=payload)
    
    assert response.status_code == 200
    assert response.json()["message"] == "Classification completed successfully"
    mock_classify.assert_called_once()
    mock_check_role.assert_called_once()

@patch("backend.api.dependencies.permissions.check_archive_role")
@patch("backend.api.routes.classification.classify")
def test_classification_endpoint_file_exists_error(mock_classify, mock_check_role):
    from backend.app.error import ClassificationFileExistsError
    
    mock_check_role.return_value = MagicMock()
    mock_classify.side_effect = ClassificationFileExistsError("Target files already exist", ["Violin_1", "Violin_2"])

    payload = {
        "piece_std_name": "Symphony_9",
        "archive_id": 1,
        "source_files": ["file1.pdf"],
        "classifications": {}
    }

    response = client.post("/api/v1/classification/1", json=payload)
    
    assert response.status_code == 400
    detail = response.json()["detail"]
    assert detail["message"] == "File collision detected. The configurations lacked rename/overwrite strategies."
    assert "Violin_1" in detail["missing_names"]
    assert "Violin_2" in detail["missing_names"]

@patch("backend.api.dependencies.permissions.check_archive_role")
@patch("backend.api.routes.classification.classify")
def test_classification_endpoint_not_found(mock_classify, mock_check_role):
    mock_check_role.return_value = MagicMock()
    mock_classify.side_effect = FileNotFoundError("Piece folder not found")

    payload = {
        "piece_std_name": "Symphony_9",
        "archive_id": 1,
        "source_files": [],
        "classifications": {}
    }

    response = client.post("/api/v1/classification/1", json=payload)
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Piece folder not found"

@patch("backend.api.dependencies.permissions.check_archive_role")
def test_classification_endpoint_mismatched_archive_id(mock_check_role):
    mock_check_role.return_value = MagicMock()
    
    payload = {
        "piece_std_name": "Symphony_9",
        "archive_id": 99,  # Mismatched! URL is 1
        "source_files": [],
        "classifications": {}
    }

    response = client.post("/api/v1/classification/1", json=payload)
    
    assert response.status_code == 400
    assert response.json()["detail"] == "Archive ID in URL does not match the ClassificationJob payload."

