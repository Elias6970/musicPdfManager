#import pytesseract 
import sys
from PyQt5 import QtWidgets
import gui.main_window as gui
import gui.other_windows as ot
import classes.files_manage as a
from classes.constants import *
#import classes.db_manage as db
#import classes.score as sc
#pytesseract.pytesseract.tesseract_cmd = "/usr/local/bin/tesseract"




def main():

    #rr = a.Reorganize("archivo.db","../test/","../felicidad/")
    #ab = a.Archivo("AMVR archive","archivo.db",RELATIVE_ARCHIVE_PATH)
    
    #m = list(filter(lambda i:os.path.basename(i.path),ab.pieces_in_dirs))

    #for i in ab.pieces_in_dirs:
        #print(os.path.basename(i.path))


    #print(ab.get_dir_names())
    app = gui.QtWidgets.QApplication(sys.argv)
    w = gui.MainWindow()
    w.show()
    sys.exit(app.exec_())







if __name__ == "__main__":
    main()