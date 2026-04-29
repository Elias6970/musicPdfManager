import sys
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import (QApplication, QCheckBox, QDialog, QVBoxLayout, QTableWidget, 
                             QTableWidgetItem, QComboBox, QPushButton, QHeaderView)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QIcon
from frontend.pyqt.app.config.constants import TRASH_IMG_PATH
from frontend.pyqt.app.pop_up_windows.error.error_window import ShowError

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
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Email", "Name", "Role", "Password", ""])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)

        # 2. Setup a button to test extracting the data
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.get_data)
        layout.addWidget(self.save_btn)


    def add_user_row(self, user_id:int, email:str, name:str, role_id:int | None):
        """Helper method to add a row with text items and a combobox."""
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)

        # Standard Text Cells for Email and Name
        email_item = QTableWidgetItem(email)
        email_item.setData(Qt.ItemDataRole.UserRole, user_id)  # Store user_id in the item for later retrieval
        self.table.setItem(row_position, 0, email_item)
        self.table.setItem(row_position, 1, QTableWidgetItem(name))

        # ComboBox for the Role
        combo = QComboBox()
        for _role_id, _role_name in self.available_roles.items():
            combo.addItem(_role_name, _role_id)  # Display role name, store role id as data

        # Set the current dropdown text to match the user's role
        if role_id in self.available_roles:
            combo.setCurrentText(self.available_roles[role_id])
        else:
            combo.setCurrentIndex(-1)  # No selection if role_id is not valid
            
        # Inject the widget into the table cell
        self.table.setCellWidget(row_position, 2, combo)

        self.table.setItem(row_position, 3, QTableWidgetItem(""))  # Empty password field for user input

        delete_btn = QPushButton()
        delete_btn.setIcon(QIcon(TRASH_IMG_PATH))
        delete_btn.setFixedSize(20, 25)
        delete_btn.setStyleSheet("background-color: #ff5555")
        delete_btn.setSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Preferred)
        # Compute the row index dynamically when the button is clicked 
        delete_btn.clicked.connect(lambda _, btn=delete_btn: self.table.removeRow(self.table.indexAt(btn.pos()).row()))
        self.table.setCellWidget(row_position, 4, delete_btn)


    def get_data(self) -> list[tuple[int, str, str, int, str, int]]:
        """
        Extract data from both standard items and cell widgets.
            :return: A list of tuples containing (user_id, email, name, role_id, password, row) for each row.
        """
        elements = []
        for row in range(self.table.rowCount()):
            email = self.table.item(row, 0).text()
            name = self.table.item(row, 1).text()
            password = self.table.item(row, 3).text()
            # To get data from a custom widget, we have to extract the widget first
            role_widget = self.table.cellWidget(row, 2)
            if role_widget and isinstance(role_widget, QComboBox):
                role_id = role_widget.currentData()  # Extract the stored role_id or None
                user_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)  # Retrieve the stored user_id
                
                if user_id == -1 and email == "" and name == "" and password == "" and role_id == None:
                    continue #This is a blank user, skip it

                elements.append((user_id, email, name, role_id, password, row))

        return elements 

    def show_tooltip_error_in_a_row(self, row:int, message:str):
        """Show a tooltip in a specific row. This can be used to show validation errors."""
        # Since ShowError.show_tooltip_error requires a QWidget and QTableWidgetItem is NOT a widget,
        # we can attach the tooltip to the QComboBox widget that lives in cell column 2 of this row.
        role_combo_widget = self.table.cellWidget(row, 2)
        
        if role_combo_widget:
            ShowError.show_tooltip_error(message, 5000, role_combo_widget)
        else:
            # Fallback: display it in the center of the table if the widget is missing
            ShowError.show_tooltip_error(message, 5000, self.table)