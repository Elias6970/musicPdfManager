from PyQt5 import QtCore, QtWidgets
import os
from classes.files_manage import Archive,Dir
from gui.error_window import Error_window


#Abstract window that have: (Is a false abstract window but it used like that)
#   a search bar linked to all scores in the archive directory
#   a lbl with the score selected
#   btn1 that you can select the lbl and you set the function
#   cancel btn that exits
class Abstract_serch_bar_and_two_buttons_window(QtWidgets.QDialog):

    def __init__(self,archive:Archive,window_title:str,btn_lbl:str,btn_function,parent=None):
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
        container_layout.addLayout(self.create_buttons_layout(btn_lbl,btn_function))
        
        self.setGeometry(0,0,400,200)
        self.setLayout(container_layout)


    def create_buttons_layout(self,btn1_lbl:str,btn_function):
        btns_layout = QtWidgets.QHBoxLayout()
        close_btn = QtWidgets.QPushButton("Close") #traducir
        func_btn = QtWidgets.QPushButton(btn1_lbl) #traducir

        close_btn.clicked.connect(self.close)
        func_btn.clicked.connect(btn_function)
        
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
        return False

    def close(self):
        self.hide()


#Abstract class that shows a window with:
#Parameters:
#   archive: Archive object of the archive
#   window_title: window string title
#   btn_lbl: text for the button that make something
#   checkboxes_names: strings of the names of the checkboxes. They are stored 
#                     in a dictionary with {"String in checkboxes_names",QtWidgets.QCheckbox}
#   btn_function: pointer to the function linked to the button
#   close_function: pointer to close function. By default is the close of the class
#Window parts:
#   4 fields to fill(code,name,author,type)
#   Two buttons(add the piece, close the window)
#   handwritten checkbox TODO: add posibility to not add scores
#   
class Abstract_fields_window(QtWidgets.QDialog):
    def __init__(self,archive:Archive,window_title:str,btn_lbl:str,checkboxes_names:list[str],btn_function,close_function=None,parent=None):
        super(Abstract_fields_window,self).__init__(parent=parent)
        
        self.setWindowTitle(window_title) #traducir

        self.archive = archive
        
        self.checkboxes_names = checkboxes_names #names of the checkboxes
        
        self.setWindowModality(QtCore.Qt.WindowModal) #type: ignore

        container_layout = QtWidgets.QVBoxLayout()
        
        #Space
        container_layout.setSpacing(0)
        container_layout.setContentsMargins(20,0,20,20)

        container_layout.addLayout(self.create_fields_layout())
        container_layout.addLayout(self.create_checkboxes_layout(checkboxes_names))
        container_layout.addLayout(self.create_buttons_layout(btn_lbl,btn_function,close_function))
        

        self.setGeometry(0,0,400,200)
        self.setLayout(container_layout)

        


    #Create the fields layout that is returned and added as a layout(not as a widget)
    def create_fields_layout(self):
        fields_layout = QtWidgets.QVBoxLayout()
 
        self.line_cod = QtWidgets.QLineEdit()
        self.line_name = QtWidgets.QLineEdit()
        self.line_author = QtWidgets.QLineEdit()
        self.line_type = QtWidgets.QLineEdit()

        
        cod_layout = QtWidgets.QHBoxLayout()
        cod_layout.addWidget(QtWidgets.QLabel("Cod  ")) #traducir
        cod_layout.addWidget(self.line_cod)

        name_layout = QtWidgets.QHBoxLayout()
        name_layout.addWidget(QtWidgets.QLabel("Name *  ")) #traducir
        name_layout.addWidget(self.line_name)

        author_layout = QtWidgets.QHBoxLayout()
        author_layout.addWidget(QtWidgets.QLabel("Author  ")) #traducir
        author_layout.addWidget(self.line_author)
        
        type_layout = QtWidgets.QHBoxLayout()
        type_layout.addWidget(QtWidgets.QLabel("Type  ")) #traducir
        type_layout.addWidget(self.line_type)

        fields_layout.addLayout(cod_layout)
        fields_layout.addLayout(name_layout)
        fields_layout.addLayout(author_layout)
        fields_layout.addLayout(type_layout)

        return fields_layout
    

    #Create the checkboxes handwritten,parted and digitalized
    def create_checkboxes_layout(self,names:list[str]):
        self.checkboxes_dict:dict[str,QtWidgets.QCheckBox] = {}
        layout = QtWidgets.QVBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignLeft) #type: ignore

        for i in names:
            self.checkboxes_dict[i] = QtWidgets.QCheckBox(i)
            layout.addWidget(self.checkboxes_dict[i])
            #self.checkboxes_dict.setToolTip("You must check this checkbox if the score is handwritten")#traducir
        
        return layout


    #Create the buttons layout
    def create_buttons_layout(self,btn_lbl:str,btn_function,close_function):
        btns_layout = QtWidgets.QHBoxLayout()
        close_btn = QtWidgets.QPushButton("Close") #traducir
        add_btn = QtWidgets.QPushButton(btn_lbl) #traducir

        if close_function != None:
            close_btn.clicked.connect(close_function)
        else:
            close_btn.clicked.connect(self.close)

        add_btn.clicked.connect(btn_function)
        
        btns_layout.addWidget(add_btn)
        btns_layout.addWidget(close_btn)
        
        return btns_layout
    
    
    #Clear the text in all the fiels
    def reset_fields(self):
        self.line_cod.setText(str(self.archive.get_next_cod()))
        self.line_name.clear()
        self.line_author.clear()
        self.line_type.clear()

        
    def close(self):
        self.hide()



