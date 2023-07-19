from PyQt5 import QtWidgets,QtCore
import PyPDF2
from classes.constants import *
from classes.files_manage import *
from gui.other_windows import *

class MainWindow(QtWidgets.QMainWindow):
    actual_score:Dir #Dir
    score_parts_added = [] #List of Files

    def __init__(self):

        super(MainWindow,self).__init__() #Create the MainWindow Object callin QMainWindow constructor(i think)
        
        #Init the Archive 
        self.archive = Archivo("archivo AMRV","archivo.db",RELATIVE_ARCHIVE_PATH)

        self.setMenuBar(self.create_menu_bar())        

        up_zone = self.create_up_zone()

        self.scroll = self.create_status_console()


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
        self.setWindowTitle("AMRV archive manager")

    #Create the menu bar
    def create_menu_bar(self):
        a1 = QtWidgets.QAction("Option 1",self)
        a1.triggered.connect(self.mv_back_preview)
        a2 = QtWidgets.QAction("Option 2",self)
        a2.triggered.connect(self.mv_forward_preview)
        menu = self.menuBar()
        file_menu = menu.addMenu("File").addAction(a1)
        edit_menu = menu.addMenu("Edit").addAction(a2)

        return menu


    #Create two buttons in a horizontal layout
    def create_two_buttons(self,btn1,btn2):
        obj = QtWidgets.QWidget()

        btn_left = QtWidgets.QPushButton(btn1)
        btn_right = QtWidgets.QPushButton(btn2)

        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(btn_left)
        hbox.addWidget(btn_right)
        
        if btn1.lower() == "add":
            btn_left.clicked.connect(self.add_score)
            btn_right.clicked.connect(self.create_pdf)
        else:
            btn_left.clicked.connect(self.mv_back_preview)
            btn_right.clicked.connect(self.mv_forward_preview)
        
        obj.setLayout(hbox)

        return obj


    #Create the up-left zone of the program(Two search bars, two labels and two buttons)
    def create_search_bars(self):
        search_bars = QtWidgets.QWidget()
        search_bars_layout = QtWidgets.QVBoxLayout()
        
        #Space
        #search_bars_layout.setSpacing(2)
        search_bars_layout.setContentsMargins(0,0,0,0)
        
        #All widgets
        self.piece_search_bar = QtWidgets.QLineEdit()
        self.piece_search_bar.setPlaceholderText("Buscar partitura")
        self.piece_search_bar.textChanged.connect(self.validate_selection) #type: ignore
            
        self.pieces_names = [os.path.basename(i.path) for i in self.archive.pieces_in_dirs]

        #Auto Completer
        completer = QtWidgets.QCompleter(self.pieces_names)
        completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive) #type: ignore
        completer.setFilterMode(QtCore.Qt.MatchContains) #type: ignore

        self.piece_search_bar.setCompleter(completer)


        #Rest of widgets
        self.piece_lbl = QtWidgets.QLabel()
        self.part_combo_box = QtWidgets.QComboBox()
        
        #self.part_combo_box.addItems(self.option_of_instruments(21))

        self.add_create_buttons = self.create_two_buttons("Add","Create Pdf")
        

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

        scroll_arrows = self.create_two_buttons("<",">")
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
    

    #Create in the lower partthe block of text where will appear the scores added
    def create_status_console(self):
        self.status_console = QtWidgets.QWidget()
        self.status_console_layout = QtWidgets.QVBoxLayout()
        self.status_console_layout.setSpacing(0)

        #Create the labels that apear in the list
        self.status_console.setLayout(self.status_console_layout)

        #Scroll zone for the scores
        scroll = QtWidgets.QScrollArea()
        scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn) #type: ignore
        scroll.setAlignment(QtCore.Qt.AlignTop) #type: ignore
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.status_console)

        return scroll

    
    #Check if the piece selected is equals to one on the list
    def validate_selection(self,text,new_check=True):
        for i in self.archive.pieces_in_dirs:
            if text == os.path.basename(i.path):
                self.piece_lbl.setText(text)
                self.actual_score = i

                if new_check:
                    self.set_option_of_instruments(i.scores)

                return True


    #Add the score to the list of added scores an update it in the labels list
    def add_score(self):
        #Stops the user if try to add a score no existing
        if self.validate_selection(os.path.basename(self.actual_score.path),False):
            
            self.score_parts_added.append(File(os.path.join(self.actual_score.path+DIR_SCORES,self.part_combo_box.currentText())))
            
            new_score_text = os.path.basename(self.actual_score.path)+"->"+self.part_combo_box.currentText()

            #Update the labels of the down scores
            new_score_lbl = QtWidgets.QLabel(new_score_text)
            self.status_console_layout.addWidget(new_score_lbl)
    

    #Set the option of the instruments to the combo box
    def set_option_of_instruments(self,scores):
        #Clear the old options
        for i in range(self.part_combo_box.count()):
                self.part_combo_box.removeItem(0)
        
        #Set the news
        self.part_combo_box.addItems(scores) 


    #Create one pdf with all the selected pdfs merged
    def create_pdf(self):
        file_dialog = QtWidgets.QFileDialog()
        #file_dialog.setFileMode(QtWidgets.QFileDialog.AnyFile)  # Allow selecting any file type
        file_dialog.setWindowTitle("Select Folder and File Name")
        file_dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)  # Set the dialog to save mode
        file_dialog.setDefaultSuffix(".pdf")
        #file_dialog.setDirectory("/")

        if file_dialog.exec_() == QtWidgets.QFileDialog.Accepted:
            
            try: #Check if the path is valid
                merged_pdf = PyPDF2.PdfWriter()
                for i in self.score_parts_added:
                    if os.path.exists(i.path):
                        merged_pdf.append(i.path)
                
                merged_pdf.write(file_dialog.selectedFiles()[0])
                merged_pdf.close()
            
            except Exception as e:
                print("Error: ",e)


    def mv_back_preview(self):
        self.hide()
        aaa = add_scores_window()
        aaa.show()
        self.show()
    def mv_forward_preview(self):
        pass