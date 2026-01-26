import sqlite3
from classes.constants.constants import DB_PATH, DB_PIECES_TABLE
from classes.error import IncorrectCodOrNameError, CodAlreadyExistsError

#Abstraction of a class that represets a db
class Db:
    def __init__(self,table_name) -> None:
        self.table_name = table_name
        self.db_path = DB_PATH()
        
        self.open_db()
        self.create_tables()

    #Set up the tables 
    def create_tables(self) -> None:...

    def open_db(self):
        self.con = sqlite3.connect(self.db_path)
        self.cur = self.con.cursor()
    
    #close the db
    def close_db(self):
        self.cur.close()


#Manages the archive table in the db
#---Data table(named AMVR_archive):
#       Cod: internal cod that uses the db and is defined in the archive. Is not set automatically and can be repeated because you could have a local archive and add scores not in order
#       Name: name of the piece
#       Author: author of the piece
#       type: type of the score 
#       created_date: date when the score was added to the db, is set automatically
#       last_modification: last date when the row was modified, is set automatically
#       digitalized: can be 0,1 if the piece is in the directory archive(if its pdf score exists)
#       handwritten: can be 0,1 if the piece is digital or handwritten. All the pieces was set to 0 but in the future we need to be set to null and 0 or 1 deppending on their type
#       parted: can be 0,1 if the score was parted with the classify tools of the program that splits the pdf by type of instrument
class Db_archive(Db):
    def __init__(self,table_name):
        super(Db_archive,self).__init__(table_name)

    def create_tables(self) -> None:

        self.cur.execute("PRAGMA foreign_keys = 1") #Enable foreign keys

        self.cur.execute("CREATE TABLE IF NOT EXISTS {} (cod INTEGER PRIMARY KEY,name TEXT NOT NULL,author TEXT,type TEXT,created_date DATE,last_modification DATE,digitalized INTEGER DEFAULT 0,handwritten INTEGER DEFAULT 0,parted INTEGER DEFAULT 0)".format(self.table_name))

        self.con.commit()


    #Insert a score in the db
    def insert(self,cod:int, name:str, author:str="", type="",handwritten=0,parted=0,digitalized=0, commit=True) -> bool:
        """
        Insert a piece into the db. It can raise IncorrectCodOrNameError and CodAlreadyExistsError exceptions
        """
        try: 
            #Check if cod>0 and have name
            if int(cod) > 0 and name is not None and len(name.strip()) > 0:

                self.cur.execute("INSERT INTO {} (cod, name, author, type, created_date, last_modification, digitalized, handwritten, parted) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, ?, ?, ?)".format(self.table_name), (str(cod), str(name), str(author), str(type),digitalized,handwritten,parted))
                if commit:
                    self.con.commit()
                return True
            
            else:
                print("Error inserting: Incorrect code or name")
                raise IncorrectCodOrNameError("Incorrect code or name")#Jump to the except statement

        except sqlite3.IntegrityError as e: #cod repited
            print("Error inserting: This piece already exists")
            raise CodAlreadyExistsError("This piece already exists")

        except Exception as e:
            print(f"Exception inserting: {e}")

        return False
    
    def massive_insert(self, pieces:list[tuple[int,str,str,str]]) -> int:
        """
        Insert multiple pieces into the db. It returns the number of pieces inserted correctly.
        Each piece is a tuple with (cod:int, name:str, author:str, type:str). 
        Handwritten, parted and digitalized are set to 0 by default.

        :param pieces: List of pieces to insert.
        :type pieces: list[tuple[int,str,str,str]]
        :return: Number of pieces inserted correctly.
        :rtype: int
        """
        inserted = 0
        for piece in pieces:
            try:
                if self.insert(piece[0],piece[1],piece[2],piece[3], 0, 0, 0, commit=False):
                    inserted += 1
            except (IncorrectCodOrNameError, CodAlreadyExistsError):
                print("Skipping piece due to error:", piece)
        
        self.con.commit()

        return inserted


    def delete_score(self,cod):
        self.cur.execute("DELETE FROM {} WHERE cod = {}".format(self.table_name,cod))
        self.con.commit()


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
            self.cur.execute("PRAGMA case_sensitive_like = false")
            
            extracted = self.cur.execute("SELECT {} FROM {} WHERE {} LIKE '%{}%'".format(returned_camps,self.table_name,camp_to_compare,value))

        except Exception as e:
            print(f"{type(e)}:{e}")
            return ["0"]
        
        return extracted.fetchall()


    #Make the get but comparing with '=' not with LIKE % %
    def get_with_equals(self,camp_to_compare:str,value:str,returned_camps='*'):
        try:
            extracted = self.cur.execute("SELECT {} FROM {} WHERE {} = '{}'".format(returned_camps,self.table_name,camp_to_compare,value))

        except Exception as e:
            print(f"{type(e)}:{e}")
            return ["0"]
        
        return extracted.fetchall()


    #Get the next cod to the db
    def get_next_cod(self):
        next_cod = self.cur.execute("SELECT MAX(cod) FROM {}".format(self.table_name)).fetchone()
        if next_cod[0] == None or str(next_cod[0]).strip() == "":
            return 1 #When the db is empty
        return int(next_cod[0])+1


    #Returns all the db(without parted, handwritten,created_date and last_modification)
    def get_all_to_print(self):
        return self.cur.execute("SELECT CASE WHEN digitalized = '1' THEN 'x' WHEN digitalized = '0' THEN ' ' END AS modified_column,cod,name,author,type FROM {} ORDER BY name".format(self.table_name)).fetchall()

    #Return a list of tuples with all COD-name in the db
    #The name returned is the name in the db(not upper)
    def get_all_parsed_names(self):
        return self.cur.execute("SELECT COD || '-' || NAME AS CODNAME FROM {}".format(self.table_name)).fetchall()
    
    #returns all the names, cods and digitalized flag in a list of tuples
    def get_all_cod_name_digitalized(self):
        return self.cur.execute("SELECT COD,NAME,DIGITALIZED FROM {}".format(self.table_name)).fetchall()
    
    #Try to insert a new row, if it is not possible it update the value of that row
    def upsert(self,old_cod,cod,name,author,type,handwritten=0,digitalized=0,parted=0):
        try: 
            if cod > 0 and name is not None and len(name.strip()) > 0 and old_cod != cod:
                self.cur.execute("DELETE FROM {} WHERE cod = {} ".format(self.table_name,old_cod))
                self.cur.execute("INSERT INTO {} (cod, name, author, type, created_date, last_modification, digitalized, handwritten, parted) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 1, ?, ?)".format(self.table_name), (cod, name, author, type,handwritten,parted))
            else:
                self.cur.execute("UPDATE {} SET cod=?,name=?,author=?,type=?,last_modification=CURRENT_TIMESTAMP,digitalized=?,handwritten=?,parted=? WHERE cod=?".format(self.table_name),(cod,name,author,type,digitalized,handwritten,parted,cod))
            
            self.con.commit()
            return True
        
        except Exception as e:
            print(e,"Error introduciendo la obra: "+ str(name))#traducir

        return False


    #Update parted flag of one piece
    def update_parted(self,cod:str|int,parted:bool=True):
        self.cur.execute("UPDATE {} SET last_modification=CURRENT_TIMESTAMP,parted=? WHERE cod=?".format(self.table_name),(int(parted),str(cod)))
        self.con.commit()
        return True

    def update_digitalized(self,cod:str|int,digitalized:bool=True,commit:bool=True):
        self.cur.execute("UPDATE {} SET last_modification=CURRENT_TIMESTAMP,digitalized=? WHERE cod=?".format(self.table_name),(int(digitalized),str(cod)))
        if commit:
            self.con.commit()
        return True
    
    def update_digitalized_bulk(self,cods:list[int],digitalized:bool=True):
        for cod in cods:
            self.update_digitalized(cod,digitalized,commit=False)
        self.con.commit()

    #Check if a piece is parted
    def is_parted(self,cod) -> bool:
        if self.cur.execute("SELECT * FROM {} WHERE cod = '{}' and parted = 1".format(self.table_name,cod)).fetchall() == []:
            return False
        return True
    
    def is_digitalized(self,cod) -> bool:
        if self.cur.execute("SELECT * FROM {} WHERE cod = '{}' and digitalized = 1".format(self.table_name,cod)).fetchall() == []:
            return False
        return True
    

    def open_db(self):
        self.con = sqlite3.connect(self.db_path)
        self.cur = self.con.cursor()


    #close the db
    def close_db(self):
        self.cur.close()

    def correct_names(self):
        """
        Clean up leading and trailing whitespace in the `name` column for all rows in the current table.
        For each record, the method strips whitespace, updates the name and `last_modification` timestamp if it changed,
        commits the changes, and returns True on success or False if an exception is encountered.
        """
        try:
            rows = self.cur.execute(f"SELECT cod,name FROM {self.table_name}").fetchall()
            for cod, name in rows:
                if name is None:
                    continue
                fixed = str(name).strip()
                if fixed != name:
                    self.cur.execute(
                        f"UPDATE {self.table_name} SET name=?,last_modification=CURRENT_TIMESTAMP WHERE cod=?",
                        (fixed, cod),
                    )
            self.con.commit()
            return True
        except Exception as e:
            print(f"{type(e)}:{e}")
            return False


#---Presets:
#       name: name of the preset
#       preset: has a str with instruments separated with commas. 
#               The instruments are represented like in the score classifier
#               (one letter or the complete name and can be a number)
class Db_presets(Db):
    def __init__(self, table_name):
        super(Db_presets,self).__init__(table_name)

        self.table_name = table_name
   
    def create_tables(self) -> None:
        self.cur.execute("CREATE TABLE IF NOT EXISTS {} (name TEXT NOT NULL,preset TEXT)".format(self.table_name))
        self.con.commit()

    def get_preset(self,name:str) -> list[tuple[str,str]]:
        return self.cur.execute("SELECT * FROM {} WHERE name = {}".format(self.table_name,name)).fetchall()
    
    def get_presets(self) -> list[tuple[str,str]]:
        return self.cur.execute("SELECT * FROM {}".format(self.table_name)).fetchall()

    def save_preset(self,name:str,preset:str) -> bool:
        try:
            self.cur.execute("INSERT INTO {} (name, preset) VALUES ({},{})".format(self.table_name,name,preset))
            return True
        except Exception:
            return False