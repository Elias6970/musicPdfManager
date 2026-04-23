import sys
from PyQt6.QtWidgets import (QApplication, QDialog, QVBoxLayout, QTableWidget, 
                             QTableWidgetItem, QComboBox, QPushButton, QHeaderView)
from PyQt6.QtCore import pyqtSignal, Qt

class UsersView(QDialog):
    save_signal = pyqtSignal(list)
    create_blank_user = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Manage Users and Roles")
        self.resize(600, 300)

        # Define the allowed roles for the dropdown
        self.available_roles:dict[int,str] = {}

        # Main layout for the dialog
        layout = QVBoxLayout(self)
        # 0. Create add button
        self.add_btn = QPushButton("+")
        self.add_btn.clicked.connect(self.create_blank_user.emit)
        self.add_btn.setFixedWidth(30)
        self.add_btn.setStyleSheet("background-color: green")
        self.add_btn.setToolTip("Add a new empty user")
        layout.addWidget(self.add_btn)

        # 1. Setup the Table
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Email", "Name", "Role"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)

        # 2. Setup a button to test extracting the data
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.get_data)
        layout.addWidget(self.save_btn)


    def add_user_row(self, user_id:int, email:str, name:str, role_id:int):
        """Helper method to add a row with text items and a combobox."""
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)

        # Standard Text Cells for Email and Name
        email = QTableWidgetItem(email)
        email.setData(Qt.ItemDataRole.UserRole, user_id)  # Store user_id in the item for later retrieval
        self.table.setItem(row_position, 0, email)
        self.table.setItem(row_position, 1, QTableWidgetItem(name))

        # ComboBox for the Role
        combo = QComboBox()
        for role_value, role_name in self.available_roles.items():
            combo.addItem(role_name, role_value)  # Display role name, store role id as data

        # Set the current dropdown text to match the user's role
        if role_id in self.available_roles:
            combo.setCurrentText(self.available_roles[role_id])
        else:
            combo.setCurrentIndex(-1)  # No selection if role_id is not valid
            
        # Inject the widget into the table cell
        self.table.setCellWidget(row_position, 2, combo)


    def get_data(self) -> list[tuple[str, str, str, str]]:
        """
        Extract data from both standard items and cell widgets.
        :return: A list of tuples containing (user_id, email, name, role)
        """
        elements = []
        for row in range(self.table.rowCount()):
            email = self.table.item(row, 0).text()
            name = self.table.item(row, 1).text()
            
            # To get data from a custom widget, we have to extract the widget first
            role_widget = self.table.cellWidget(row, 2)
            if role_widget and isinstance(role_widget, QComboBox):
                role = role_widget.currentText() # Extract text from the QComboBox
                user_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)  # Retrieve the stored user_id

                elements.append((user_id, email, name, role))

        return elements 

