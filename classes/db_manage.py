import sqlite3,xlrd,openpyxl
from .score import Score

class Db:
    def __init__(self,db_name,file_name):
        self.db_name = db_name
        self.db_path = "./data/"+str(file_name)
        
        self.open_db()

        self.cur.execute("PRAGMA foreign_keys = 1") #Enable foreign keys

        self.cur.execute("CREATE TABLE IF NOT EXISTS {} (cod INTEGER PRIMARY KEY,name TEXT NOT NULL,author TEXT,type TEXT,created_date DATE,last_modification DATE,digitalized INTEGER DEFAULT 0,handwritten INTEGER DEFAULT 0,parted INTEGER DEFAULT 0)".format(db_name))

        self.con.commit()

 
    #Insert a score in the db
    def insert(self,score:Score):
        try: 
            #Check if cod>0 and have name
            if score.cod > 0 and score.name is not None and len(score.name.strip()) > 0:
                
                if score.create_date is None:
                    score.create_date = "DATE('now')"
                self.cur.execute("INSERT INTO {} VALUES (?,?,?,?,{},{})".format(self.db_name,score.create_date,"DATE('now')"),(score.cod,score.name,score.author,score.type))
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
        #camp_to_compare:
        #   cod->get row by the cod
        #   name->get rows with similar name
        #   author->get rows with similar author
        #   Can be used with dates but it doesn't work correctly
        #
        #selected camp get the camp that you want to be selected from the db. Can be more than one ej:("cod,name")
     
    #Make the get but comparing with LIKE % %
    def get_with_like(self,camp_to_compare,value,returned_camps='*'): 
        try:
            self.cur.execute("PRAGMA case_sensitive_like = true")
            
            extracted = self.cur.execute("SELECT {} FROM {} WHERE {} LIKE '%{}%'".format(returned_camps,self.db_name,camp_to_compare,value))

        except Exception as e:
            print(e)
            return ["0"]
        
        return extracted.fetchall()


    #Make the get but comparing with '=' not with LIKE % %
    def get_with_equals(self,camp_to_compare,value,returned_camps='*'):
        try:
            self.cur.execute("PRAGMA case_sensitive_like = true")
            
            extracted = self.cur.execute("SELECT {} FROM {} WHERE {} = '{}'".format(returned_camps,self.db_name,camp_to_compare,value))

        except Exception as e:
            print(e)
            return ["0"]
        
        return extracted.fetchall()

    #Get the next cod to the db
    def get_next_cod(self):
        next_cod = self.cur.execute("SELECT MAX(cod) FROM {}".format(self.db_name)).fetchone()
        return int(next_cod[0])+1

    #Returns all the db
    def get_all(self):
        return self.cur.execute("SELECT * FROM {}".format(self.db_name)).fetchall()


    def open_db(self):
        self.con = sqlite3.connect(self.db_path)
        self.cur = self.con.cursor()

    #close the db
    def close_db(self):
        self.cur.close()
