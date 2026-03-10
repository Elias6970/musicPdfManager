from backend.app.constants.constants import PRESETS_COPIES,PRESETS_OTHER_OPTIONS,PRESETS_PATH
import json

class Preset:
    """
    Class that represents a fixed amount of different instruments 
    Each instrument has the name, the number of copies and a list with other options if the instrument doesn't exit
    Example preset:
    {
        "oboe" : {
            PRESETS_COPIES : 3,
            PRESETS_OTHER_OPTIONS : ["flauta_1","clarinete_1"]
        }
    }
    """

    def __init__(self,name:str) -> None:
        self.name:str = name
        self.instruments:dict[str, dict[str, int|list[str]]] = {}

    # Add instrument to the preset
    #   instrument: name of the instrument with the number
    #   num: number of copies of this instrument
    #   other_options: list to options to substitute this instrument if it doesn't exist in a piece. 
    #                  The options are checked in order.
    def add_instrument(self,instrument:str,copies:int|str,other_options:list[str]=[]) -> bool:
        try:
            self.instruments[instrument] = {PRESETS_COPIES:int(copies),PRESETS_OTHER_OPTIONS:other_options}
            return True
        except Exception:
            return False
    

    def print(self) -> str:
        """Return a string to print the preset"""

        out = ""
        for i,value in enumerate(self.instruments.keys()):
            out += "   " + str(self.instruments[value][PRESETS_COPIES]) + "x " + str(value)
            
            if i+1 < len(self.instruments):
                out += "\n"

        return out



    def dump(self,path:str|None=None):
        """Save or update. If there is a preset with the same name it will overwrite it"""
        if path == None:
            path = PRESETS_PATH()
        
        with open(path,'r+') as file:
            data = json.load(file)
            data[self.name] = self.instruments

            file.seek(0)
            json.dump(data,file,indent=4)
            file.truncate()