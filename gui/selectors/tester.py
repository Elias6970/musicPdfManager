import PyQt6
import PyQt6.QtWidgets
from gui.selectors.individual_selection_window import IndividualSelectionWindow
from gui.selectors.multiple_selection_window import MultipleSelectionWindow
from classes.files_management.archive import Archive
from classes.constants import RELATIVE_ARCHIVE_PATH,DB_NAME

class TestDialog(PyQt6.QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        archive = Archive(DB_NAME,RELATIVE_ARCHIVE_PATH())
        #m = IndividualSelectionWindow(archive)
        m = MultipleSelectionWindow(archive)
        h = PyQt6.QtWidgets.QVBoxLayout()
        h.addWidget(m)
        self.setLayout(h)

        self.exec()
        quit()