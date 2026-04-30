from PyQt6.QtWidgets import (
    QDialog, QSizePolicy, QSpacerItem, QWidget, QVBoxLayout, QFormLayout, QLabel, QLineEdit,
    QCompleter, QCheckBox, QPushButton, QListWidget,
    QListWidgetItem, QHBoxLayout, QGroupBox, QFrame
)
from PyQt6.QtCore import pyqtSignal, Qt, QStringListModel

from frontend.pyqt.app.elements.score_search_bar import ScoreSearchBar


class UpdatePieceView(QDialog):
    # Signals to be connected in the controller
    piece_searched = pyqtSignal(str)
    select_files_clicked = pyqtSignal()
    update_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Update Piece")
        self.resize(450, 650)
        self.removed_files: list[str] = []
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)

        # Top Search Bar for selecting the piece
        search_layout = QHBoxLayout()
        self.search_bar = ScoreSearchBar()
        self.search_bar.setPlaceholderText(self.tr("Search piece to update..."))
        
        # We can trigger search either by pressing Enter or clicking a explicit button
        self.search_bar.returnPressed.connect(lambda: self.piece_searched.emit(self.search_bar.text()))
        
        search_btn = QPushButton(self.tr("Load Piece"))
        search_btn.clicked.connect(lambda: self.piece_searched.emit(self.search_bar.text()))
        
        search_layout.addWidget(self.search_bar)
        search_layout.addWidget(search_btn)
        main_layout.addLayout(search_layout)

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

        # Existing Files Area
        existing_group = QGroupBox(self.tr("Existing Scores"))
        existing_layout = QVBoxLayout()
        existing_lbl = QLabel(self.tr("Click ❌ to mark for removal, freeing the file from this piece."))
        existing_lbl.setStyleSheet("color: gray; font-style: italic; font-size: 11px;")
        existing_layout.addWidget(existing_lbl)
        self.existing_files_list = QListWidget()
        self.existing_files_list.setMaximumHeight(100)
        existing_layout.addWidget(self.existing_files_list)
        existing_group.setLayout(existing_layout)
        main_layout.addWidget(existing_group)

        # Add New Files Area
        new_files_group = QGroupBox(self.tr("Add New Scores"))
        new_files_layout = QVBoxLayout()
        self.select_files_btn = QPushButton(self.tr("Browse Local Files to Upload..."))
        self.select_files_btn.clicked.connect(self.select_files_clicked.emit)
        new_files_layout.addWidget(self.select_files_btn)
        self.new_files_list = QListWidget()
        self.new_files_list.setMaximumHeight(100)
        new_files_layout.addWidget(self.new_files_list)
        new_files_group.setLayout(new_files_layout)
        main_layout.addWidget(new_files_group)
        
        main_layout.addSpacing(10)
        
        # Bottom Separator
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(line)

        # Submit button
        self.update_btn = QPushButton(self.tr("Confirm Update Piece"))
        self.update_btn.setStyleSheet("""
            QPushButton {
                font-weight: bold; 
                padding: 12px; 
                font-size: 14px; 
                background-color: #2F80ED; 
                color: white; 
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #1A6BDA;
            }
            QPushButton:pressed {
                background-color: #1153AD;
            }
        """)
        self.update_btn.clicked.connect(self.update_clicked.emit)
        main_layout.addWidget(self.update_btn)

    def set_pieces_options(self, piece_names: list[str]):
        """Populate the pieces top search bar autocompleter."""
        self.search_bar.update_autocompleter_scores(piece_names)

    def set_author_options(self, options: list[str]):
        """Populate the author autocompleter from the controller."""
        self.author_completer.setModel(QStringListModel(options))

    def set_type_options(self, options: list[str]):
        """Populate the type autocompleter from the controller."""
        self.type_completer.setModel(QStringListModel(options))
        
    def populate_form(self, data: dict):
        """Called by controller to safely set all inputs when piece is loaded."""
        self.cod_input.setText(str(data.get("cod", "")))
        self.name_input.setText(data.get("name", ""))
        self.author_input.setText(data.get("author", ""))
        self.type_input.setText(data.get("type", ""))
        self.is_handwritten_cb.setChecked(data.get("is_handwritten", False))
        
        # Reset existing files states
        self.existing_files_list.clear()
        self.removed_files.clear()
        
        # Populate existing files
        for filename in data.get("existing_files", []):
            self._add_to_existing_files(filename)

    def _add_to_existing_files(self, filename: str):
        """Adds a file to the existing_files_list with a cross button to mark it for removal."""
        item = QListWidgetItem(filename)
        self.existing_files_list.addItem(item)
        
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(5, 2, 5, 2)
        
        remove_btn = QPushButton("❌")
        remove_btn.setFixedSize(20, 20)
        remove_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        remove_btn.setStyleSheet("color: red; font-weight: bold; border: none; background: transparent;")
        remove_btn.clicked.connect(lambda checked, i=item: self._mark_existing_file_for_removal(i))
        
        text_label = QLabel(filename)
        text_label.setToolTip(filename)
        font_metrics = text_label.fontMetrics()
        elided_text = font_metrics.elidedText(filename, Qt.TextElideMode.ElideLeft, 300)
        text_label.setText(elided_text)
        
        row_layout.addWidget(text_label)
        row_layout.addStretch()
        row_layout.addWidget(remove_btn)
        
        item.setSizeHint(row_widget.sizeHint())
        self.existing_files_list.setItemWidget(item, row_widget)
        
    def _mark_existing_file_for_removal(self, item: QListWidgetItem):
        """Moves an existing file to the internal removed_files list and removes it from UI."""
        self.removed_files.append(item.text())
        row = self.existing_files_list.row(item)
        if row >= 0:
            self.existing_files_list.takeItem(row)

    def add_new_files_to_list(self, file_paths: list[str]):
        """Add newly selected files to the bottom list widget to be uploaded."""
        for path in file_paths:
            item = QListWidgetItem(path)
            self.new_files_list.addItem(item)
            
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(5, 2, 5, 2)
            
            remove_btn = QPushButton("❌")
            remove_btn.setFixedSize(20, 20)
            remove_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            remove_btn.setStyleSheet("color: red; font-weight: bold; border: none; background: transparent;")
            remove_btn.clicked.connect(lambda checked, i=item: self._remove_new_file_item(i))
            
            text_label = QLabel(path)
            text_label.setToolTip(path)
            font_metrics = text_label.fontMetrics()
            elided_text = font_metrics.elidedText(path, Qt.TextElideMode.ElideLeft, 300)
            text_label.setText(elided_text)
            
            row_layout.addWidget(text_label)
            row_layout.addStretch()
            row_layout.addWidget(remove_btn)
            
            item.setSizeHint(row_widget.sizeHint())
            self.new_files_list.setItemWidget(item, row_widget)

    def _remove_new_file_item(self, item: QListWidgetItem):
        """Allows deciding against uploading a newly picked file before submission."""
        row = self.new_files_list.row(item)
        if row >= 0:
            self.new_files_list.takeItem(row)

    def clear(self):
        """Utility method to clear all form inputs and selections."""
        self.search_bar.clear()
        self.cod_input.clear()
        self.name_input.clear()
        self.author_input.clear()
        self.type_input.clear()
        self.is_handwritten_cb.setChecked(False)
        self.existing_files_list.clear()
        self.new_files_list.clear()
        self.removed_files.clear()

    def get_form_data(self) -> dict:
        """Utility method for the controller to extract the current view state upon update click."""
        new_files = []
        for i in range(self.new_files_list.count()):
            item = self.new_files_list.item(i)
            if item is not None:
                new_files.append(item.text())
                
        # Existing files left untouched
        existing_files = []
        for i in range(self.existing_files_list.count()):
            item = self.existing_files_list.item(i)
            if item is not None:
                existing_files.append(item.text())
        
        return {
            "search_query": self.search_bar.text(),
            "cod": self.cod_input.text(),
            "name": self.name_input.text(),
            "author": self.author_input.text(),
            "type": self.type_input.text(),
            "is_handwritten": self.is_handwritten_cb.isChecked(),
            "skip_classification": self.skip_classification_cb.isChecked(),
            "untouched_existing_files": existing_files,
            "removed_files": self.removed_files,
            "new_files": new_files
        }
