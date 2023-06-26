import sqlite3,os

class db:
    def __init__(self,name):
        self.name = name
        self.path = "./db/"+name
        try:
            os.remove(self.path)
        except:
            pass
        #Check if exists the db
        if os.path.exists(self.path):
            exists = True
        else:
            exists = False
        
        self.con = sqlite3.connect(self.path)
        self.cur = self.con.cursor()

        self.cur.execute("PRAGMA foreign_keys = 1") #Enable foreign keys

        
        self.cur.execute("CREATE TABLE general(cod INTEGER PRIMARY KEY,name VARCHAR(50),type VARCHAR(25),create_date DATE,last_modification DATE)")
        self.cur.execute("CREATE TABLE partes(cod1 INTEGER,oboe VARCHAR(50), FOREIGN KEY(cod1) REFERENCES general(cod) ON DELETE CASCADE)")

        self.cur.execute("INSERT INTO general(cod,name) VALUES (1,'Buen'),(2,'Mal')")
        


        self.cur.execute("INSERT INTO partes(cod1,oboe) VALUES (1,'afj'),(2,'asdj')")
       

        self.cur.execute("DELETE FROM general WHERE cod=1")
       
       
        self.con.commit()
        self.con.close()


if __name__ == "__main__":
    a = db("abc.db")