import typing
from PyQt5 import QtCore, QtWidgets
import PyQt5
from PyQt5.QtWidgets import QWidget



class add_scores_window(QtWidgets.QDialog):
    def __init__(self):
        super(add_scores_window,self).__init__()
        
        self.setWindowTitle("Add Score")
        self.btn = QtWidgets.QPushButton("AAA")
        self.btn.clicked.connect(self.a)

        container_layout = QtWidgets.QVBoxLayout()
        
        #Space
        container_layout.setSpacing(0)
        container_layout.setContentsMargins(20,0,20,20)

        container_layout.addWidget(self.btn)
        
        self.setLayout(container_layout)

        #self.setCentralWidget(container)
        self.setGeometry(100,80,200,200)
        self.exec_()

    def a(self):
        self.hide()
