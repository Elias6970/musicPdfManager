import sys
import frontend_pyqt.main_window as frontend_pyqt

def main():
    app = frontend_pyqt.QtWidgets.QApplication(sys.argv)
    w = frontend_pyqt.Main_window()
    w.show()
    w.center_on_screen()
    sys.exit(app.exec())
    
if __name__ == "__main__":
    main()