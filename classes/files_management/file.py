import os

#Represent a file in the directory structure
class File:
    def __init__(self,path):
        self.path = path
    
    def set_path(self,path):
        self.path = path
    
    def remove(self):
        os.remove(self.path)

    @staticmethod
    def is_pdf(path:str):
        extension = os.path.splitext(path) #Extract the extension
        if ".pdf" == extension[1]:
            return True
        return False