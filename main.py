#import pytesseract 
import sys
import gui.gui_init as gui
#import classes.db_manage as db
#import classes.score as sc
#pytesseract.pytesseract.tesseract_cmd = "/usr/local/bin/tesseract"




def main():
    #pa = sc.Score(cod=23,name="Sinfonías Marianas",parts=1,author="Jaime Emperador",create_date="11/03/2011")
    app = gui.QtWidgets.QApplication(sys.argv)
    w = gui.MainWindow()
    w.show()
    sys.exit(app.exec_())







if __name__ == "__main__":
    main()