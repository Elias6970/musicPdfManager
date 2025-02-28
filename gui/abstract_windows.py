from PyQt6 import QtCore, QtWidgets, QtGui
from classes.files_manage import Archive
import os


#Abstract window that have: (Is a false abstract window but it used like that)
#   a search bar linked to all scores in the archive directory
#   a lbl with the score selected
#   btn1 that you can select the lbl and you set the function
#   cancel btn that exits
#   NEED TO ADD THE TEXT TO THE self.func_btn FOR EVERY INSTANCE 
#   NEED TO ADD THE WINDOW TITLE USING self.setWindowTitle
class Abstract_serch_bar_and_two_buttons_window(QtWidgets.QDialog):

    def __init__(self,archive:Archive,btn_function,parent=None):
        super(Abstract_serch_bar_and_two_buttons_window,self).__init__(parent)
        
        #self.setWindowTitle(window_title) #traducir

        self.archive = archive
        self.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        
        container_layout = QtWidgets.QVBoxLayout()
        
        #Space
        container_layout.setSpacing(0)
        
        self.search_bar = Score_search_bar(self.archive.pieces.get_parsed_names(),self.validate_selection) # type: ignore
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
        #self.archive.update_pieces_in_dirs()
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


#Abstract class that shows a window with:
#Parameters:
#   archive: Archive object of the archive
#   window_title: window string title
#   btn_lbl: text for the button that make something
#   checkboxes_names: strings of the names of the checkboxes. They are stored 
#                     in a dictionary with {"String in checkboxes_names",QtWidgets.QCheckbox}
#                     that you can acced later to check if they are checked
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
        
        self.setWindowModality(QtCore.Qt.WindowModality.WindowModal)

        container_layout = QtWidgets.QVBoxLayout()
        
        #Space
        container_layout.setSpacing(5)
        container_layout.setContentsMargins(20,0,20,20)

        container_layout.addLayout(self.create_fields_layout())
        container_layout.addLayout(self.create_checkboxes_layout(checkboxes_names))
        container_layout.addLayout(self.create_buttons_layout(btn_lbl,btn_function,close_function))
        

        #self.setGeometry(0,0,400,200)
        self.setFixedSize(400,200)
        self.setLayout(container_layout)

        


    #Create the fields layout that is returned and added as a layout(not as a widget)
    def create_fields_layout(self):
        fields_layout = QtWidgets.QVBoxLayout()
 
        self.line_cod = QtWidgets.QLineEdit()
        self.line_name = QtWidgets.QLineEdit()
        self.line_author = QtWidgets.QLineEdit()
        self.line_type = QtWidgets.QLineEdit()

        
        cod_layout = QtWidgets.QHBoxLayout()
        cod_layout.addWidget(QtWidgets.QLabel(self.tr("Cod  "))) #traducir
        cod_layout.addWidget(self.line_cod)

        name_layout = QtWidgets.QHBoxLayout()
        name_layout.addWidget(QtWidgets.QLabel(self.tr("Name *  "))) #traducir
        name_layout.addWidget(self.line_name)

        author_layout = QtWidgets.QHBoxLayout()
        author_layout.addWidget(QtWidgets.QLabel(self.tr("Author  "))) #traducir
        author_layout.addWidget(self.line_author)
        
        type_layout = QtWidgets.QHBoxLayout()
        type_layout.addWidget(QtWidgets.QLabel(self.tr("Type  "))) #traducir
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
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)

        for i in names:
            self.checkboxes_dict[i] = QtWidgets.QCheckBox(i)
            layout.addWidget(self.checkboxes_dict[i])
            #self.checkboxes_dict.setToolTip("You must check this checkbox if the score is handwritten")#traducir
        
        return layout


    #Create the buttons layout
    def create_buttons_layout(self,btn_lbl:str,btn_function,close_function):
        btns_layout = QtWidgets.QHBoxLayout()
        close_btn = QtWidgets.QPushButton(self.tr("Close")) #traducir
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
        self.line_cod.setText(str(self.archive.db.get_next_cod()))
        self.line_name.clear()
        self.line_author.clear()
        self.line_type.clear()

        
    def close(self):
        self.hide()



