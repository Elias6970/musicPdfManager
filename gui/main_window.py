from PyQt6 import QtWidgets,QtGui,QtCore
from classes.constants.constants import DB_NAME, RELATIVE_ARCHIVE_PATH, ICON_PATH, VERSION
from classes.config import Configuration
from classes.files_management.archive import Archive
from classes.config import PLAIN_TEXT_CONFIG_PATH
from classes.printers.dossier import Dossier
from gui.error_window import Error_window
from gui.selectors.individual_selection_window import IndividualSelectionWindow
from gui.selectors.multiple_selection_window import MultipleSelectionWindow
from gui.piece_windows.add_piece_window import Add_piece_window
from gui.piece_windows.delete_piece_window import Delete_piece_window
from gui.piece_windows.modify_piece_window import Modify_piece_window
from gui.piece_windows.add_scores_to_existing_piece_window import Add_scores_to_existing_piece_window
from gui.score_classifier.piece_selector_to_classify_window import PieceSelectorToClassifyWindow
from gui.about_us_window import About_us_window
from gui.preferences_window import Preferences_window
from gui.presets.presets_window import PresetsWindow
from tools.delete_junk_files import delete_junk_files
import sys, os

class Main_window(QtWidgets.QMainWindow):
    def __init__(self):

        super(Main_window,self).__init__() #Create the Main_window Object callin QMainWindow constructor(i think)
        self.change_language(Configuration.name_to_cod_language(Configuration.get_language()))
        
        #Check if there is the config file and the paths exitsts
        while(not os.path.exists(PLAIN_TEXT_CONFIG_PATH) or not os.path.exists(Configuration.get_archive_path()) or not os.path.exists(Configuration.get_dossier_cover_path())):
            Preferences_window(True,self)

        #Init the Archive 
        self.archive = Archive(DB_NAME,RELATIVE_ARCHIVE_PATH())
        
        container = QtWidgets.QWidget()
        container_layout = QtWidgets.QVBoxLayout()
        
        #Space
        container_layout.setSpacing(20)
        container_layout.setContentsMargins(20,0,20,20)

        self.individual_selection_window = IndividualSelectionWindow(archive=self.archive)
        self.multiple_selection_window = MultipleSelectionWindow(archive=self.archive)
        self.selectors = QtWidgets.QStackedWidget()
        self.selectors.addWidget(self.individual_selection_window)
        self.selectors.addWidget(self.multiple_selection_window)

        self.setMenuBar(self.create_menu_bar())

        container_layout.addLayout(self.create_buttons_for_selectors())
        container_layout.addWidget(self.selectors)
        container.setLayout(container_layout)

               
        self.setCentralWidget(container)
        self.setWindowTitle("AMRV archive manager v" + str(VERSION)) #traducir
        self.setWindowIcon(QtGui.QIcon(ICON_PATH))


    def create_menu_bar(self):
        """Crete the menu bar"""
        preferences_opt = QtGui.QAction(self.tr("Preferences"),self) #traducir
        preferences_opt.triggered.connect(self.show_preferences_window)

        presets_opt = QtGui.QAction(self.tr("Presets"),self) #traducir
        presets_opt.triggered.connect(self.show_presets_window)

        #Create the submenus for save and load pieces presets
        self._save_pieces_preset_opt = QtGui.QAction(self.tr("Save pieces preset"),self) #traducir
        self._save_pieces_preset_opt.triggered.connect(lambda: (self.multiple_selection_window.save_pieces_preset(), self.update_pieces_presets_list()))

        self._load_pieces_preset_opt = QtWidgets.QMenu(self.tr("Load pieces preset"),self) #traducir
        #self._load_pieces_preset_opt.triggered.connect(lambda: None)

        #Load all the piecee presets in the menu
        self.update_pieces_presets_list()

        add_score_opt = QtGui.QAction(self.tr("Add score"),self) #traducir
        add_score_opt.triggered.connect(self.show_add_scores_menu)

        modify_score_opt = QtGui.QAction(self.tr("Modify score"),self) #traducir
        modify_score_opt.triggered.connect(self.show_modify_piece_menu)

        delete_score_opt = QtGui.QAction(self.tr("Delete score"),self) #traducir
        delete_score_opt.triggered.connect(self.show_delete_score_menu)

        add_score_to_piece_opt = QtGui.QAction(self.tr("Add score to piece"),self) #traducir
        add_score_to_piece_opt.triggered.connect(self.show_add_scores_to_existing_piece_window)
        
        export_dossier_opt = QtGui.QAction(self.tr("Export dossier"),self) #traducir
        export_dossier_opt.triggered.connect(self.export_dossier)
        
        clasify_scores_opt = QtGui.QAction(self.tr("Clasify scores"),self) #traducir
        clasify_scores_opt.triggered.connect(self.clasify_scores)

        delete_junk_files_opt = QtGui.QAction(self.tr("Delete junk files"),self)
        delete_junk_files_opt.triggered.connect(lambda: delete_junk_files(RELATIVE_ARCHIVE_PATH()))

        about_opt = QtGui.QAction(self.tr("About"),self) #traducir
        about_opt.triggered.connect(self.about_opt_menu)


        #If something happend can create an empty menu due to the casts to QMenuBar
        menu = self.menuBar()

        if isinstance(menu,QtWidgets.QMenuBar):
            config_menu = menu.addMenu(self.tr("Configuration"))
            if config_menu:
                config_menu.addActions([preferences_opt,
                                        presets_opt]) #traducir
                
            edit_menu = menu.addMenu(self.tr("Edit"))
            if edit_menu:
                edit_menu.addActions([self._save_pieces_preset_opt])
                edit_menu.addMenu(self._load_pieces_preset_opt)

            archive_menu = menu.addMenu(self.tr("Archive"))
            if archive_menu:
                archive_menu.addActions([add_score_opt,
                                        modify_score_opt,
                                        delete_score_opt,
                                        menu.addSeparator(),
                                        add_score_to_piece_opt,
                                        menu.addSeparator(),
                                        clasify_scores_opt]) #traducir
            
            database_menu = menu.addMenu(self.tr("Database"))
            if database_menu:
                database_menu.addActions([export_dossier_opt]) #traducir
            
            tools_menu = menu.addMenu(self.tr("Tools"))
            if tools_menu:
                tools_menu.addActions([delete_junk_files_opt])

            help_menu = menu.addMenu(self.tr("Help"))
            if help_menu:
                help_menu.addActions([about_opt])

        return menu


    def create_buttons_for_selectors(self) -> QtWidgets.QHBoxLayout:
        """
        Create two buttons in a row to change between windows.
        Returns an horizontal layout
        """
        main_layout = QtWidgets.QHBoxLayout()

        self.btn_individual_selection = QtWidgets.QPushButton(self.tr("Single selection"))
        self.btn_individual_selection.clicked.connect(lambda: (self.selectors.setCurrentWidget(self.individual_selection_window), self.change_style_selector_buttons()))
        self.btn_multiple_selection = QtWidgets.QPushButton(self.tr("Multiple selection"))
        self.btn_multiple_selection.clicked.connect(lambda: (self.selectors.setCurrentWidget(self.multiple_selection_window), self.change_style_selector_buttons()))

        main_layout.setSpacing(0)
        main_layout.addWidget(self.btn_individual_selection)
        main_layout.addWidget(self.btn_multiple_selection)

        #Simulate a button click to set the first window and set the style 
        self.btn_individual_selection.click()

        return main_layout

    def change_style_selector_buttons(self):
        """
        Change the style to the buttons to select between selectors.
        """
        clicked_sytle = """
            QPushButton {
                border: none;
                border-bottom: 2px solid #ffffff;  /* Only bottom border */
                background-color: #3c3c3c;    /* No background */
                border-top-left-radius: 15px;
                border-top-right-radius: 15px;
                padding: 3px;
                font-size: 13px;
                border-bottom: 2px solid #2980b9;
            }
        """
        not_clicked_style = """
            QPushButton {
                border: none;
                border-bottom: 2px solid #ffffff;  /* Only bottom border */
                background-color: transparent;    /* No background */
                border-top-left-radius: 15px;
                border-top-right-radius: 15px;
                padding: 3px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #313131;
            }
        """
        clicked = self.sender() 
        
        if clicked == self.btn_individual_selection:
            self.btn_individual_selection.setStyleSheet(clicked_sytle)
            self.btn_multiple_selection.setStyleSheet(not_clicked_style)

            #Disable the save and load pieces preset options
            self._save_pieces_preset_opt.setEnabled(False)
            self._load_pieces_preset_opt.setEnabled(False)

        else:
            self.btn_individual_selection.setStyleSheet(not_clicked_style)
            self.btn_multiple_selection.setStyleSheet(clicked_sytle)

            self._save_pieces_preset_opt.setEnabled(True)
            self._load_pieces_preset_opt.setEnabled(True)

    def center_on_screen(self):
        """
        enter the window in the middle of the screen.
        If any error ocurrs, it doesn't move the window
        """
        # Get the screen geometry
        screen = QtWidgets.QApplication.primaryScreen()
        if isinstance(screen, QtGui.QScreen):
            screen_geometry = screen.availableGeometry()
            screen_center = screen_geometry.center()

            # Get the window size (without decorations yet, because it's not shown)
            window_size = self.size()

            # Calculate top-left point so that window center = screen center
            x = screen_center.x() - window_size.width() // 2
            y = screen_center.y() - window_size.height() // 2

            self.move(x, y)


