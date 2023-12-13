import os
from classes.files_manage import Dir
from PyQt5 import QtCore, QtWidgets

#TODO: tratar de eliminar la duplicacion de códgio de la search bar en main window. Actualmente nok puedo porque no se como actualizar el combo box de instrumentos
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
