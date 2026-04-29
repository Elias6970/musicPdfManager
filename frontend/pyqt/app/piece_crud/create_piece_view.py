from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QFormLayout, QLabel, QLineEdit,
    QCompleter, QCheckBox, QPushButton, QListWidget,
    QListWidgetItem, QHBoxLayout
)
from PyQt6.QtCore import pyqtSignal, Qt, QStringListModel

class CreatePieceView(QDialog):
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
        self.cod_input.setPlaceholderText(self.tr("Enter unique code"))
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText(self.tr("Enter piece name"))

        self.author_input = QLineEdit()
        self.author_input.setPlaceholderText(self.tr("Select or enter author"))
        self.author_completer = QCompleter([])
        self.author_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.author_input.setCompleter(self.author_completer)

        self.type_input = QLineEdit()
        self.type_input.setPlaceholderText(self.tr("Select or enter type"))
        self.type_completer = QCompleter([])
        self.type_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.type_input.setCompleter(self.type_completer)

        form_layout.addRow(self.tr("Code*:"), self.cod_input)
        form_layout.addRow(self.tr("Name*:"), self.name_input)
        form_layout.addRow(self.tr("Author:"), self.author_input)
        form_layout.addRow(self.tr("Type:"), self.type_input)

        main_layout.addLayout(form_layout)

        # Checkboxes
        self.is_handwritten_cb = QCheckBox(self.tr("Is Handwritten"))
        self.skip_classification_cb = QCheckBox(self.tr("Skip Classification (Do not classify now)"))
        self.skip_classification_cb.setChecked(True)
        self.skip_classification_cb.setDisabled(True) #TODO: Test it and use it
        main_layout.addWidget(self.is_handwritten_cb)
        main_layout.addWidget(self.skip_classification_cb)

        # File Selection Area
        self.select_files_btn = QPushButton(self.tr("Select Files"))
        self.select_files_btn.clicked.connect(self.select_files_clicked.emit)
        main_layout.addWidget(self.select_files_btn)

        # Small scroll area for files (QListWidget implements a scroll area natively)
        self.files_list = QListWidget()
        self.files_list.setMaximumHeight(120)
        main_layout.addWidget(self.files_list)

        # Submit button
        self.create_btn = QPushButton(self.tr("Create Piece"))
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
            # We store the path as the item's text, which is useful when retrieving data
            # It's hidden by the custom widget, but still natively accessible via item.text()
            item = QListWidgetItem(path)
            self.files_list.addItem(item)
            
            # Custom widget for the row
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(5, 2, 5, 2)
            
            # The removal button (cross) aligned to the left
            remove_btn = QPushButton("❌")
            remove_btn.setFixedSize(20, 20)
            remove_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            remove_btn.setStyleSheet("color: red; font-weight: bold; border: none; background: transparent;")
            remove_btn.clicked.connect(lambda checked, i=item: self._remove_file_item(i))
            
            # The actual text label of the file path
            # We configure elide mode so it cuts the left side of the text off with "..."
            text_label = QLabel(path)
            text_label.setToolTip(path) # Add tooltip to see the full path on hover
            
            # Instead of standard elide which is tricky on QLabel, we use robust Qt styling properties
            # Note: For flawless left-eliding on resize, it usually requires a custom paintEvent, 
            # but setting the text format properly alongside a fixed/minimizing policy is best here.
            # Alternatively, we can let Qt's font metrics generate an elided string of fixed length:
            font_metrics = text_label.fontMetrics()
            # 300 is a safe estimate for the label width in a 400px wide dialog, leaving room for the cross 
            elided_text = font_metrics.elidedText(path, Qt.TextElideMode.ElideLeft, 300)
            text_label.setText(elided_text)
            
            row_layout.addWidget(text_label)
            row_layout.addStretch()  # pushes everything to the left
            row_layout.addWidget(remove_btn)
            
            # Must set size hint so the QListWidget displays the widget properly
            item.setSizeHint(row_widget.sizeHint())
            self.files_list.setItemWidget(item, row_widget)

    def _remove_file_item(self, item: QListWidgetItem):
        """Removes the given item from the list."""
        row = self.files_list.row(item)
        if row >= 0:
            self.files_list.takeItem(row)

    def clear_files(self):
        """Clear the selected files list."""
        self.files_list.clear()
    
    def clear(self):
        """Utility method to clear all form inputs and selections."""
        self.cod_input.clear()
        self.name_input.clear()
        self.author_input.clear()
        self.type_input.clear()
        self.is_handwritten_cb.setChecked(False)
        self.skip_classification_cb.setChecked(True)
        self.clear_files()

    def get_form_data(self) -> dict:
        """Utility method for the controller to extract the current view state."""
        files = []
        for i in range(self.files_list.count()):
            item = self.files_list.item(i)
            if item is not None:
                files.append(item.text())
        
        return {
            "cod": self.cod_input.text(),
            "name": self.name_input.text(),
            "author": self.author_input.text(),
            "type": self.type_input.text(),
            "is_handwritten": self.is_handwritten_cb.isChecked(),
            "skip_classification": self.skip_classification_cb.isChecked(),
            "files": files
        }
