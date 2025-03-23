from classes.presets.preset import Preset
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
    def dump(self,path:str):
        export_json = {}
        for i in self.presets:
            export_json[i.name] = i.instruments

        with open(path,'w') as file:
            json.dump(export_json,file,indent=4)
    

    # Save the presets in a file
    def load(self,path:str):
        with open(path,'r') as file:
            imported_json = json.load(file)
            for i in imported_json.keys():
                preset = Preset(i)
                preset.instruments = imported_json[i]
                self.add_preset(preset)
    
    #Return the name of all presets
    def get_names(self):
        return [i.name for i in self.presets]