#Search bar + autocompleter that shows the score selected
class Score_search_bar(QtWidgets.QLineEdit):
    def __init__(self, pieces_in_dirs:list[Dir],verify_function,parent=None) -> None:
        super(Score_search_bar,self).__init__(parent)

        self.setContentsMargins(0,0,0,0)
        self.setPlaceholderText("Search score") #traducir
        self.textChanged.connect(lambda: verify_function(self.text()))

        self.pieces_names:list[str] = [os.path.basename(i.path) for i in pieces_in_dirs]

        #Auto Completer
        self.auto_completer = QtWidgets.QCompleter(self.pieces_names)
        self.auto_completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive) #type: ignore
        self.auto_completer.setFilterMode(QtCore.Qt.MatchContains) #type: ignore
        
        self.setCompleter(self.auto_completer)

    #Update the autocompleter list of the search bar
    def update_autocompleter_scores(self,pieces_in_dirs:list[Dir]):
        self.pieces_names = [os.path.basename(i.path) for i in pieces_in_dirs]
        self.auto_completer.setModel(QtCore.QStringListModel(self.pieces_names))


"""
Pop up a window that shows a message with buttons
    If only_yes_btn:bool = 0 there are yes or no
    if only_yes_btn:bool = 1 there are only yes
"""
class Pop_up_window(QtWidgets.QDialog):
    def __init__(self,text:str,only_yes_btn:bool,parent) -> None:
        super(Pop_up_window,self).__init__(parent)

        self.btn_confirm_pressed = False #This values become true when no button is pressed

        self.setWindowModality(QtCore.Qt.WindowModal) #type: ignore

        container_layout = QtWidgets.QVBoxLayout()

        #labels
        warning_lbl = QtWidgets.QLabel(text)
        container_layout.addWidget(warning_lbl)
        
        
        btn_layout = QtWidgets.QHBoxLayout()


        if only_yes_btn == False:
            yes_btn = QtWidgets.QPushButton("Yes") #traducir
            no_btn = QtWidgets.QPushButton("No") #traducir
            yes_btn.clicked.connect(self.confirm)
            no_btn.clicked.connect(self.no)
            btn_layout.addWidget(yes_btn)
            btn_layout.addWidget(no_btn)

            confirmation_lbl = QtWidgets.QLabel("Do you want to keep adding it?")#traducir
            container_layout.addWidget(confirmation_lbl)
        
        else:
            confirm_btn = QtWidgets.QPushButton("Ok") #traducir
            confirm_btn.clicked.connect(self.confirm)
            btn_layout.addWidget(confirm_btn)

        
        container_layout.addLayout(btn_layout)


        #self.setGeometry(0,0,400,200)
        self.setLayout(container_layout)

        self.exec_()

    def confirm(self):
        self.btn_confirm_pressed = True
        self.hide()
    
    def no(self):
        self.hide()

#Scroll area where you can add QLabels 
class Status_console(QtWidgets.QScrollArea):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        status_console = QtWidgets.QWidget()
        self.status_console_layout = QtWidgets.QVBoxLayout()
        self.status_console_layout.setSpacing(0)

        #Create the labels that apear in the list
        status_console.setLayout(self.status_console_layout)


        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn) #type: ignore
        self.setAlignment(QtCore.Qt.AlignTop) #type: ignore
        self.setWidgetResizable(True)
        self.setWidget(status_console)

    def add_lbl(self,lbl:QtWidgets.QLabel) -> None:
        self.status_console_layout.addWidget(lbl)