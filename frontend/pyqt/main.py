import sys
from PyQt6.QtWidgets import QApplication
from frontend.pyqt.app.selectors.multiple_selection_controller import MultipleSelectionController
from frontend.pyqt.app.selectors.multiple_selection_view import MultipleSelectionView
from frontend.pyqt.app.selectors.individual_selection_controller import IndividualSelectionController
from frontend.pyqt.app.selectors.individual_selection_view import IndividualSelectionView

def main():
    app = QApplication(sys.argv)
    
    #view = MultipleSelectionView()
    #controller = MultipleSelectionController(view)
    #view = IndividualSelectionView()
    #controller = IndividualSelectionController(view)

    
    #view.show()

    sys.exit(app.exec())
    
if __name__ == "__main__":
    main()