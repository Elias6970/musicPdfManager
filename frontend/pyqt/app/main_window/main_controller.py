import os, sys

from PyQt6 import QtCore, QtWidgets, QtGui

from frontend.pyqt.app.config.session_manager import SessionManager
from frontend.pyqt.app.main_window.main_view import MainView
from frontend.pyqt.app.selectors.individual_selection_controller import IndividualSelectionController
from frontend.pyqt.app.selectors.multiple_selection_controller import MultipleSelectionController


from frontend.pyqt.app.login.login_view import LoginView
from frontend.pyqt.app.login.login_controller import LoginController
from frontend.pyqt.app.api_client.users_api_client import UsersApiClient

class MainController(QtCore.QObject):
    def __init__(self, view:MainView):
        super().__init__()
        self.view = view
        self.session = SessionManager()
        #self.session.set_jwt("H")

        self.users_api_client = UsersApiClient(self)
        self.users_api_client.get_me_success.connect(self._on_auth_success)
        self.users_api_client.get_me_error.connect(self._show_login)

        # Check Auth first
        self._check_auth()

        self.individual_selection_controller = IndividualSelectionController(self.view.individual_selection_window)
        self.multiple_selection_controller = MultipleSelectionController(self.view.multiple_selection_window)

        self.change_language(self.session.get_language())


        #Load pieces_presets in the menu list
        self.multiple_selection_controller.get_pieces_presets_names() #To update the pieces presets names in the menu when a new preset is created

        #Connect signals
        self.multiple_selection_controller.update_pieces_presets_menu_list.connect(self.update_pieces_presets_menu_list)

        self.view.show_preferences.connect(self.show_preferences)
        self.view.show_presets.connect(self.show_presets)
        self.view.show_about_us.connect(self.show_about_us)
        self.view.show_add_piece.connect(self.show_add_piece)
        self.view.show_update_piece.connect(self.show_update_piece)
        self.view.show_delete_piece.connect(self.show_delete_piece)
        self.view.show_add_scores_to_piece.connect(self.show_add_scores_to_piece)
        self.view.save_pieces_preset.connect(self.save_pieces_preset)

    def _check_auth(self):
        """Check if the user is authenticated, if not, show the login window"""
        token = self.session.get_jwt()
        if not token:
            self._show_login()
        else:
            self.users_api_client.get_me()

    def _show_login(self, error: str = ""):
        """Show the login window and handle the authentication process"""
        login_view = LoginView(self.view)
        login_controller = LoginController(login_view)
        # Assuming LoginController sets up token internally and dialog closes with accept()
        if login_view.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            self.change_language(self.session.get_language())
            self.multiple_selection_controller.get_pieces_presets_names()
        else:
            sys.exit(0)

    def _on_auth_success(self, data: dict):
        # Already authenticated, proceed normally
        pass

    def change_language(self,language):
        """Change the language of all the windows"""
        translator = QtCore.QTranslator(self)

        #TODO: Change this to a function that return the path of the translation file, and also check if it exists, if not, show an error message and exit the program
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            path = os.path.join(sys._MEIPASS,"frontend","pyqt","translate",language,"compiled",language+".qm") #type:ignore
        else:
            path = os.path.join("frontend","pyqt","translate",language,"compiled",language+".qm")

        translator.load(path)

        app = QtWidgets.QApplication.instance()
        if app:
            app.installTranslator(translator)

    def save_pieces_preset(self):
        """Saves the pieces preset with the given name"""
        self.multiple_selection_controller.save_pieces_preset()
        self.multiple_selection_controller.get_pieces_presets_names() #To update the pieces presets names in the menu when a new preset is created


    def update_pieces_presets_menu_list(self, preset_names:list[str]):
        """Update the pieces presets list in the menu bar"""
        self.view.clear_load_pieces_preset_menu() #Clear the menu before updating it with the new presets names

        for i in preset_names:
            action = QtGui.QAction(i,self.view._load_pieces_preset_opt)
            action.triggered.connect(lambda _, i=i: self.multiple_selection_controller.load_pieces_preset(i))
            self.view._load_pieces_preset_opt.addAction(action)


    #Show the config window
    def show_preferences(self):
        #Preferences_window(False,self)
        pass

    def show_presets(self):
        #PresetsWindow(self)
        #self.multiple_selection_window.refresh_presets_list(keep_current_index=True)
        pass

    #Show the add_scores_window hiding the main menu
    def show_add_piece(self):
        # Add_piece_window(self.archive,self)
        # self.update_autocompleter_scores()
        pass

    #Show the modifiy scores window hiding the main menu
    def show_update_piece(self):
        # Modify_piece_window(self.archive,self)
        # self.update_autocompleter_scores()
        pass

    #Show the add to exisiting piece window
    def show_add_scores_to_piece(self):
        # Add_scores_to_existing_piece_window(self.archive,self)
        # self.update_autocompleter_scores()
        pass

    #Show delete score menu hiding main menu
    def show_delete_piece(self):
        # Delete_piece_window(self.archive,self)
        # self.update_autocompleter_scores()
        pass

    #Show the window to classify the scores
    def clasify_scores(self):
        #PieceSelectorToClassifyWindow(self.archive,self)
        #self.update_autocompleter_scores()
        pass

    #Show about us window
    def show_about_us(self):
        #About_us_window(self)
        pass

