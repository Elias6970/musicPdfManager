from PyQt6 import QtWidgets,QtCore
from frontend_pyqt.elements.score_search_bar import ScoreSearchBar
from backend.app.files_management.archive import Archive

#Abstract window that have: (Is a false abstract window but it used like that)
#   a search bar linked to all scores in the archive directory
#   a lbl with the score selected
#   btn1 that you can select the lbl and you set the function
#   cancel btn that exits
#   NEED TO ADD THE TEXT TO THE self.func_btn FOR EVERY INSTANCE 
#   NEED TO ADD THE WINDOW TITLE USING self.setWindowTitle
class AbstractSerchBarAndTwoButtonsWindow(QtWidgets.QDialog):

    def __init__(self,archive:Archive,btn_function,parent=None):
        super(AbstractSerchBarAndTwoButtonsWindow,self).__init__(parent)
        
        #self.setWindowTitle(window_title) #traducir

        self.archive = archive
        self.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        
        container_layout = QtWidgets.QVBoxLayout()
        
        #Space
        container_layout.setSpacing(0)
        
        self.search_bar = ScoreSearchBar(self.archive.pieces.get_parsed_names(),self.validate_selection) # type: ignore
        self.piece_lbl = QtWidgets.QLabel()
        
        container_layout.addWidget(self.search_bar)
        container_layout.addWidget(self.piece_lbl)
        container_layout.addLayout(self.create_buttons_layout(btn_function))
        
        #self.setGeometry(0,0,400,200)
        self.setFixedSize(400,100)
        self.setLayout(container_layout)


    def create_buttons_layout(self,btn_function):
        btns_layout = QtWidgets.QHBoxLayout()
        close_btn = QtWidgets.QPushButton(self.tr("Close")) #traducir
        self.func_btn = QtWidgets.QPushButton("Action") #traducir

        close_btn.clicked.connect(self.close)
        self.func_btn.clicked.connect(btn_function)
        
        btns_layout.addWidget(self.func_btn)
        btns_layout.addWidget(close_btn)
        
        return btns_layout

    
    #Update the autocompleter list of the search
    def update_autocompleter_scores(self):
        self.search_bar.update_autocompleter_scores(self.archive.pieces.get_parsed_names()) #type: ignore
    
    
    #Check if the piece selected is equals to one on the list
    def validate_selection(self,text):
        for i in self.search_bar.pieces_parsed_names:
            if text == i:
                self.piece_lbl.setText(text)
                return True
        return False

    def close(self):
        self.hide()