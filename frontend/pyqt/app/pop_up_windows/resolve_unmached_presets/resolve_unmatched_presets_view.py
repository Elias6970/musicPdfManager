from PyQt6 import QtWidgets,QtCore,QtGui
from app.elements.status_console import StatusConsole
from app.elements.list_items.status_console_item_with_two_texts_and_one_field import StatusConsoleItemWithTwoTextsAndOneField

class ResolveUnmatchedPresetsView(QtWidgets.QDialog):
    confirm_signal = QtCore.pyqtSignal()
    def __init__(self,parent=None) -> None:
        super(ResolveUnmatchedPresetsView,self).__init__(parent)

        self.setWindowTitle(self.tr("Solve not autosolved scores"))
        self.status_console = StatusConsole()
        self.items:list[StatusConsoleItemWithTwoTextsAndOneField] = []

        self.btn_confirm = QtWidgets.QPushButton(self.tr("Confirm"))
        self.btn_confirm.clicked.connect(self.confirm_signal.emit)

        _layout = QtWidgets.QVBoxLayout()
        _layout.addWidget(self.status_console)
        _layout.addWidget(self.btn_confirm)

        self.setLayout(_layout)

    def add_item(self, piece:str, preset_instrument:str, options:list[str]):
        item = StatusConsoleItemWithTwoTextsAndOneField(piece,
                                                       preset_instrument,
                                                       options)
        self.status_console.add_item(item)
        self.items.append(item)

    def clear_items(self):
        for i in self.items:
            self.status_console.remove_item(i)
        self.items = []


