import sys,re,os
import gui.main_window as gui
import gui.score_classifier_window as sc
from classes.files_manage import Dir
from classes.constants import RELATIVE_ARCHIVE_PATH

#TODO: herramienta de importado de partituras que al importarlas se vayan mostrando para guardarlas por partes.




def main():
    app = gui.QtWidgets.QApplication(sys.argv)
    w = gui.Main_window()
    w.show()
    sys.exit(app.exec_())
    
if __name__ == "__main__":
    main()