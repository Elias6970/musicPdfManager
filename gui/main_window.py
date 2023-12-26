from PyQt5 import QtWidgets,QtCore
import PyPDF2
from classes.constants import *
from classes.files_manage import *
from gui.error_window import Error
from gui.abstract_windows import Score_search_bar,Status_console
from gui.add_piece_window import Add_piece_window
from gui.delete_piece_window import Delete_piece_window
from gui.modify_piece_window import Modify_piece_window
from gui.add_scores_to_existing_piece_window import Add_scores_to_existing_piece_window
from gui.score_classifier_window import Score_classifier_window,Piece_selector_to_classify_window



class Main_window(QtWidgets.QMainWindow):
    actual_score:Dir #Dir
    score_parts_added = [] #List of Print files

    def __init__(self):

        super(Main_window,self).__init__() #Create the Main_window Object callin QMainWindow constructor(i think)
        
        #Init the Archive 
        self.archive = Archive(DB_NAME,DB_FILE_NAME,RELATIVE_ARCHIVE_PATH)
        
        self.setMenuBar(self.create_menu_bar())        

        up_zone = self.create_up_zone()

        self.scroll = Status_console()

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
        preferences_opt = QtWidgets.QAction("Preferences",self) #traducir
        preferences_opt.triggered.connect(self.show_preferences_window)

        add_score_opt = QtWidgets.QAction("Add score",self) #traducir
        add_score_opt.triggered.connect(self.show_add_scores_menu)

        modify_score_opt = QtWidgets.QAction("Modify score",self) #traducir
        modify_score_opt.triggered.connect(self.show_modify_piece_menu)

        delete_score_opt = QtWidgets.QAction("Delete score",self) #traducir
        delete_score_opt.triggered.connect(self.show_delete_score_menu)

        add_score_to_piece_opt = QtWidgets.QAction("Add score to piece",self) #traducir
        add_score_to_piece_opt.triggered.connect(self.show_add_scores_to_existing_piece_window)
        
        export_dossier_opt = QtWidgets.QAction("Export dossier",self) #traducir
        export_dossier_opt.triggered.connect(self.export_dossier)
        
        clasify_scores_opt = QtWidgets.QAction("Clasify scores",self) #traducir
        clasify_scores_opt.triggered.connect(self.clasify_scores)

        about_opt = QtWidgets.QAction("About",self) #traducir
        about_opt.triggered.connect(self.about_opt_menu)

        menu = self.menuBar()
        menu.addMenu("File").addActions([preferences_opt]) #traducir

        menu.addMenu("Archive").addActions([add_score_opt,modify_score_opt,delete_score_opt,menu.addSeparator(),add_score_to_piece_opt,menu.addSeparator(),clasify_scores_opt]) #traducir
        
        menu.addMenu("Database").addActions([export_dossier_opt]) #traducir
        
        menu.addMenu("Help").addActions([about_opt])
        
        return menu


    #Create the zone with a combo box to the num of copies, add and create pdf buttons
    def create_add_zone(self):
        obj = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout()

        self.num_copies = QtWidgets.QComboBox()
        self.num_copies.setFixedWidth(50)
        self.num_copies.addItems([str(i+1) for i in range(MAX_COPIES)])
        
        btn1 = QtWidgets.QPushButton("Add") #traducir
        btn2 = QtWidgets.QPushButton("Create Pdf") #traducir

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
        search_bars_layout = QtWidgets.QVBoxLayout()
        
        #Space
        search_bars_layout.setContentsMargins(0,0,0,0)
        
        self.piece_search_bar = Score_search_bar(self.archive.pieces_in_dirs,self.validate_selection)

        #Rest of widgets
        self.piece_lbl = QtWidgets.QLabel()
        self.part_combo_box = QtWidgets.QComboBox()
        

        self.add_create_buttons = self.create_add_zone()
        

        #Add the widgets to the layout
        search_bars_layout.addWidget(self.piece_search_bar)
        search_bars_layout.addWidget(self.piece_lbl)
        search_bars_layout.addWidget(self.part_combo_box)
        search_bars_layout.addWidget(self.add_create_buttons)
        
        search_bars.setLayout(search_bars_layout)
    
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


        #Update the autocompleter list of the search bar
    def update_autocompleter_scores(self):
        self.archive.update_pieces_in_dirs()
        self.piece_search_bar.update_autocompleter_scores(self.archive.pieces_in_dirs)


    #Check if the piece selected is equals to one on the list
    def validate_selection(self,text):
        
        #Use the list pieces in dirs because we need to extract the score names
        for i in self.archive.pieces_in_dirs:
            if text == os.path.basename(i.path):
                self.piece_lbl.setText(text)
                self.actual_score = i

                self.set_option_of_instruments(i.scores)

                return True


    #Add the score to the list of added scores an update it in the labels list
    def add_score(self):
        #Stops the user if try to add a score no existing
        if self.validate_selection(os.path.basename(self.actual_score.path)):
            
            self.score_parts_added.append(Print_file(os.path.join(self.actual_score.path,DIR_SCORES,self.part_combo_box.currentText()),int(self.num_copies.currentText())))
            
            new_score_text = self.num_copies.currentText()+"x "+os.path.basename(self.actual_score.path)+"->"+self.part_combo_box.currentText()

            #Update the labels of the down scores
            new_score_lbl = QtWidgets.QLabel(new_score_text)
            #self.status_console_layout.addWidget(new_score_lbl)
            self.scroll.add_lbl(new_score_lbl)
    

    #Set the option of the instruments to the combo box
    def set_option_of_instruments(self,scores):
        #Clear the old options
        for i in range(self.part_combo_box.count()):
                self.part_combo_box.removeItem(0)
        
        #Set the news
        self.part_combo_box.addItems(scores) 


    #Display a window to select a location to save a pdf
    def dialog_window_select_new_pdf(self):
        file_dialog = QtWidgets.QFileDialog()
        
        file_dialog.setWindowTitle("Select Folder and File Name") #traducir
        file_dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)  # Set the dialog to save mode
        file_dialog.setDefaultSuffix(".pdf")

        if file_dialog.exec_() == QtWidgets.QFileDialog.Accepted:
            return file_dialog.selectedFiles()[0]
        else:
            return ""
        

    #Create one pdf with all the selected pdfs merged
    def create_pdf(self):
        pdf_path = self.dialog_window_select_new_pdf()
            
        try: #Check if the path is valid
            merged_pdf = PyPDF2.PdfWriter()
            for i in self.score_parts_added:
                if os.path.exists(i.path):
                    for j in range(i.copies): #Add the pdf the times that is selected in copies
                        merged_pdf.append(i.path)
            
            merged_pdf.write(pdf_path)
            merged_pdf.close()
        
        except Exception as e:
            Error.print_error(e)
        

    def mv_back_preview(self):
        pass

    def mv_forward_preview(self):
        pass

    def show_preferences_window(self):
        pass

    #Show the add_scores_window hiding the main menu
    def show_add_scores_menu(self):
        Add_piece_window(self.archive,self)
        self.update_autocompleter_scores()


    #Show the modifiy scores window hiding the main menu
    #TODO: modify menu
    def show_modify_piece_menu(self):
        Modify_piece_window(self.archive,self)
        self.update_autocompleter_scores()

    def show_add_scores_to_existing_piece_window(self):
        Add_scores_to_existing_piece_window(self.archive,self)
        self.update_autocompleter_scores()


    #Show delete score menu hiding main menu
    def show_delete_score_menu(self):
        Delete_piece_window(self.archive,self)
        self.update_autocompleter_scores()


    def clasify_scores(self):
        #list = [Dir(os.path.join(RELATIVE_ARCHIVE_PATH,"1604-HOLA")),Dir(os.path.join(RELATIVE_ARCHIVE_PATH,"1596-FERVOR"))]
        #actual_clasification = Score_classifier_window(list,self.archive.update_parted,self)
        Piece_selector_to_classify_window(self.archive,self)

    #Create a pdf dossier with a list of all the scores in the db as an index
    def export_dossier(self):
        extra_cover_text = QtWidgets.QInputDialog.getText(self,"Additional conver info","Enter additional info to be added to the cover:(max 9 chars)")[0] #traducir
        pdf_path = self.dialog_window_select_new_pdf()
        self.archive.export_pdf_dossier_to_print(pdf_path,extra_cover_text)

    #TODO
    def about_opt_menu(self):
        pass