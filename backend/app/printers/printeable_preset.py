from backend.app.printers.printeable_element import PrinteableElement
from backend.app.files_management.dir import Dir
from backend.app.presets.preset import Preset
from backend.app.utils.name_manager import NameManager

#Printeable file
#The id is used to delete it from the status console
class PrinteablePreset(PrinteableElement):
    def __init__(self,copies:int):
        super().__init__(copies=copies)
        self.preset:Preset
        self.dir:Dir

    def set_preset(self,preset:Preset):
        self.preset = preset
    
    def set_dir(self,dir:Dir):
        self.dir = dir
        
    #Custom method less than to order by name of the dir
    def __lt__(self,other):
        if isinstance(other, PrinteablePreset):
            NameManager.get_name(self.dir.name) < NameManager.get_name(other.dir.name)
        
        return super().__lt__(other)#Different types