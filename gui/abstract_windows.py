from PyQt5 import QtCore, QtWidgets
import os,shutil
from classes.files_manage import Archive,File,Dir
from classes.error import Error
from classes.constants import RELATIVE_ARCHIVE_PATH


#Abstract window that have: (Is a false abstract window but it used like that)
#   a search bar linked to all scores in the archive directory
#   a lbl with the score selected
#   btn1 that you can select the lbl and you set the function
#   cancel btn that exits
class Abstract_serch_bar_and_two_buttons_window(QtWidgets.QDialog):

    def __init__(self,archive:Archive,window_title:str,btn_lbl:str,parent=None):
        super(Abstract_serch_bar_and_two_buttons_window,self).__init__(parent)
        
        self.setWindowTitle(window_title) #traducir

        self.archive = archive
        self.setWindowModality(QtCore.Qt.WindowModal) #type: ignore
        
        container_layout = QtWidgets.QVBoxLayout()
        
        #Space
        container_layout.setSpacing(0)
        
        self.search_bar = Score_search_bar(self.archive.pieces_in_dirs,self.validate_selection)
        self.piece_lbl = QtWidgets.QLabel()
        
        container_layout.addWidget(self.search_bar)
        container_layout.addWidget(self.piece_lbl)
        container_layout.addLayout(self.create_buttons_layout(btn_lbl))
        
        self.setGeometry(0,0,400,200)
        self.setLayout(container_layout)

        self.exec_()

    def create_buttons_layout(self,btn1_lbl:str):
        btns_layout = QtWidgets.QHBoxLayout()
        close_btn = QtWidgets.QPushButton("Close") #traducir
        func_btn = QtWidgets.QPushButton(btn1_lbl) #traducir

        close_btn.clicked.connect(self.close)
        func_btn.clicked.connect(self.btn_function)
        
        btns_layout.addWidget(func_btn)
        btns_layout.addWidget(close_btn)
        
        return btns_layout

    
    #Update the autocompleter list of the search
    def update_autocompleter_scores(self):
        self.archive.update_pieces_in_dirs()
        self.search_bar.update_autocompleter_scores(self.archive.pieces_in_dirs)
    
    
    #Check if the piece selected is equals to one on the list
    def validate_selection(self,text):
        for i in self.search_bar.pieces_names:
            if text == i:
                self.piece_lbl.setText(text)
                return True

    def close(self):
        self.hide()

    #Acts like an abstract method
    def btn_function(self):
        pass


#Search bar + autocompleter + label that shows the score selected
class Score_search_bar(QtWidgets.QWidget):
    def __init__(self, pieces_in_dirs:list[Dir],verify_function:callable,parent=None) -> None:
        super(Score_search_bar,self).__init__(parent)

        search_bar_layout = QtWidgets.QVBoxLayout()
        
        #Space
        search_bar_layout.setContentsMargins(0,0,0,0)

        self.piece_search_bar = QtWidgets.QLineEdit()
        self.piece_search_bar.setPlaceholderText("Search score") #traducir
        #self.piece_search_bar.textChanged.connect(lambda: self.validate_selection(self.piece_search_bar.text(),False)) #type: ignore
        self.piece_search_bar.textChanged.connect(lambda: verify_function(self.piece_search_bar.text()))

        self.pieces_names:str = [os.path.basename(i.path) for i in pieces_in_dirs]

        #Auto Completer
        self.completer = QtWidgets.QCompleter(self.pieces_names)
        self.completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive) #type: ignore
        self.completer.setFilterMode(QtCore.Qt.MatchContains) #type: ignore

        self.piece_search_bar.setCompleter(self.completer)


        search_bar_layout.addWidget(self.piece_search_bar)

        self.setLayout(search_bar_layout)

    #Update the autocompleter list of the search bar
    def update_autocompleter_scores(self,pieces_in_dirs:list[Dir]):
        self.pieces_names = [os.path.basename(i.path) for i in pieces_in_dirs]
        self.completer.setModel(QtCore.QStringListModel(self.pieces_names))


