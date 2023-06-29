#import pytesseract 
import gui.gui_init as gui
import classes.db_manage as db
import classes.score as sc
#pytesseract.pytesseract.tesseract_cmd = "/usr/local/bin/tesseract"




def main():
    pa = sc.Score(cod=23,name="Sinfonías Marianas",parts=1,author="Jaime Emperador",create_date="11/03/2011")
    a = db.db("archivo.db")
    #a.insert_from_xls("classes/excel.xls")
    #a.insert_from_xlsx("classes/partituras.xlsx")
    #a.insert(pa)
    print(a.get_all())

    a.close_db()







if __name__ == "__main__":
    main()