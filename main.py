import sys
import gui.main_window as gui

def main():
    app = gui.QtWidgets.QApplication(sys.argv)
    w = gui.Main_window()
    w.show()
    sys.exit(app.exec_())
    
if __name__ == "__main__":
    main()