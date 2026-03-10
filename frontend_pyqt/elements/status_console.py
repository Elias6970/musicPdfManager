from PyQt6 import QtWidgets,QtCore

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

        if self.verticalScrollBar().value() == self.verticalScrollBar().maximum():
            item.show()
            QtCore.QTimer.singleShot(0, lambda: self.verticalScrollBar().setValue(self.verticalScrollBar().maximum()))
    
    def remove_item(self,item:QtWidgets.QFrame) -> None:
        self.status_console_layout.removeWidget(item)
        item.deleteLater()
        self.items.remove(item)

    def clear(self):
        for i in self.items:
            self.status_console_layout.removeWidget(i)
            i.deleteLater()
        self.items.clear()