import os, sys

from PyQt6 import QtCore, QtWidgets, QtGui

from frontend.pyqt.app.api_client.archives_api_client import ArchivesApiClient
from frontend.pyqt.app.api_client.base_api_client_factory import get_base_client
from frontend.pyqt.app.config.session_manager import SessionManager
from frontend.pyqt.app.main_window.main_view import MainView
from frontend.pyqt.app.models.generated_models import ArchivePublic

from frontend.pyqt.app.selectors.individual_selection_controller import IndividualSelectionController
from frontend.pyqt.app.selectors.multiple_selection_controller import MultipleSelectionController

from frontend.pyqt.app.archive_crud.create_archive.create_archive_view import CreateArchiveView
from frontend.pyqt.app.archive_crud.create_archive.create_archive_controller import CreateArchiveController
from frontend.pyqt.app.archive_crud.delete_archive.delete_archive_view import DeleteArchiveView
from frontend.pyqt.app.archive_crud.delete_archive.delete_archive_controller import DeleteArchiveController
from frontend.pyqt.app.archive_crud.update_archive.update_archive_view import UpdateArchiveView
from frontend.pyqt.app.archive_crud.update_archive.update_archive_controller import UpdateArchiveController

from frontend.pyqt.app.piece_crud.create_piece.create_piece_controller import CreatePieceController
from frontend.pyqt.app.piece_crud.create_piece.create_piece_view import CreatePieceView
from frontend.pyqt.app.piece_crud.delete_piece.delete_piece_controller import DeletePieceController
from frontend.pyqt.app.piece_crud.delete_piece.delete_piece_view import DeletePieceView
from frontend.pyqt.app.piece_crud.update_piece.update_piece_controller import UpdatePieceController
from frontend.pyqt.app.piece_crud.update_piece.update_piece_view import UpdatePieceView

from frontend.pyqt.app.score_classifier.piece_selector.piece_selector_controller import PieceSelectorController
from frontend.pyqt.app.score_classifier.piece_selector.piece_selector_view import PieceSelectorView

from frontend.pyqt.app.preferences.preferences_controller import PreferencesController
from frontend.pyqt.app.preferences.preferences_view import PreferencesView
from frontend.pyqt.app.instruments_presets.list_instruments_presets.list_instruments_presets_controller import ListInstrumentsPresetsController
from frontend.pyqt.app.instruments_presets.list_instruments_presets.list_instruments_presets_view import ListInstrumentsPresetsView

from frontend.pyqt.app.login.login_view import LoginView
from frontend.pyqt.app.login.login_controller import LoginController
from frontend.pyqt.app.api_client.users_api_client import UsersApiClient
from frontend.pyqt.app.users_crud.users_controller import UsersController
from frontend.pyqt.app.users_crud.users_view import UsersView

from frontend.pyqt.app.pop_up_windows.about_us_view import AboutUsView

