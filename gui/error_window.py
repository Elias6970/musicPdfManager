from PyQt5 import QtWidgets
#Error class that throws error creating a pop up window with the error.
class Error_window:
    @staticmethod
    def print_error(e=None,message=""):
        if e != None:
            error = QtWidgets.QMessageBox(QtWidgets.QMessageBox.NoIcon,"Error","Error: {},{} \n{}".format(type(e),e,message)) #traducir
        else:
            error = QtWidgets.QMessageBox(QtWidgets.QMessageBox.NoIcon,"Error","Error: {}".format(message)) #traducir
        
        error.exec_()
        
