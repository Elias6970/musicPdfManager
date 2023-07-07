from PyQt5 import QtWidgets,QtCore
from classes.db_manage import Db
from classes.constants import *

class MainWindow(QtWidgets.QMainWindow):
    actual_score = ""
    scores_added = []

    def __init__(self):

        super(MainWindow,self).__init__() #Create the MainWindow Object callin QMainWindow constructor(i think)
        
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
        
        
        #Get the list of all partitures in the db
        db_con = Db(DB_NAME)

        pieces_packed = db_con.get_with_like("cod","","cod,name")
        
        db_con.close_db() #close the connection
        
        self.list_of_pieces = []
        for i in pieces_packed:
            self.list_of_pieces.append(str(i[0])+"-"+i[1])
            
        #Auto Completer
        completer = QtWidgets.QCompleter(self.list_of_pieces)
        completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive) #type: ignore
        completer.setFilterMode(QtCore.Qt.MatchContains) #type: ignore

        self.piece_search_bar.setCompleter(completer)


        #Rest of widgets
        self.piece_lbl = QtWidgets.QLabel()
        self.part_search = QtWidgets.QComboBox()
        #self.part_search.setEditable(True)
        self.add_create_buttons = self.create_two_buttons("Add","Create Pdf")
        self.part_search.addItems(OPTIONS_OF_INSTRUMENTS)
        

        #Add the widgets to the layout
        search_bars_layout.addWidget(self.piece_search_bar)
        search_bars_layout.addWidget(self.piece_lbl)
        search_bars_layout.addWidget(self.part_search)
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
    def validate_selection(self,text):
        if text in self.list_of_pieces:
            self.piece_lbl.setText(text)
            self.actual_score = text

            #D
            for i in range(self.part_search.count()):
                self.part_search.removeItem(0)
            return True

    #Add the score to the list of added scores an update it in the labels list
    def add_score(self):
        if self.validate_selection(self.actual_score):
            score_to_add = self.actual_score+"->"+self.part_search.currentText()
            self.scores_added.append(score_to_add)
            
            #Update the labels of the down scores
            item = QtWidgets.QLabel(score_to_add)
            self.status_console_layout.addWidget(item)
    
    
    def create_pdf(self):
        pass

    def mv_back_preview(self):
        pass

    def mv_forward_preview(self):
        pass

