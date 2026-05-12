from PyQt6 import QtWidgets
from app.error import OptionNotSelectedError, EmptyNameError

class CollisionItem(QtWidgets.QFrame):
    def __init__(self, missing_name: str, parent=None):
        super().__init__(parent)
        self.missing_name = missing_name
        
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        self.label = QtWidgets.QLabel(missing_name)
        layout.addWidget(self.label)
        layout.addStretch()
        self.overwrite_radio = QtWidgets.QRadioButton(self.tr("Overwrite"))
        self.rename_radio = QtWidgets.QRadioButton(self.tr("Rename to:"))
        self.rename_input = QtWidgets.QLineEdit()
        self.rename_input.setEnabled(False)
        
        # Action group to make radio buttons exclusive
        self.button_group = QtWidgets.QButtonGroup(self)
        self.button_group.addButton(self.overwrite_radio)
        self.button_group.addButton(self.rename_radio)
        
        layout.addWidget(self.overwrite_radio)
        layout.addWidget(self.rename_radio)
        layout.addWidget(self.rename_input)
        
        self.setFrameShape(QtWidgets.QFrame.Shape.Box)
        self.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
        self.rename_radio.toggled.connect(self.rename_input.setEnabled)
        
    def get_result(self) -> tuple[str, str | None]:
        if self.overwrite_radio.isChecked():
            return (self.missing_name, None)
        elif self.rename_radio.isChecked():
            new_name = self.rename_input.text().strip()
            if not new_name:
                raise EmptyNameError()
            return (self.missing_name, new_name)
        else:
            raise OptionNotSelectedError()