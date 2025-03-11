from PyQt6 import QtWidgets,QtCore

"""
Pop up a window that shows a message with buttons
    If only_yes_btn:bool = 0 there are yes or no
    if only_yes_btn:bool = 1 there are only yes
"""
class PopUpWindow(QtWidgets.QDialog):
    def __init__(self,text:str,only_yes_btn:bool,parent) -> None:
        super(PopUpWindow,self).__init__(parent)

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
