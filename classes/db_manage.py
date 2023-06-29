import sqlite3,xlrd,openpyxl
from .score import Score

class db:
    def __init__(self,name):
        self.name = name
        self.path = "./classes/"+str(name)
        
        self.con = sqlite3.connect(self.path)
        self.cur = self.con.cursor()

        self.cur.execute("PRAGMA foreign_keys = 1") #Enable foreign keys

        self.cur.execute("CREATE TABLE IF NOT EXISTS archive(cod INTEGER PRIMARY KEY,name TEXT NOT NULL,author TEXT,type TEXT,create_date DATE,last_modification DATE)")

        self.con.commit()

 
    #Insert a score in the db
    def insert(self,score:Score):
        try: 
            #Check if cod>0 and have name
            if score.cod > 0 and score.name is not None and len(score.name.strip()) > 0:
                
                if score.create_date is None:
                    score.create_date = "DATE('now')"
                self.cur.execute("INSERT INTO archive VALUES (?,?,?,?,{},{})".format(score.create_date,"DATE('now')"),(score.cod,score.name,score.author,score.type))
                self.con.commit()
            else:
                print("Error en el código o nombre de la obra")
                raise #Jump to the except statement

        except sqlite3.IntegrityError: #cod repited
            print("Error, ya existe esa obra: ",score.cod)

        except Exception as e:
            print("Error ",type(e)," introduciendo la obra, ",score.name)
    

    #Insert into the db from excel xlsx 
    def insert_from_xlsx(self,file):
        i = 0
        print("JJJ")
        excel = openpyxl.load_workbook(file)
        sheet = excel.active
        for row in sheet.iter_rows(): # type: ignore    
            if i == 0: #Jump the firsts iteration
                i+=1
                continue 

            row_values = list(cell.value for cell in row)

            #Don't analize the empty rows 
            if row_values[0] == None:
                continue
            try:
                self.insert(Score(row_values[0],str(row_values[1]),row_values[2],row_values[3]))
            except:
                print("Error inserting: ",row_values)

            i+=1         


    #Insert into the db from excel xls   
    def insert_from_xls(self,file):
        excel = xlrd.open_workbook(file)
        sheet = excel.sheet_by_index(0)

        for i in range(1,sheet.nrows):
            row = sheet.row_values(i)
            try:
                self.insert(Score(row[0],str(row[1]),row[2],row[3]))
            except:
                print("Error inserting: ",row)
        
        self.cur.close()


    #Get rows from the db
        #type:
        #   cod->get row by the cod
        #   name->get rows with similar name
        #   author->get rows with similar author
        #   Can be used with dates but it doesn't work correctly
    def get(self,type,value): 
        try:
            self.cur.execute("PRAGMA case_sensitive_like = true")
            
            extracted = self.cur.execute("SELECT * FROM archive WHERE {} like '%{}%'".format(type,value))

        except Exception as e:
            print(e)
            return 0
        
        return extracted.fetchall()


    #Returns all the db
    def get_all(self):
        return self.cur.execute("SELECT * FROM archive").fetchall()
    
    #close the db
    def close_db(self):
        self.cur.close()

