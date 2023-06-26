from PyQt5 import QtWidgets
import sys


def init():
    app = QtWidgets.QApplication(sys.argv)

    window = QtWidgets.QMainWindow()
    window.setWindowTitle("Archivo AMVR")
    window.resize(300, 200)


    button = QtWidgets.QPushButton("Click me", window)
    button.setGeometry(50, 50, 200, 50)

    
    window.show()

    

    sys.exit(app.exec_())
