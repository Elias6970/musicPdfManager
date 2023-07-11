#import pytesseract 
import sys
import gui.main_window as gui
import classes.files_manage as a
from classes.constants import *
#import classes.db_manage as db
#import classes.score as sc
#pytesseract.pytesseract.tesseract_cmd = "/usr/local/bin/tesseract"
import os,rarfile



def main():

    #rr = a.Reorganize("archivo.db","../test/","../felicidad/")
    #ab = a.Archivo("archivo.db",RELATIVE_ARCHIVE_PATH)
    #print(ab.get_dir_names())
    app = gui.QtWidgets.QApplication(sys.argv)
    w = gui.MainWindow()
    w.show()
    sys.exit(app.exec_())







if __name__ == "__main__":
    main()