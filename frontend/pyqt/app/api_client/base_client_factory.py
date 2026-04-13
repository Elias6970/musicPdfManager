from frontend.pyqt.app.api_client.base_client import BaseApiClient
from frontend.pyqt.app.config.session_manager import SessionManager

# We maintain a single global instance of BaseApiClient so that
# the underlying QNetworkAccessManager can connection-pool and share cookies/headers.
_base_client_instance = None

def get_base_client() -> BaseApiClient:
    """
    Returns a configured singleton instance of BaseApiClient.
    Automatically injects the current JWT token from the SessionManager.
    """
    global _base_client_instance
    
    if _base_client_instance is None:
        _base_client_instance = BaseApiClient()
        
    # Always pull the latest token in case it was updated by a login action
    session = SessionManager()
    token = session.get_jwt()
    if token:
        _base_client_instance.set_token(token)  
    return _base_client_instance
