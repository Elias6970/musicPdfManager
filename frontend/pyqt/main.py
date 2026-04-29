import sys
from PyQt6.QtWidgets import QApplication
from frontend.pyqt.app.main_window.main_view import MainView
from frontend.pyqt.app.main_window.main_controller import MainController

def main():
    app = QApplication(sys.argv)
    view = MainView()
    controller = MainController(view)
    view.show()
    view.center_on_screen()
    
    view.show()

    sys.exit(app.exec())
    
if __name__ == "__main__":
    main()