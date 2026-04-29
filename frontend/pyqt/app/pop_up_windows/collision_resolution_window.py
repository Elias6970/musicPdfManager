from PyQt6 import QtWidgets, QtCore
from frontend.pyqt.app.elements.status_console import StatusConsole
from frontend.pyqt.app.pop_up_windows.error.error_window import ShowError
from frontend.pyqt.app.error import OptionNotSelectedError, EmptyNameError
from frontend.pyqt.app.elements.list_items.collition_item import CollisionItem

class CollisionResolutionWindow(QtWidgets.QDialog):
    resolved_signal = QtCore.pyqtSignal(dict) # dict[str, str | None]
    
    def __init__(self, missing_names: list[str], parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("File Collision Resolution"))
        self.setMinimumSize(500, 400)
        
        layout = QtWidgets.QVBoxLayout(self)
        
        info_label = QtWidgets.QLabel(self.tr("The following files already exist in the destination. Please choose to overwrite them or rename the new file."))
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        self.status_console = StatusConsole()
        layout.addWidget(self.status_console)
        
        self.items: list[CollisionItem] = []
        for name in missing_names:
            item = CollisionItem(name)
            self.status_console.add_item(item)
            self.items.append(item)
            
        self.confirm_button = QtWidgets.QPushButton(self.tr("Confirm"))
        self.confirm_button.clicked.connect(self._on_confirm)
        layout.addWidget(self.confirm_button)
        
    def _on_confirm(self):
        result_dict = {}
        for item in self.items:
            try:
                original, new_name = item.get_result()
                result_dict[original] = new_name
            except OptionNotSelectedError:
                ShowError.show_tooltip_error(self.tr("Please select an option."), 3000, item)
                return
            except EmptyNameError:
                ShowError.show_tooltip_error(self.tr("Please enter a new name."), 3000, item.rename_input)
                return
                
        self.resolved_signal.emit(result_dict)
        self.accept()
