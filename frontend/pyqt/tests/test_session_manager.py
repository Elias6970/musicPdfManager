import pytest
from unittest.mock import MagicMock, patch
from app.config.session_manager import SessionManager

@pytest.fixture
@patch("app.config.session_manager.QSettings")
def session_manager(mock_qsettings_class):
    """
    Fixture that provides a SessionManager instance with a mocked QSettings.
    This avoids writing test data to the actual OS registry/configuration files.
    """
    store = {}
    mock_settings = MagicMock()
    
    def set_value(key, value):
        store[key] = value
        
    def get_value(key, type=None):
        val = store.get(key)
        if val is None:
            if type == int: return 0
            if type == str: return ""
            return None
        if type is not None:
            try:
                return type(val)
            except ValueError:
                return val
        return val
        
    def contains(key):
        return key in store
        
    def clear():
        store.clear()
        
    mock_settings.setValue.side_effect = set_value
    mock_settings.value.side_effect = get_value
    mock_settings.contains.side_effect = contains
    mock_settings.clear.side_effect = clear
    
    mock_qsettings_class.return_value = mock_settings
    
    return SessionManager()


def test_initialization_sets_defaults(session_manager):
    assert session_manager.get_archive_id() == 1
    assert session_manager.get_language() == "en_US"
    # It should set the initial token from the file
    assert session_manager.get_jwt().startswith("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9")

def test_get_set_jwt(session_manager):
    session_manager.set_jwt("test_token_123")
    assert session_manager.get_jwt() == "test_token_123"

def test_get_set_archive_id(session_manager):
    session_manager.set_archive_id(42)
    assert session_manager.get_archive_id() == 42
    
def test_get_set_language(session_manager):
    session_manager.set_language("es_ES")
    assert session_manager.get_language() == "es_ES"

def test_is_logged_in_valid_token(session_manager):
    session_manager.set_jwt("real.jwt.token")
    assert session_manager.is_logged_in() is True

def test_is_logged_in_dummy_token(session_manager):
    session_manager.set_jwt("dummy_jwt_token_12345")
    assert session_manager.is_logged_in() is False

def test_is_logged_in_empty_token(session_manager):
    session_manager.set_jwt("")
    assert session_manager.is_logged_in() is False

def test_clear_session(session_manager):
    # Call clear session
    session_manager.clear_session()
    
    # Assert that the underlying QSettings.clear() method was invoked
    session_manager.settings.clear.assert_called_once()
