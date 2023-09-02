#import pytesseract 
import sys
from PyQt5 import QtWidgets
import gui.main_window as gui
import gui.add_score_window as ot
import classes.files_manage as a
from classes.constants import *
#import classes.db_manage as db
#import classes.score as sc
#pytesseract.pytesseract.tesseract_cmd = "/usr/local/bin/tesseract"

from autodetect.pdf_file import Pdf
from classes.files_manage import Archivo

def main():
    #ab = Pdf("tests/el_moro.pdf")
    #ab.rotate(90)
    """ar = []
    for i in range(29):
        ar.append(ab.extract_header_text(i))"""
    #print(ar)
    #rr = a.Reorganize("archivo.db","../test/","../felicidad/")
    #ab = a.Archivo("AMVR_archive","archivo.db",RELATIVE_ARCHIVE_PATH)
    #ab.add_digitalized_mark()
    

    #m = list(filter(lambda i:os.path.basename(i.path),ab.pieces_in_dirs))

    #for i in ab.pieces_in_dirs:
        #print(os.path.basename(i.path))


    #archive = Archivo(DB_NAME,DB_FILE_NAME,RELATIVE_ARCHIVE_PATH)
    #archive.export_pdf_to_print("out.pdf")
    #print(ab.get_dir_names())

    app = gui.QtWidgets.QApplication(sys.argv)
    w = gui.MainWindow()
    w.show()
    sys.exit(app.exec_())







if __name__ == "__main__":
    main()