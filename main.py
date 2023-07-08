#import pytesseract 
import sys
import gui.main_window as gui
import classes.files_manage as a
from classes.constants import *
#import classes.db_manage as db
#import classes.score as sc
#pytesseract.pytesseract.tesseract_cmd = "/usr/local/bin/tesseract"




def main():
    #pa = sc.Score(cod=23,name="Sinfonías Marianas",parts=1,author="Jaime Emperador",create_date="11/03/2011")
    #m = a.Dir("../ArchivoDigital/120-HIMNO REGIONAL VALENCIANO 120")
    #m.export_all_names(RELATIVE_ARCHIVE_PATH)

    
    m = a.Archivo("archivo.db",RELATIVE_NEW_PATH)
    
    #r = a.Reorganize("archivo.db","../ArchivoDigitalSinTocar/")          
    #r = a.Reorganize("archivo.db","../test/")
    #print(m.get_dir_names())

    """app = gui.QtWidgets.QApplication(sys.argv)
    w = gui.MainWindow()
    w.show()
    sys.exit(app.exec_())"""







if __name__ == "__main__":
    main()