class MainController(QtCore.QObject):
    def __init__(self, view:MainView):
        super().__init__()
        self.view = view
        self.session = SessionManager()

        self.change_language(self.session.get_language())

        self.archive_api_client = ArchivesApiClient(get_base_client(), self)
        self.archive_api_client.get_all_archives_success.connect(self._on_get_all_archives_success)
        
        self._previous_archive_index = -1    

        self.individual_selection_controller = IndividualSelectionController(self.view.individual_selection_window)
        self.multiple_selection_controller = MultipleSelectionController(self.view.multiple_selection_window)
        self.multiple_selection_controller.update_pieces_presets_menu_list.connect(self.update_pieces_presets_menu_list)
        
        # Check Auth first
        self._check_auth()

        #Connect signals
        self.view.archive_combobox.currentIndexChanged.connect(self._on_archive_combobox_changed)

        self.view.show_manage_users.connect(self.show_manage_users)

        self.view.logout.connect(self.logout)
        self.view.show_preferences.connect(self.show_preferences)
        self.view.show_presets.connect(self.show_presets)

        self.view.show_create_archive.connect(self.show_create_archive)
        self.view.show_delete_archive.connect(self.show_delete_archive)
        self.view.show_update_archive.connect(self.show_update_archive)

        self.view.show_about_us.connect(self.show_about_us)
        self.view.show_add_piece.connect(self.show_add_piece)
        self.view.show_update_piece.connect(self.show_update_piece)
        self.view.show_delete_piece.connect(self.show_delete_piece)
        self.view.clasify_scores.connect(self.clasify_scores)
        self.view.save_pieces_preset.connect(self.save_pieces_preset)

    
    def _check_auth(self):
        """Check if the user is authenticated, if not, show the login window"""
        if not self.session.is_logged_in():
            self._show_login()
        else:
            self._after_login_setup()

    def _show_login(self, error: str = ""):
        """Show the login window and handle the authentication process"""
        login_view = LoginView(self.view)
        login_controller = LoginController(login_view)
        # Assuming LoginController sets up token internally and dialog closes with accept()
        if not login_view.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            sys.exit(0)
        else:
            self._after_login_setup()
    
    
    def _after_login_setup(self):
        """Setup the archives and the presets (user related data)"""
        self._previous_archive_index = -1
        self.archive_api_client.get_all_archives()    

        #Refresh the selectors to load the data of the first archive
        self.individual_selection_controller.refresh()
        self.multiple_selection_controller.refresh()

    def logout(self):
        """Logout the user and show the login window"""
        self.session.clear_session()
        self._show_login()
    

    def _on_get_all_archives_success(self, items: list[ArchivePublic]):
        """Handle the successful retrieval of all archives and populate the selection combobox."""
        if not items:
            self.view.selectors.setEnabled(False)
            self.view.archive_combobox.setEnabled(False)
            self.view.archive_combobox.blockSignals(True)
            self.view.archive_combobox.clear()
            self.view.archive_combobox.blockSignals(False)

            QtWidgets.QMessageBox.information(
                self.view,
                self.tr("No Archives Available"),
                self.tr("There are no archives available. Please create an archive (Archive > Create Archive) to get started."),
                QtWidgets.QMessageBox.StandardButton.Ok
            )
            return
        self.view.selectors.setEnabled(True)    
        self.view.archive_combobox.blockSignals(True) #To avoid triggering the index change event while populating the combobox
        self.view.archive_combobox.clear()
        
        current_archive_id = self.session.get_archive_id()
        selected_idx = -1
        
        for i, archive in enumerate(items):
            self.view.archive_combobox.addItem(f"{archive.name} (ID: {archive.id})", userData=archive.id)
            if archive.id == current_archive_id:
                selected_idx = i
                
        if selected_idx >= 0:
            self.view.archive_combobox.setCurrentIndex(selected_idx)
            self._previous_archive_index = selected_idx
        else:
            # If no archive is currently selected or if the stored ID is invalid, default to the first one available
            self.view.archive_combobox.setCurrentIndex(0)
            self._previous_archive_index = 0
            self.session.set_archive_id(items[0].id)
            
        self.view.archive_combobox.setEnabled(True)
        self.view.archive_combobox.blockSignals(False)

    def _on_archive_combobox_changed(self, index: int):
        """Prompt to change the archive and clear progress."""
        if index < 0 or index == self._previous_archive_index:
            return

        reply = QtWidgets.QMessageBox.warning(
            self.view,
            self.tr("Change Archive"),
            self.tr("Changing the archive will clear any unsaved progress in the selectors.\nDo you want to proceed?"),
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
            QtWidgets.QMessageBox.StandardButton.No
        )

        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            new_id = self.view.archive_combobox.itemData(index)
            self.session.set_archive_id(int(new_id))
            self._previous_archive_index = index
            
            self.individual_selection_controller.refresh()
            self.multiple_selection_controller.refresh()
        else:
            self.view.archive_combobox.blockSignals(True)
            self.view.archive_combobox.setCurrentIndex(self._previous_archive_index)
            self.view.archive_combobox.blockSignals(False)



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


    def show_manage_users(self):
        view = UsersView()
        controller = UsersController(view)
        view.exec()

    #Show the config window
    def show_preferences(self):
        view = PreferencesView(self.view)
        controller = PreferencesController(view)
        view.exec()

    def show_presets(self):
        view = ListInstrumentsPresetsView(self.view)
        controller = ListInstrumentsPresetsController(view)
        view.exec()

    def show_create_archive(self):
        view = CreateArchiveView()
        controller = CreateArchiveController(view)
        if view.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            self.archive_api_client.get_all_archives()
        
    
    def show_delete_archive(self):
        view = DeleteArchiveView()
        controller = DeleteArchiveController(view)
        if view.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            self.archive_api_client.get_all_archives()
    
    def show_update_archive(self):
        view = UpdateArchiveView()
        controller = UpdateArchiveController(view)
        if view.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            self.archive_api_client.get_all_archives()

    #Show the add_scores_window hiding the main menu
    def show_add_piece(self):
        view = CreatePieceView()
        controller = CreatePieceController(view)
        view.exec()

    #Show the modifiy scores window hiding the main menu
    def show_update_piece(self):
        view = UpdatePieceView()
        controller = UpdatePieceController(view)
        view.exec()

    #Show delete score menu hiding main menu
    def show_delete_piece(self):
        view = DeletePieceView()
        controller = DeletePieceController(view)
        view.exec()

    #Show the window to classify the scores
    def clasify_scores(self):
        self.piece_selector_view = PieceSelectorView(self.view)
        self.piece_selector_controller = PieceSelectorController(self.piece_selector_view)
        self.piece_selector_view.exec()

    #Show about us window
    def show_about_us(self):
        view = AboutUsView(self.view)
        view.exec()