#Search bar + autocompleter that shows the score selected
class Score_search_bar(QtWidgets.QLineEdit):
    def __init__(self, pieces_parsed_names:list[str],verify_function,parent=None) -> None:
        super(Score_search_bar,self).__init__(parent)

        self.setContentsMargins(0,0,0,0)
        self.setPlaceholderText(self.tr("Search score")) #traducir
        self.textChanged.connect(lambda: verify_function(self.text()))
        
        self.pieces_parsed_names =  pieces_parsed_names

        #Auto Completer
        self.auto_completer = QtWidgets.QCompleter(self.pieces_parsed_names)
        self.auto_completer.setCaseSensitivity(QtCore.Qt.CaseSensitivity.CaseInsensitive)
        self.auto_completer.setFilterMode(QtCore.Qt.MatchFlag.MatchContains)
        
        self.setCompleter(self.auto_completer)

    #Update the autocompleter list of the search bar
    def update_autocompleter_scores(self,pieces_parsed_names:list[str]):
        self.pieces_parsed_names =  pieces_parsed_names
        self.auto_completer.setModel(QtCore.QStringListModel(self.pieces_parsed_names))


"""
Pop up a window that shows a message with buttons
    If only_yes_btn:bool = 0 there are yes or no
    if only_yes_btn:bool = 1 there are only yes
"""
class Pop_up_window(QtWidgets.QDialog):
    def __init__(self,text:str,only_yes_btn:bool,parent) -> None:
        super(Pop_up_window,self).__init__(parent)

        self.btn_confirm_pressed = False #This values become true when no button is pressed

        self.setWindowModality(QtCore.Qt.WindowModality.WindowModal)

        container_layout = QtWidgets.QVBoxLayout()

        #labels
        warning_lbl = QtWidgets.QLabel(text)
        container_layout.addWidget(warning_lbl)
        
        
        btn_layout = QtWidgets.QHBoxLayout()


        if only_yes_btn == False:
            yes_btn = QtWidgets.QPushButton(self.tr("Yes")) #traducir
            no_btn = QtWidgets.QPushButton(self.tr("No")) #traducir
            yes_btn.clicked.connect(self.confirm)
            no_btn.clicked.connect(self.no)
            btn_layout.addWidget(yes_btn)
            btn_layout.addWidget(no_btn)

            confirmation_lbl = QtWidgets.QLabel(self.tr("Do you want to keep adding it?"))#traducir
            container_layout.addWidget(confirmation_lbl)
        
        else:
            confirm_btn = QtWidgets.QPushButton(self.tr("Ok")) #traducir
            confirm_btn.clicked.connect(self.confirm)
            btn_layout.addWidget(confirm_btn)

        
        container_layout.addLayout(btn_layout)


        self.setLayout(container_layout)

        self.exec()

    def confirm(self):
        self.btn_confirm_pressed = True
        self.hide()
    
    def no(self):
        self.hide()


#Item in the status console
# item_id: id to delete the item from a list
# remove_widget: function to remove the widget from the layout
# remove_from_list: function to remove the item from the list. (Used for the logic list to print)
class StatusConsoleItem(QtWidgets.QFrame):
    def __init__(self, piece_name:str, instrument:str, copies:str|int, item_id:int|str, remove_widget, remove_from_list,parent=None) -> None:
        super().__init__(parent)

        self.item_id = item_id

        self.piece_lbl = QtWidgets.QLabel(piece_name)
        self.instrument_lbl = QtWidgets.QLabel(instrument)
        self.piece_lbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        self.piece_lbl.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)
        self.instrument_lbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        self.instrument_lbl.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)
        bold_font = QtGui.QFont()
        bold_font.setBold(True)
        self.instrument_lbl.setFont(bold_font)

        piece_layout = QtWidgets.QVBoxLayout()
        piece_layout.setSpacing(0)
        piece_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        piece_layout.setContentsMargins(0,0,0,0)
        piece_layout.addWidget(self.piece_lbl)
        piece_layout.addWidget(self.instrument_lbl)


        self.copies_lbl = QtWidgets.QLabel(str(copies))
        self.copies_lbl.setContentsMargins(0,0,3,0)

        self.delete_btn = QtWidgets.QPushButton()
        self.delete_btn.setIcon(QtGui.QIcon(os.path.join("data","img","trash.png")))
        self.delete_btn.setFixedSize(20, 25)
        self.delete_btn.setStyleSheet("background-color: #ff5555")
        self.delete_btn.setSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Preferred)

        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(5,3,5,3)
        layout.addLayout(piece_layout)
        layout.addWidget(self.copies_lbl)
        layout.addWidget(self.delete_btn)
        
        self.setFrameShape(QtWidgets.QFrame.Shape.Box)
        self.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
        self.setLayout(layout)
        
        # Connect delete button
        #Remove the item from the StatusConsole and from the list of pdfs
        self.delete_btn.clicked.connect(lambda: remove_widget(self) or remove_from_list(self.item_id))


