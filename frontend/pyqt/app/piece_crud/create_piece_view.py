from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLabel, QLineEdit,
    QCompleter, QCheckBox, QPushButton, QListWidget
)
from PyQt6.QtCore import pyqtSignal, Qt, QStringListModel

class CreatePieceView(QWidget):
    # Signals to be connected in the controller
    select_files_clicked = pyqtSignal()
    create_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Create New Piece")
        self.resize(400, 500)
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)

        # Form layout for the main input fields
        form_layout = QFormLayout()

        self.cod_input = QLineEdit()
        self.cod_input.setPlaceholderText("Enter unique code")
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter piece name")

        self.author_input = QLineEdit()
        self.author_input.setPlaceholderText("Select or enter author")
        self.author_completer = QCompleter([])
        self.author_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.author_input.setCompleter(self.author_completer)

        self.type_input = QLineEdit()
        self.type_input.setPlaceholderText("Select or enter type")
        self.type_completer = QCompleter([])
        self.type_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.type_input.setCompleter(self.type_completer)

        form_layout.addRow("Code:", self.cod_input)
        form_layout.addRow("Name:", self.name_input)
        form_layout.addRow("Author:", self.author_input)
        form_layout.addRow("Type:", self.type_input)

        main_layout.addLayout(form_layout)

        # Checkboxes
        self.is_handwritten_cb = QCheckBox("Is Handwritten")
        self.skip_classification_cb = QCheckBox("Skip Classification (Do not classify now)")
        
        main_layout.addWidget(self.is_handwritten_cb)
        main_layout.addWidget(self.skip_classification_cb)

        # File Selection Area
        self.select_files_btn = QPushButton("Select Files")
        self.select_files_btn.clicked.connect(self.select_files_clicked.emit)
        main_layout.addWidget(self.select_files_btn)

        # Small scroll area for files (QListWidget implements a scroll area natively)
        self.files_list = QListWidget()
        self.files_list.setMaximumHeight(120)
        main_layout.addWidget(self.files_list)

        # Submit button
        self.create_btn = QPushButton("Create Piece")
        self.create_btn.setStyleSheet("font-weight: bold; padding: 8px;")
        self.create_btn.clicked.connect(self.create_clicked.emit)
        main_layout.addWidget(self.create_btn)

    def set_author_options(self, options: list[str]):
        """Populate the author autocompleter from the controller."""
        self.author_completer.setModel(QStringListModel(options))

    def set_type_options(self, options: list[str]):
        """Populate the type autocompleter from the controller."""
        self.type_completer.setModel(QStringListModel(options))

    def add_files_to_list(self, file_paths: list[str]):
        """Add selected files to the list widget."""
        for path in file_paths:
            self.files_list.addItem(path)
            
    def clear_files(self):
        """Clear the selected files list."""
        self.files_list.clear()

    def get_form_data(self) -> dict:
        """Utility method for the controller to extract the current view state."""
        return {
            "cod": self.cod_input.text(),
            "name": self.name_input.text(),
            "author": self.author_input.text(),
            "type": self.type_input.text(),
            "is_handwritten": self.is_handwritten_cb.isChecked(),
            "skip_classification": self.skip_classification_cb.isChecked(),
            "files": [self.files_list.item(i).text() for i in range(self.files_list.count())]
        }
