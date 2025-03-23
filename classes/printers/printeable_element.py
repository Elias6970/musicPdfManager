
#The id is used to delete it from the status console
class PrinteableElement():
    _id_counter = 0
    def __init__(self,copies:int):
        self.id = PrinteableElement._id_counter
        PrinteableElement._id_counter += 1
        self.copies = copies
