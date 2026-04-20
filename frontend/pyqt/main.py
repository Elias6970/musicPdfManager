import sys
from PyQt6.QtWidgets import QApplication
from frontend.pyqt.app.selectors.multiple_selection_controller import MultipleSelectionController
from frontend.pyqt.app.selectors.multiple_selection_view import MultipleSelectionView
from frontend.pyqt.app.selectors.individual_selection_controller import IndividualSelectionController
from frontend.pyqt.app.selectors.individual_selection_view import IndividualSelectionView
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