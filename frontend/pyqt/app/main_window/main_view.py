from PyQt6 import QtWidgets, QtCore, QtGui

from frontend.pyqt.app.config.constants import CLIENT_VERSION, ICON_PATH
from frontend.pyqt.app.selectors.individual_selection_view import IndividualSelectionView
from frontend.pyqt.app.selectors.multiple_selection_view import MultipleSelectionView
from frontend_pyqt.main_window import Main_window
from frontend_pyqt.pop_up_windows.yes_no_window import YesNoWindow

class MainView(QtWidgets.QMainWindow):
    logout = QtCore.pyqtSignal()
    show_preferences = QtCore.pyqtSignal()
    show_presets = QtCore.pyqtSignal()
    show_about_us = QtCore.pyqtSignal()
    show_add_piece = QtCore.pyqtSignal()
    show_update_piece = QtCore.pyqtSignal()
    show_delete_piece = QtCore.pyqtSignal()
    show_add_scores_to_piece = QtCore.pyqtSignal()
    export_dossier = QtCore.pyqtSignal()
    clasify_scores = QtCore.pyqtSignal()
    delete_junk_files = QtCore.pyqtSignal()
    save_pieces_preset = QtCore.pyqtSignal()

    def __init__(self):
        super(MainView,self).__init__() #Create the Main_window Object callin QMainWindow constructor(i think)

        container = QtWidgets.QWidget()
        container_layout = QtWidgets.QVBoxLayout()
        
        #Space
        container_layout.setSpacing(20)
        container_layout.setContentsMargins(20,0,20,20)

        self.individual_selection_window = IndividualSelectionView()
        self.multiple_selection_window = MultipleSelectionView()
        self.selectors = QtWidgets.QStackedWidget()
        self.selectors.addWidget(self.individual_selection_window)
        self.selectors.addWidget(self.multiple_selection_window)

        self.setMenuBar(self.create_menu_bar())

        container_layout.addLayout(self.create_buttons_for_selectors())
        container_layout.addWidget(self.selectors)
        container.setLayout(container_layout)

               
        self.setCentralWidget(container)
        self.setWindowTitle("AMRV archive manager client v" + str(CLIENT_VERSION))
        self.setWindowIcon(QtGui.QIcon(ICON_PATH))
    

    def create_menu_bar(self):
        """Crete the menu bar"""
        logout_opt = QtGui.QAction(self.tr("Logout"),self)
        logout_opt.triggered.connect(self.logout.emit)

        preferences_opt = QtGui.QAction(self.tr("Preferences"),self)
        preferences_opt.triggered.connect(self.show_preferences.emit)

        presets_opt = QtGui.QAction(self.tr("Presets"),self)
        presets_opt.triggered.connect(self.show_presets.emit)

        #Create the submenus for save and load pieces presets
        self._save_pieces_preset_opt = QtGui.QAction(self.tr("Save pieces preset"),self)
        self._save_pieces_preset_opt.triggered.connect(self.save_pieces_preset.emit)

        self._load_pieces_preset_opt = QtWidgets.QMenu(self.tr("Load pieces preset"),self)
        #self._load_pieces_preset_opt.triggered.connect(lambda: None)


        add_score_opt = QtGui.QAction(self.tr("Add piece"),self)
        add_score_opt.triggered.connect(self.show_add_piece.emit)

        modify_score_opt = QtGui.QAction(self.tr("Modify piece"),self)
        modify_score_opt.triggered.connect(self.show_update_piece.emit)

        delete_score_opt = QtGui.QAction(self.tr("Delete piece"),self)
        delete_score_opt.triggered.connect(self.show_delete_piece.emit)

        add_scores_to_piece_opt = QtGui.QAction(self.tr("Add scores to piece"),self)
        add_scores_to_piece_opt.triggered.connect(self.show_add_scores_to_piece.emit)
        
        export_dossier_opt = QtGui.QAction(self.tr("Export dossier"),self)
        export_dossier_opt.triggered.connect(self.export_dossier.emit)
        
        clasify_scores_opt = QtGui.QAction(self.tr("Classify scores"),self)
        clasify_scores_opt.triggered.connect(self.clasify_scores.emit)

        delete_junk_files_opt = QtGui.QAction(self.tr("Delete junk files"),self)
        delete_junk_files_opt.triggered.connect(self.delete_junk_files.emit)

        about_opt = QtGui.QAction(self.tr("About us"),self)
        about_opt.triggered.connect(self.show_about_us.emit)


        menu = self.menuBar()
        if isinstance(menu,QtWidgets.QMenuBar):
            user_menu = menu.addMenu(self.tr("User"))
            if user_menu:
                user_menu.addAction(logout_opt)

            config_menu = menu.addMenu(self.tr("Configuration"))
            if config_menu:
                config_menu.addActions([preferences_opt,
                                        presets_opt])
                
            edit_menu = menu.addMenu(self.tr("Edit"))
            if edit_menu:
                edit_menu.addActions([self._save_pieces_preset_opt])
                edit_menu.addMenu(self._load_pieces_preset_opt)

            archive_menu = menu.addMenu(self.tr("Pieces"))
            if archive_menu:
                archive_menu.addActions([add_score_opt,
                                        modify_score_opt,
                                        delete_score_opt,
                                        menu.addSeparator(),
                                        add_scores_to_piece_opt,
                                        menu.addSeparator(),
                                        clasify_scores_opt])
            
            database_menu = menu.addMenu(self.tr("Database"))
            if database_menu:
                database_menu.addActions([export_dossier_opt])
            
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
    

    def clear_load_pieces_preset_menu(self):
        """Clear the load pieces preset menu"""
        self._load_pieces_preset_opt.clear()
    