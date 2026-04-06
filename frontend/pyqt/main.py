import sys
from PyQt6.QtWidgets import QApplication
from frontend.pyqt.app.selectors.individual_selection_view import IndividualSelectionView
from frontend.pyqt.app.selectors.individual_selection_controller import IndividualSelectionController

def main():
    app = QApplication(sys.argv)
    
    view = IndividualSelectionView()
    controller = IndividualSelectionController(view)
    
    # Simulate some initial data for testing
    controller.refresh()
    
    view.show()

    sys.exit(app.exec())
    
if __name__ == "__main__":
    main()