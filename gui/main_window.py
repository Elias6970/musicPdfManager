from PyQt5 import QtWidgets,QtGui,QtCore
from classes.constants import *
from classes.files_manage import *
from classes.config import PLAIN_TEXT_CONFIG_PATH
from classes.validate import Validate
from classes.printer import Printer,Dossier
from classes.error import NoScoresException
from gui.error_window import Error_window
from gui.abstract_windows import Score_search_bar,Status_console
from gui.add_piece_window import Add_piece_window
from gui.delete_piece_window import Delete_piece_window
from gui.modify_piece_window import Modify_piece_window
from gui.add_scores_to_existing_piece_window import Add_scores_to_existing_piece_window
from gui.score_classifier_window import Piece_selector_to_classify_window
from gui.about_us_window import About_us_window
from gui.preferences_window import Preferences_window

class Main_window(QtWidgets.QMainWindow):
    def __init__(self):

        super(Main_window,self).__init__() #Create the Main_window Object callin QMainWindow constructor(i think)
        self.change_language(Configuration.name_to_cod_language(Configuration.get_language()))
        
        #Check if there is the config file and the paths exitsts
        #IMPORTANTE: Solo comprueba que exista el archivo, el dossier no lo  mira
        while(not os.path.exists(PLAIN_TEXT_CONFIG_PATH) or not os.path.exists(Configuration.get_archive_path()) or not os.path.exists(Configuration.get_dossier_cover_path())):
            Preferences_window(True,self)

        #Init the Archive 
        self.archive = Archive(DB_NAME,RELATIVE_ARCHIVE_PATH())
        self.printer = Printer()

        self.setWindowIcon(QtGui.QIcon(ICON_PATH))

        self.setMenuBar(self.create_menu_bar())        

        up_zone = self.create_up_zone()

        self.scroll:Status_console = Status_console()

        container = QtWidgets.QWidget()
        container_layout = QtWidgets.QVBoxLayout()
        
        #Space
        container_layout.setSpacing(0)
        container_layout.setContentsMargins(20,0,20,20)

        container_layout.addWidget(up_zone)
        container_layout.addWidget(self.scroll)
        
        container.setLayout(container_layout)


        self.setCentralWidget(container)
        self.setGeometry(100,80,200,200)
        self.setWindowTitle("AMRV archive manager") #traducir


    #Create the menu bar
    def create_menu_bar(self):
        preferences_opt = QtWidgets.QAction(self.tr("Preferences"),self) #traducir
        preferences_opt.triggered.connect(self.show_preferences_window)

        add_score_opt = QtWidgets.QAction(self.tr("Add score"),self) #traducir
        add_score_opt.triggered.connect(self.show_add_scores_menu)

        modify_score_opt = QtWidgets.QAction(self.tr("Modify score"),self) #traducir
        modify_score_opt.triggered.connect(self.show_modify_piece_menu)

        delete_score_opt = QtWidgets.QAction(self.tr("Delete score"),self) #traducir
        delete_score_opt.triggered.connect(self.show_delete_score_menu)

        add_score_to_piece_opt = QtWidgets.QAction(self.tr("Add score to piece"),self) #traducir
        add_score_to_piece_opt.triggered.connect(self.show_add_scores_to_existing_piece_window)
        
        export_dossier_opt = QtWidgets.QAction(self.tr("Export dossier"),self) #traducir
        export_dossier_opt.triggered.connect(self.export_dossier)
        
        clasify_scores_opt = QtWidgets.QAction(self.tr("Clasify scores"),self) #traducir
        clasify_scores_opt.triggered.connect(self.clasify_scores)

        about_opt = QtWidgets.QAction(self.tr("About"),self) #traducir
        about_opt.triggered.connect(self.about_opt_menu)

        menu = self.menuBar()
        menu.addMenu(self.tr("Configuration")).addActions([preferences_opt]) #traducir

        menu.addMenu(self.tr("Archive")).addActions([add_score_opt,modify_score_opt,delete_score_opt,menu.addSeparator(),add_score_to_piece_opt,menu.addSeparator(),clasify_scores_opt]) #traducir
        
        menu.addMenu(self.tr("Database")).addActions([export_dossier_opt]) #traducir
        
        menu.addMenu(self.tr("Help")).addActions([about_opt])
        
        return menu


    #Create the zone with a combo box to the num of copies, add and create pdf buttons
    def create_add_zone(self):
        obj = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout()

        self.num_copies = QtWidgets.QComboBox()
        self.num_copies.setFixedWidth(50)
        self.num_copies.addItems([str(i+1) for i in range(MAX_COPIES)])
        
        btn1 = QtWidgets.QPushButton(self.tr("Add")) #traducir
        btn2 = QtWidgets.QPushButton(self.tr("Create Pdf")) #traducir

        btn1.clicked.connect(self.add_score)
        btn2.clicked.connect(self.create_pdf)

        layout.addWidget(self.num_copies)
        layout.addWidget(btn1)
        layout.addWidget(btn2)

        obj.setLayout(layout)
        return obj


    #Create two buttons in a horizontal layout
    def create_preview_buttons(self):
        obj = QtWidgets.QWidget()
        hbox = QtWidgets.QHBoxLayout()
        
        btn_left = QtWidgets.QPushButton("<")
        btn_right = QtWidgets.QPushButton(">")
        
        hbox.addWidget(btn_left)
        hbox.addWidget(btn_right)
        
        btn_left.clicked.connect(self.mv_back_preview)
        btn_right.clicked.connect(self.mv_forward_preview)
        
        obj.setLayout(hbox)

        return obj


    #Create the up-left zone of the program(Two search bars, two labels and two buttons)
    def create_search_bars(self):
        search_bars = QtWidgets.QWidget()
        select_zone_layout = QtWidgets.QVBoxLayout()
        search_bar_layout = QtWidgets.QHBoxLayout()
        check_box_layout = QtWidgets.QHBoxLayout()
        #Space
        select_zone_layout.setContentsMargins(0,0,0,0)
        search_bar_layout.setContentsMargins(0,0,0,0)
        
        #Refresh button
        self.refresh_button = QtWidgets.QPushButton()
        self.refresh_button.clicked.connect(self.refresh)

        try:
            if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
                img_path = os.path.join(sys._MEIPASS,'data','img') #type: ignore
            else:
                img_path = os.path.join('data','img')
                self.refresh_button.setIcon(QtGui.QIcon(os.path.join(img_path,'refresh.png')))
        except Exception:
            pass

        #Search bar
        self.piece_search_bar = Score_search_bar(self.archive.pieces.get_parsed_names(),self.set_option_of_instruments)

        #Rest of widgets
        self.only_digitalized_cb = QtWidgets.QCheckBox()
        self.only_digitalized_cb.clicked.connect(self.only_digitalized)
        only_digitalized_lbl = QtWidgets.QLabel(self.tr("Only digitalized")) #traducir
        self.piece_lbl = QtWidgets.QLabel()
        self.part_combo_box = QtWidgets.QComboBox()
        

        self.add_create_buttons = self.create_add_zone()
        

        #Add the widgets to the layout
        search_bar_layout.addWidget(self.refresh_button)
        search_bar_layout.addWidget(self.piece_search_bar)
        
        check_box_layout.addWidget(self.only_digitalized_cb)
        check_box_layout.addWidget(only_digitalized_lbl)
        check_box_layout.setAlignment(QtCore.Qt.AlignLeft) #type: ignore

        select_zone_layout.addLayout(search_bar_layout)
        select_zone_layout.addLayout(check_box_layout)
        select_zone_layout.addWidget(self.piece_lbl)
        select_zone_layout.addWidget(self.part_combo_box)
        select_zone_layout.addWidget(self.add_create_buttons)
        
        search_bars.setLayout(select_zone_layout)
    
        return search_bars    
    

    #Create the preview. This is going to be developed in the future. Now its not necessary
    def create_preview(self):
        preview = QtWidgets.QWidget()
        preview_layout = QtWidgets.QVBoxLayout()

        preview_layout.setSpacing(0)
        preview_layout.setContentsMargins(30,0,0,0)

        scroll_arrows = self.create_preview_buttons()
        preview_layout.addWidget(QtWidgets.QLabel("Aquí iríra la preview del pdf"))
        preview_layout.addWidget(scroll_arrows)

        preview.setLayout(preview_layout)

        return preview


    #Create the layout of all the up zone(search bars+preview)
    def create_up_zone(self):
        up = QtWidgets.QWidget()
        up_layout = QtWidgets.QHBoxLayout()

        up_layout.addWidget(self.create_search_bars())
        up_layout.addWidget(self.create_preview())

        up.setLayout(up_layout)
        
        return up

