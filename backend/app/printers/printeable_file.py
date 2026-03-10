from backend.app.files_management.file import File
from backend.app.printers.printeable_element import PrinteableElement

#Printeable file
#The id is used to delete it from the status console
class PrinteableFile(File,PrinteableElement):
    def __init__(self, path,copies:int):
        File.__init__(self,path=path)
        PrinteableElement.__init__(self,copies=copies)
