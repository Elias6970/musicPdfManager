from PyQt5 import QtWidgets
#Error class that throws error creating a pop up window with the error.
class Error:
    @staticmethod
    def print_error(e=None,message=""):
        error = QtWidgets.QMessageBox(QtWidgets.QMessageBox.NoIcon,"Error","Error: {},{} \n{}".format(type(e),e,message)) #traducir
        error.exec_()
    