#####################################################################
#----------------------------APP LOGIC -----------------------------#
#####################################################################

    #Update the autocompleter list of the search bar
    def update_autocompleter_scores(self):
        #self.archive.update_pieces_in_dirs()
        self.piece_search_bar.update_autocompleter_scores(self.archive.pieces.get_parsed_names())
    
    
    #Set the option of the instruments to the combo box
    def set_option_of_instruments(self,text):
        #Clear the old options
        for i in range(self.part_combo_box.count()):
                self.part_combo_box.removeItem(0)

        #set instruments
        piece = Validate.select_window_validate_selection(text,self.archive.pieces.get_parsed_names())
        if not isinstance(piece,Dir_Error):
            try:
                piece.path = os.path.join(self.archive.archive_path,piece.name)
                scores = piece.get_scores()
                #Raise the error if the scores dir is empty
                if not scores:
                    raise NoScoresException()
                
                self.part_combo_box.setEnabled(True)
                self.part_combo_box.addItems(piece.get_scores())
                self.piece_lbl.setText(piece.name)
                self.printer.actual_piece = piece
            
            #if the piece is not in the digital archive
            except FileNotFoundError:
                self.part_combo_box.setEnabled(False)
                self.part_combo_box.insertItem(0,self.tr("NO DIGITALIZED")) #TRADUCIR
            except NoScoresException:
                self.part_combo_box.setEnabled(False)
                self.part_combo_box.insertItem(0,self.tr("NO SCORES")) #TRADUCIR



    #Add the score to the list of added scores an update it in the labels list
    def add_score(self):
        if self.part_combo_box.isEnabled() and self.printer.add_score(self.part_combo_box.currentText(),int(self.num_copies.currentText()),self.archive.pieces.get_parsed_names()):
            new_score_text = self.num_copies.currentText()+"x "+self.printer.actual_piece.name+"->"+self.part_combo_box.currentText()

            #Update the labels of the down scores
            new_score_lbl = QtWidgets.QLabel(new_score_text)
            #self.status_console_layout.addWidget(new_score_lbl)
            self.scroll.add_lbl(new_score_lbl)
    

    #Display a window to select a location to save a pdf
    def dialog_window_select_new_pdf(self):
        file_dialog = QtWidgets.QFileDialog()
        
        file_dialog.setWindowTitle(self.tr("Select Folder and File Name")) #traducir
        file_dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)  # Set the dialog to save mode
        file_dialog.setDefaultSuffix(".pdf")

        if file_dialog.exec_() == QtWidgets.QFileDialog.Accepted:
            return file_dialog.selectedFiles()[0]
        else:
            return ""


    #Create one pdf with all the selected pdfs merged
    def create_pdf(self):     
        try:
            if self.printer.pdfs_added:
                pdf_path = self.dialog_window_select_new_pdf()
                self.printer.create_pdf(pdf_path)
        
        except Exception as e:
            Error_window.print_error(e)


    #Refresh the list of pieces and delete the info in the printer  
    def refresh(self):
        self.scroll.clear()
        self.scroll.update()
        self.piece_search_bar.clear()
        self.piece_lbl.clear()

        self.printer = Printer()
        self.archive.update_pieces()


    #Controlls the pieces showed in the search bar
    def only_digitalized(self):
        if self.only_digitalized_cb.isChecked():
            self.piece_search_bar.update_autocompleter_scores(self.archive.pieces.get_digitalized_parsed_names())
        else:
            self.piece_search_bar.update_autocompleter_scores(self.archive.pieces.get_parsed_names())


    def mv_back_preview(self):
        pass

    def mv_forward_preview(self):
        pass


    def change_language(self,language):
        translator = QtCore.QTranslator(self)

        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            path = os.path.join(sys._MEIPASS,"translate",language,"compiled",language+".qm") #type:ignore
        else:
            path = os.path.join("translate",language,"compiled",language+".qm")

        translator.load(path)

        QtWidgets.QApplication.instance().installTranslator(translator)
    
  
#####################################################################
#------------------------SHOW OTHER WINDOWS ------------------------#
#####################################################################
    #Show the config window
    def show_preferences_window(self):
        Preferences_window(False,self)

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
        Piece_selector_to_classify_window(self.archive,self)
        self.update_autocompleter_scores()

    #Show about us window
    def about_opt_menu(self):
        About_us_window(self)

    #Create a pdf dossier with a list of all the scores in the db as an index
    def export_dossier(self):
        extra_cover_text = QtWidgets.QInputDialog.getText(self,self.tr("Additional conver info"),self.tr("Enter additional info to be added to the cover:(max 9 chars)"))[0] #traducir
        pdf_path = self.dialog_window_select_new_pdf()
        
        try:
            Dossier.export_pdf_dossier_to_print(self.archive.db.get_all_to_print(),pdf_path,extra_cover_text)
        except ValueError as e:
            Error_window.print_error(message="Incorrect file name",e=e) #traducir
        except Exception as e:
            Error_window.print_error(e)