#####################################################################
#----------------------------APP LOGIC -----------------------------#
#####################################################################

    def update_autocompleter_scores(self):
        """Update the autocompleter in both selector windows"""
        self.individual_selection_window.update_autocompleter_scores()
        self.multiple_selection_window.update_autocompleter_scores()


    def change_language(self,language):
        """Change the language of all the windows"""
        translator = QtCore.QTranslator(self)

        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            path = os.path.join(sys._MEIPASS,"translate",language,"compiled",language+".qm") #type:ignore
        else:
            path = os.path.join("translate",language,"compiled",language+".qm")

        translator.load(path)

        app = QtWidgets.QApplication.instance()
        if app:
            app.installTranslator(translator)
    
    
    def update_pieces_presets_list(self):
        """Update the pieces presets list in the menu bar"""
        self._load_pieces_preset_opt.clear()  # Clear the existing actions

        for i in self.multiple_selection_window.piece_preset_manager.get_names():
            action = QtGui.QAction(i,self._load_pieces_preset_opt)
            action.triggered.connect(lambda _, i=i: self.multiple_selection_window.load_pieces_preset(i))
            self._load_pieces_preset_opt.addAction(action)
    

    #Create a pdf dossier with a list of all the scores in the db as an index
    def export_dossier(self):
        extra_cover = QtWidgets.QInputDialog.getText(self,self.tr("Additional conver info"),self.tr("Enter additional info to be added to the cover:(max 9 chars)")) #traducir
        if extra_cover[1]:
            pdf_path = QtWidgets.QFileDialog.getSaveFileName(self, 
                                                             self.tr("Select Folder and File Name"),
                                                             "",
                                                             "PDF Files (*.pdf);;All Files (*)")
            if not pdf_path[0]: 
                return

            #I think the code never enter here because getSaveFileName add the extension autocatically        
            if not pdf_path[0].endswith(".pdf"):
                pdf_path = (pdf_path[0] + ".pdf", pdf_path[1])
            
            try:
                Dossier.export_pdf_dossier_to_print(self.archive.db.get_all_to_print(),pdf_path[0],extra_cover[0])
            except ValueError as e:
                Error_window.print_error(message="Incorrect file name",e=e) #traducir
            except Exception as e:
                Error_window.print_error(e)

#####################################################################
#------------------------SHOW OTHER WINDOWS ------------------------#
#####################################################################
    #Show the config window
    def show_preferences_window(self):
        Preferences_window(False,self)

    def show_presets_window(self):
        PresetsWindow(self)
        self.multiple_selection_window.refresh_presets_list(keep_current_index=True)

    #Show the add_scores_window hiding the main menu
    def show_add_scores_menu(self):
        Add_piece_window(self.archive,self)
        self.update_autocompleter_scores()

    #Show the modifiy scores window hiding the main menu
    def show_modify_piece_menu(self):
        Modify_piece_window(self.archive,self)
        self.update_autocompleter_scores()

    #Show the add to exisiting piece window
    def show_add_scores_to_existing_piece_window(self):
        Add_scores_to_existing_piece_window(self.archive,self)
        self.update_autocompleter_scores()

    #Show delete score menu hiding main menu
    def show_delete_score_menu(self):
        Delete_piece_window(self.archive,self)
        self.update_autocompleter_scores()

    #Show the window to classify the scores
    def clasify_scores(self):
        PieceSelectorToClassifyWindow(self.archive,self)
        self.update_autocompleter_scores()

    #Show about us window
    def about_opt_menu(self):
        About_us_window(self)

