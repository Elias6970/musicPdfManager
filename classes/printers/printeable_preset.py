from classes.printers.printeable_element import PrinteableElement
from classes.files_management.dir import Dir
from classes.presets.preset import Preset

#Printeable file
#The id is used to delete it from the status console
class PrinteablePreset(PrinteableElement):
    def __init__(self,copies:int):
        super().__init__(copies=copies)
        self.preset:Preset = None
        self.dir:Dir = None

    def set_preset(self,preset:Preset):
        self.preset = preset
    
    def set_dir(self,dir:Dir):
        self.dir = dir
        