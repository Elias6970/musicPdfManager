from PyQt5.QtCore import Qt, QTranslator, QLocale, QCoreApplication
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QWidget, QVBoxLayout

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        container = QWidget()
        container_layout = QVBoxLayout()
        self.setWindowTitle(self.tr("Language Example"))

        self.label = QLabel(self.tr("Hello, World!"))
        self.label.setGeometry(50, 50, 200, 50)

        self.button = QPushButton(self.tr("Switch Language"))
        self.button.setGeometry(50, 120, 200, 50)
        self.button.clicked.connect(self.switch_language)
        container_layout.addWidget(self.label)
        container_layout.addWidget(self.button)
        container.setLayout(container_layout)
        self.setCentralWidget(container)


    def switch_language(self):
        current_locale = QLocale.system().name()
        print(current_locale)
        if current_locale == "en_US":
            new_locale = "esp_ES"
        else:
            new_locale = "en_US"

        translator = QTranslator()
        translator.load("app_" + new_locale)
        QCoreApplication.installTranslator(translator)
        self.retranslate_ui()

    def retranslate_ui(self):
        self.setWindowTitle(self.tr("Ejemplo"))
        self.label.setText(self.tr("Buenas!"))
        self.button.setText(self.tr("Cambia"))

if __name__ == "__main__":
    app = QApplication([])
    window = MyWindow()
    window.show()
    app.exec_()