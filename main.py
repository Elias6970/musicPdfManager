import sys,re,os
import gui.main_window as gui
import gui.score_clasifier_window as sc
from classes.files_manage import Dir
from classes.constants import RELATIVE_ARCHIVE_PATH
from tests.classifier_prove import *
#TODO: herramienta de importado de partituras que al importarlas se vayan mostrando para guardarlas por partes.




def main():
    """text="r1H"
    pattern1 = r'^[gofnrcjatlprdbuGOFNRCJATLPRDBU][1-9](?:[hH])?$'
    pattern2 = r'^[poner a mano las iniciales](?:[hH])?$'
    a = re.match(pattern1,text)
    if a:
        print("Siii")
    else:
        print("NO")
    print(a)"""

    """app = gui.QtWidgets.QApplication(sys.argv)
    w = gui.Main_window()
    w.show()
    sys.exit(app.exec_())"""

    #w = Pdf_controller(Dir(os.path.join(RELATIVE_ARCHIVE_PATH,"1610-A")))
    list = [Dir(os.path.join(RELATIVE_ARCHIVE_PATH,"1610-A")),Dir(os.path.join(RELATIVE_ARCHIVE_PATH,"1596-FERVOR"))]
    list2 = [Dir(os.path.join(RELATIVE_ARCHIVE_PATH,"1610-A"))]
    app = QtWidgets.QApplication(sys.argv)
    w = Classifier_window(list)
    w.show()
    sys.exit(app.exec_())
    
if __name__ == "__main__":
    main()