from PyQt6 import QtWidgets,QtCore
#Error class that throws error creating a pop up window with the error.
class Error_window:
    @staticmethod
    def print_error(e=None,message=""):
        if e != None:
            error = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Icon.NoIcon,"Error","Error: {},{} \n{}".format(type(e),e,message)) #traducir
        else:
            error = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Icon.NoIcon,"Error","Error: {}".format(message)) #traducir
        
        error.exec()



class ShowError:
    @staticmethod
    def show_tooltip_error(text:str,time_in_ms:int,widget:QtWidgets.QWidget):
        error = "<font color=#ff5050>"+text+"</font>"
        #Tell the user that the list is empty
        QtWidgets.QToolTip.showText(widget.mapToGlobal(widget.rect().center()),
                                    error,
                                    widget)
        QtCore.QTimer.singleShot(time_in_ms,QtWidgets.QToolTip.hideText)
        
