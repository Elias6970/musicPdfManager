from classes.presets.pieces_preset.pieces_preset import PiecesPreset
from classes.constants.constants import PIECES_PRESETS_PATH, PIECES_PRESETS_PIECES, PIECES_PRESETS_PRESET, PIECES_PRESETS_COPIES
import json,os


# Class that manages all the presets
class PiecesPresetManager:
    def __init__(self):
        self.presets:list[PiecesPreset] = []
    

    def add_preset(self,preset:PiecesPreset) -> bool:
        if preset.name in self.get_names():
            return False
        
        self.presets.append(preset)
        return True

    def add_preset_by_elements(self,name:str, instrument_preset_name:str, copies:int|str, pieces:list[tuple[str,str]]):
        """
        Add a preset using a printeable preset object from the printer (used in the selector windows).
            :param name: Name of the preset
            :param instrument_preset_name: Name of the instrument preset selected
            :param pieces: List of tuples with the pieces std names and the preset selected for this piece
        """
        preset = PiecesPreset(name, instrument_preset_name)
        preset.pieces = pieces 
        preset.copies = int(copies)
        self.add_preset(preset)
        
    
    def remove_preset(self,preset_name:str):
        for i in self.presets:
            if i.name == preset_name:
                self.presets.remove(i)


    # Dump the presets from a file
    #If it's empty use the default path
    def dump(self,path:str|None=None):
        if path == None:
            path = PIECES_PRESETS_PATH()

        export_json = {}
        for i in self.presets:
            export_json.update(i.dump())

        with open(path,'w') as file:
            json.dump(export_json,file,indent=4)
    

    def load(self,path:str|None=None):
        """
        Load all the presets in this object removing the old ones.
            :param path: Path where the presets are. If it's None use the default path.
        """
        self.presets.clear()
        
        if path == None:
            path = PIECES_PRESETS_PATH()

        if os.path.exists(path) == False:
            return
        try: 
            with open(path,'r') as file:
                imported_json = json.load(file)
                for i in imported_json.keys():
                    print(i)
                    preset = PiecesPreset(i, imported_json[i][PIECES_PRESETS_PRESET])
                    preset.pieces = [tuple(item) for item in imported_json[i][PIECES_PRESETS_PIECES]] #Convert the list of list (json format) to list of tuples
                    preset.copies = int(imported_json[i][PIECES_PRESETS_COPIES])
                    self.add_preset(preset)
        except json.JSONDecodeError:
            print("Error loading pieces presets from file. The file is not a valid JSON.")
            return
    
    #Return the name of all presets
    def get_names(self):
        return [i.name for i in self.presets]
    
    #Return the first preset obj with the same name
    #If not return None
    def get_preset(self,name:str) -> PiecesPreset|None:
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