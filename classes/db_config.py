import sqlite3,datetime
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
            print("Error, ya existe esa obra")

        except Exception as e:
            print("Error introduciendo la obra, ",type(e))
    

    def insert_from_excel(self,file):
        pass

    #Get rows from the db
        #type:
        #   cod->get row by the cod
        #   name->get rows with similar name
        #   author->get rows with similar author
        #   Can be used with dates but it doesn't work correctly
    def get(self,type,value): 
        try:
            self.cur.execute("PRAGMA case_sensitive_like = true")
            
            line = self.cur.execute("SELECT * FROM archive WHERE {} like '%{}%'".format(type,value))

        except Exception as e:
            print(e)
            return 0
        
        return line.fetchall()


    #Returns all the db
    def get_all(self):
        return self.cur.execute("SELECT * FROM archive").fetchall()