#Item in a list with two buttons and one lbl
#   name: name of the item. It's the identifier. Need to be unique
#   edit_func: function that is called when you press edit button. Recive the preset_name as parameter
#   delete_func: function that is called when you press delete button. Recive the preset_name as parameter
class StatusConsoleItemWithTwoButtons(QtWidgets.QFrame):
    def __init__(self, name:str, edit_func, delete_func,parent=None) -> None:
        super().__init__(parent)

        self.name = name

        self.name_lbl = QtWidgets.QLabel(name)
        self.name_lbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.name_lbl.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)
        self.name_lbl.setContentsMargins(7,0,0,0)
        bold_font = QtGui.QFont()
        bold_font.setBold(True)
        self.name_lbl.setFont(bold_font)
        



        self.edit_btn = QtWidgets.QPushButton()
        self.edit_btn.setIcon(QtGui.QIcon(os.path.join("data","img","edit.png")))
        self.edit_btn.setFixedSize(20, 25)
        #self.edit_btn.setStyleSheet("background-color: #ff5555")
        self.edit_btn.setSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Preferred)
        self.delete_btn = QtWidgets.QPushButton()
        self.delete_btn.setIcon(QtGui.QIcon(os.path.join("data","img","trash.png")))
        self.delete_btn.setFixedSize(20, 25)
        self.delete_btn.setStyleSheet("background-color: #ff5555")
        self.delete_btn.setSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Preferred)

        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(5,3,5,3)
        layout.addWidget(self.name_lbl)
        layout.addWidget(self.edit_btn)
        layout.addWidget(self.delete_btn)
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        
        self.setFrameShape(QtWidgets.QFrame.Shape.Box)
        self.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
        self.setLayout(layout)
        
        # Connect delete button
        #Remove the item from the StatusConsole and from the list of pdfs
        self.edit_btn.clicked.connect(lambda: edit_func(name))
        self.delete_btn.clicked.connect(lambda: delete_func(name))
        
#NOT finished
class InfiniteFieldsItem(QtWidgets.QFrame):
    def __init__(self,parent=None) -> None:
        super().__init__(parent)

        self.instruments:list[QtWidgets.QLineEdit] = []


        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(5,3,5,3)


        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        
        self.setFrameShape(QtWidgets.QFrame.Shape.Box)
        self.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
        self.setLayout(layout)

        #Add two first line edits
        for i in range(2):
            self.add_line()


    def add_line(self):
        l1 = QtWidgets.QLineEdit()
        l1.textChanged.connect(lambda: self.add_line() if self.instruments.index(l1) == len(self.instruments) - 1 else None)
        self.instruments.append(l1)
        self.layout().addWidget(l1)



#Scroll area where you can add QLabels 
class StatusConsole(QtWidgets.QScrollArea):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.items:list[QtWidgets.QFrame] = []

        status_console = QtWidgets.QWidget()
        self.status_console_layout = QtWidgets.QVBoxLayout()
        self.status_console_layout.setSpacing(5)
        self.status_console_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        #Create the labels that apear in the list
        status_console.setLayout(self.status_console_layout)


        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.setWidgetResizable(True)
        self.setWidget(status_console)

    def add_item(self,item:QtWidgets.QFrame) -> None:
        self.status_console_layout.addWidget(item)
        self.items.append(item)
    
    def remove_item(self,item:QtWidgets.QFrame) -> None:
        self.status_console_layout.removeWidget(item)
        item.deleteLater()
        self.items.remove(item)

    def clear(self):
        for i in self.items:
            self.status_console_layout.removeWidget(i)
            i.deleteLater()
        self.items.clear()



