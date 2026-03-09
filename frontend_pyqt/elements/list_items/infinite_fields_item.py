from PyQt6 import QtWidgets,QtCore

class InfiniteFieldsItem(QtWidgets.QFrame):
    def __init__(self,every_change_func,parent=None) -> None:
        super().__init__(parent)
        self.default_lineEdits = 2
        self.max_copies = 20
        self.instruments:list[QtWidgets.QLineEdit] = []
        self.number_of_option = 1
        self.every_change_func = every_change_func #Function that is called when the text of the line edit changes

        self.num_copies = QtWidgets.QComboBox()
        self.num_copies.setFixedWidth(48)
        self.num_copies.addItems([str(i+1) for i in range(self.max_copies)])
        #self.num_copies.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)

        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(5,3,5,3)
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.num_copies)

        
        
        self.setFrameShape(QtWidgets.QFrame.Shape.Box)
        self.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
        self.setLayout(layout)

        #Add two first line edits
        for i in range(self.default_lineEdits):
            self.add_lineEdit()

    #Add a line edit to the layout
    #The line edit add a new lineEdit if you write in the last one
    def add_lineEdit(self):
        l1 = QtWidgets.QLineEdit()
        l1.textChanged.connect(lambda: (self.add_lineEdit() if self.instruments.index(l1) == len(self.instruments) - 1 else None) or self.every_change_func(self))

        if self.number_of_option == 1:
            l1.setPlaceholderText(self.tr("Instrument"))
        else:
            l1.setPlaceholderText(self.tr("Option")+" "+str(self.number_of_option))
            self.layout().addWidget(QtWidgets.QLabel("->"))
        
        self.instruments.append(l1)
        self.layout().addWidget(l1)

        self.number_of_option += 1

