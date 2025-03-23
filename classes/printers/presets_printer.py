from classes.printers.printer import Printer
from classes.printers.printeable_preset import PrinteablePreset
from classes.presets.preset import Preset
from classes.files_management.dir import Dir

#This class represents a printer saving a list of pdfs to print
class PresetsPrinter(Printer):
    def __init__(self) -> None:
        super().__init__()
        self.items:list[PrinteablePreset] = []
    
    #Return the printeablePreset id to remove it from a list
    def add(self,copies:int,preset:Preset,dir:Dir) -> int:
        p = PrinteablePreset(copies)
        p.set_dir(dir)
        p.set_preset(preset)

        super().add(p)
        
        return p.id


    def remove(self,id:int) -> bool:
        return super().remove(id)
        

    def export(self,path:str) -> None:
        #Resolve presets
        #Merge them
        pass



