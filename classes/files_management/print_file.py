from classes.files_management.file import File

#Printeable file
#The id is used to delete it from the status console
class PrintFile(File):
    _id_counter = 0
    def __init__(self, path,copies:int):
        super().__init__(path)
        self.id = PrintFile._id_counter
        PrintFile._id_counter += 1
        self.copies = copies