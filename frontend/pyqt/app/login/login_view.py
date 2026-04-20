from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt6.QtCore import pyqtSignal

class LoginView(QDialog):
    login_requested = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Login")
        self.setModal(True)
        self.setFixedSize(300, 150)

        layout = QVBoxLayout()

        # Email field
        email_layout = QHBoxLayout()
        email_label = QLabel("Email:")
        self.email_input = QLineEdit()
        email_layout.addWidget(email_label)
        email_layout.addWidget(self.email_input)
        layout.addLayout(email_layout)

        # Password field
        password_layout = QHBoxLayout()
        password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        layout.addLayout(password_layout)

        # Login button
        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.on_login_clicked)
        layout.addWidget(self.login_button)

        self.setLayout(layout)

    def on_login_clicked(self):
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()
        if not email or not password:
            QMessageBox.warning(self, "Error", "Email and Password cannot be empty")
            return
        self.login_requested.emit(email, password)

    def show_error(self, message: str):
        QMessageBox.warning(self, "Login Error", message)
