from PyQt6 import QtWidgets,QtCore
from classes.files_manage import Archive

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
#   handwritten checkbox 
#   TODO: add posibility to not add scores
#   
class AbstractFieldsWindow(QtWidgets.QDialog):
    def __init__(self,archive:Archive,window_title:str,btn_lbl:str,checkboxes_names:list[str],btn_function,close_function=None,parent=None):
        super(AbstractFieldsWindow,self).__init__(parent=parent)
        
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