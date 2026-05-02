from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton
from PyQt6.QtCore import pyqtSignal


class PreferencesView(QDialog):
    """Dialog for managing application preferences."""
    save = pyqtSignal()  # Signal emitted when the user clicks "OK" to save preferences
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Preferences"))
        self.setModal(True)
        self.setFixedSize(400, 150)
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Language selection section
        language_layout = QHBoxLayout()
        language_label = QLabel(self.tr("Language:"))
        self.language_combobox = QComboBox()
        
        # Fill the combobox with available languages
        self.fill_language_combobox()
        
        language_layout.addWidget(language_label)
        language_layout.addWidget(self.language_combobox)
        layout.addLayout(language_layout)
        
        # Buttons layout
        buttons_layout = QHBoxLayout()
        self.ok_button = QPushButton(self.tr("OK"))
        self.cancel_button = QPushButton(self.tr("Cancel"))
        
        self.ok_button.clicked.connect(self.save.emit)
        self.cancel_button.clicked.connect(self.reject)
        
        buttons_layout.addWidget(self.ok_button)
        buttons_layout.addWidget(self.cancel_button)
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
    
    def fill_language_combobox(self, languages: dict[str, str] = {}):
        """Fill the language combobox with available languages."""
        for lang_code, lang_name in languages.items():
            self.language_combobox.addItem(lang_name, lang_code)
    
    def get_selected_language(self) -> str:
        """Get the currently selected language code.
        
        Returns:
            str: The language code (e.g., 'en', 'es', 'fr')
        """
        return self.language_combobox.currentData()
    
    def set_selected_language(self, lang_code: str):
        """Set the selected language by language code.
        
        Args:
            lang_code (str): The language code to select (e.g., 'en', 'es', 'fr')
        """
        index = self.language_combobox.findData(lang_code)
        if index != -1:
            self.language_combobox.setCurrentIndex(index)
