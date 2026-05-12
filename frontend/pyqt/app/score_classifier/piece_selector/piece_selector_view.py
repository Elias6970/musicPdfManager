from PyQt6 import QtWidgets, QtCore

from app.elements.status_console import StatusConsole
from app.elements.score_search_bar import ScoreSearchBar
from app.elements.list_items.status_console_item_two_texts import StatusConsoleItemWithTwoTexts

class PieceSelectorView(QtWidgets.QDialog):
    """
    Dialog window to select pieces to classify with the score_classifier tool. 
    The user can add pieces to a list, and open the ScoreClassifier with the selected pieces. 
    """

    add_piece_signal = QtCore.pyqtSignal(str)
    classify_signal = QtCore.pyqtSignal()

    def __init__(self,parent=None) -> None:
        super().__init__(parent)

        self.setWindowTitle(self.tr("Select pieces"))

        #Gui
        container_layout = QtWidgets.QVBoxLayout()
        
        self.search_bar = ScoreSearchBar() 
        self.status_area = StatusConsole()

        #Butons
        btn_layout = QtWidgets.QHBoxLayout()

        add_btn = QtWidgets.QPushButton(self.tr("Add"))
        classify_btn = QtWidgets.QPushButton(self.tr("Classify"))
        add_btn.clicked.connect(lambda: self.add_piece_signal.emit(self.search_bar.text()))
        classify_btn.clicked.connect(lambda: self.classify_signal.emit())
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(classify_btn)

        container_layout.addWidget(self.search_bar)
        container_layout.addLayout(btn_layout)
        container_layout.addWidget(self.status_area)
        
        self.setLayout(container_layout)
        self.setGeometry(500,200,500,400)


    def add_item(self, piece:str, id:str, remove_list_function):
        """Add a Piece item to the list"""
        self.status_area.add_item(StatusConsoleItemWithTwoTexts("",
                                    piece,
                                    "",
                                    id,
                                    self.status_area.remove_item,
                                    remove_list_function))

    #Update the autocompleter list of the search bar
    def update_search_bar_autocompleter(self, pieces:list[str]):
        self.search_bar.update_autocompleter_scores(pieces)
    
    