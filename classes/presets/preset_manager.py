from classes.presets.preset import Preset
from classes.constants.constants import PRESETS_PATH
import json


# Class that manages all the presets
class PresetManager():
    def __init__(self):
        self.presets:list[Preset] = []
    

    def add_preset(self,preset:Preset):
        self.presets.append(preset)


    def remove_preset(self,preset_name:str):
        for i in self.presets:
            if i.name == preset_name:
                self.presets.remove(i)


    # Dump the presets from a file
    #If it's empty use the default path
    def dump(self,path:str|None=None):
        if path == None:
            path = PRESETS_PATH()

        export_json = {}
        for i in self.presets:
            export_json[i.name] = i.instruments

        with open(path,'w') as file:
            json.dump(export_json,file,indent=4)
    

    # Save the presets in a file
    #If it's empty use the default path
    def load(self,path:str|None=None):
        self.presets.clear()
        
        if path == None:
            path = PRESETS_PATH()
        
        with open(path,'r') as file:
            imported_json = json.load(file)
            for i in imported_json.keys():
                preset = Preset(i)
                preset.instruments = imported_json[i]
                self.add_preset(preset)
    
    #Return the name of all presets
    def get_names(self):
        return [i.name for i in self.presets]
    
    #Return the first preset obj with the same name
    #If not return None
    def get_preset(self,name:str) -> Preset|None:
        for i in self.presets:
            if i.name == name:
                return i
        return None
    
    #Return if a preset exist in the list
    def exist(self,name:str) -> bool:
        for i in self.presets:
            if i.name == name:
                return True
        
        return False