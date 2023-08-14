import typing
from PyQt5 import QtCore, QtWidgets
import PyQt5




class Add_scores_window(QtWidgets.QDialog):
    def __init__(self,next_cod,parent=None):
        super(Add_scores_window,self).__init__(parent=parent)
        
        self.setWindowModality(QtCore.Qt.WindowModal) #type: ignore

        container_layout = QtWidgets.QVBoxLayout()
        
        #Space
        container_layout.setSpacing(0)
        container_layout.setContentsMargins(20,0,20,20)

        container_layout.addLayout(self.create_fields_layout(next_cod))
        container_layout.addLayout(self.create_buttons_layout())
        
        self.setGeometry(0,0,400,200)
        self.setLayout(container_layout)

        self.exec_()

    #Create the fields layout that is returned and added as a layout(not as a widget)
    def create_fields_layout(self,next_cod):
        fields_layout = QtWidgets.QVBoxLayout()

        
        self.line_cod = QtWidgets.QLineEdit()
        self.line_cod.setPlaceholderText(f"next in the archive will be: {next_cod}")
        self.line_name = QtWidgets.QLineEdit()
        self.line_author = QtWidgets.QLineEdit()
        self.line_type = QtWidgets.QLineEdit()


        cod_layout = QtWidgets.QHBoxLayout()
        cod_layout.addWidget(QtWidgets.QLabel("Cod  "))
        cod_layout.addWidget(self.line_cod)

        name_layout = QtWidgets.QHBoxLayout()
        name_layout.addWidget(QtWidgets.QLabel("Name *  "))
        name_layout.addWidget(self.line_name)

        author_layout = QtWidgets.QHBoxLayout()
        author_layout.addWidget(QtWidgets.QLabel("Author  "))
        author_layout.addWidget(self.line_author)
        
        type_layout = QtWidgets.QHBoxLayout()
        type_layout.addWidget(QtWidgets.QLabel("Type  "))
        type_layout.addWidget(self.line_type)

        fields_layout.addLayout(cod_layout)
        fields_layout.addLayout(name_layout)
        fields_layout.addLayout(author_layout)
        fields_layout.addLayout(type_layout)

        return fields_layout
    
    #Create the buttons layout
    def create_buttons_layout(self):
        btns_layout = QtWidgets.QHBoxLayout()
        close_btn = QtWidgets.QPushButton("Close")
        add_btn = QtWidgets.QPushButton("Add")

        close_btn.clicked.connect(self.close)
        add_btn.clicked.connect(self.add_score)

        btns_layout.addWidget(close_btn)
        btns_layout.addWidget(add_btn)

        return btns_layout
    
    def add_score(self):
        print(self.line_cod.text(),self.line_name.text())

    def close(self):
        self.hide()
