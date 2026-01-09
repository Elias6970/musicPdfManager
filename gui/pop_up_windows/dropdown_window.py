from PyQt6 import QtWidgets, QtCore
from typing import Optional

class DropdownWindow(QtWidgets.QDialog):
    """
    Dialog window that shows a list of string options in a combo box and captures the user's selection.
    Args:
        options (list[str]): Sequence of option labels to populate the dropdown.
        preselected_option (Optional[str], optional): An option to select by default if present in the list.
        parent (Optional[QtWidgets.QWidget]): Parent widget for the dialog.
    Attributes:
        selected_option (Optional[str]): The option selected when the user confirms; `None` until confirmation.
    """

    def __init__(self, options: list[str], preselected_option: Optional[str]=None, parent=None) -> None:
        super().__init__(parent)
        self.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        self.setWindowTitle(self.tr("Select an option"))

        self.selected_option: Optional[str] = None

        container = QtWidgets.QVBoxLayout()
        container.setContentsMargins(20, 10, 20, 20)
        container.setSpacing(10)

        label = QtWidgets.QLabel(self.tr("Select the instrument preset to import the pieces."))
        container.addWidget(label)

        self.combo = QtWidgets.QComboBox()
        self.combo.addItems(options)
        if preselected_option:
            idx = self.combo.findText(preselected_option)
            if idx != -1:
                self.combo.setCurrentIndex(idx)
        container.addWidget(self.combo)

        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addStretch()
        ok_btn = QtWidgets.QPushButton(self.tr("Ok"))
        ok_btn.clicked.connect(self.confirm)
        btn_layout.addWidget(ok_btn)

        container.addLayout(btn_layout)
        self.setLayout(container)
        self.exec()

    def confirm(self):
        self.selected_option = self.combo.currentText()
        self.hide()