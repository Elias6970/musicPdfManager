from PyQt6.QtCore import QObject
from PyQt6.QtWidgets import QMessageBox

from frontend.pyqt.app.api_client.base_api_client_factory import get_base_client
from frontend.pyqt.app.api_client.users_api_client import UsersApiClient
from frontend.pyqt.app.config.session_manager import SessionManager
from frontend.pyqt.app.models.generated_models import UserConfigCreatePublic
from frontend.pyqt.app.preferences.preferences_view import PreferencesView


# Dictionary of available languages
LANGUAGES = {
    "es_ES": "Español",
    "ca_VA": "Valencià",
    "en_US": "English",
}


class PreferencesController(QObject):
    """Controller for managing application preferences."""
    def __init__(self, view: PreferencesView, parent=None):
        super().__init__(parent)
        self.view = view
        self.session = SessionManager()
        self.users_api_client = UsersApiClient(get_base_client())
        
        # Connect signals
        self.view.save.connect(self.on_save_preferences)
        self.users_api_client.update_user_config_success.connect(self.on_update_user_config_success)
        self.users_api_client.update_user_config_error.connect(self.on_update_user_config_error)
        
        # Initialize the view
        self._fill_language_combobox()
        self._load_current_language()
    

    def _fill_language_combobox(self):
        """Fill the language combobox with available languages."""
        self.view.fill_language_combobox(LANGUAGES)
    

    def _load_current_language(self):
        """Load the current language from the session manager and set it in the view."""
        current_language = self.session.get_language()
        if current_language:
            self.view.set_selected_language(current_language)
        else:
            # Default to English if no language is set
            self.view.set_selected_language("en_US")
    

    def on_save_preferences(self):
        """Handle the save preferences signal from the view."""
        selected_language = self.view.get_selected_language()
        self.session.set_language(selected_language)     
        self._update_language_on_server(selected_language)
    
    
    def _update_language_on_server(self, language_code: str):
        """Update the user's language preference on the server.
        
        Args:
            language_code (str): The language code to save (e.g., 'es_ES', 'en_US')
        """
        user_config_update = UserConfigCreatePublic(language=language_code)
        print(f"Updating user config: {user_config_update}")
        self.users_api_client.update_user_config(user_config_update)
    

    def on_update_user_config_success(self, user_config):
        """Handle successful user config update from the server."""
        QMessageBox.information(
            self.view,
            self.view.tr("Success"),
            self.view.tr("Language preference saved successfully. You need to restart the application for changes to take effect.")
        )
        self.view.accept()
    

    def on_update_user_config_error(self, error_message: str):
        """Handle error when updating user config on the server."""
        QMessageBox.warning(
            self.view,
            self.view.tr("Error"),
            self.view.tr(f"Failed to save language preference: {error_message}")
        )
