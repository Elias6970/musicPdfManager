import json
#from classes.classifier import Text_analizer
#from classes.db_manage import Db_presets

COPIES = "copies"
OTHER_OPTIONS = "other_options"


class Preset:
    def __init__(self,name:str) -> None:
        self.name:str = name
        self.instruments:dict[str, dict[str, int|list[str]]] = {}


    def set_preset(self,new_list:list[str]) -> bool:
        try:
            self.instruments = new_list
            return True
        except Exception:
            return False
    

    def add_instrument(self,instrument:str,num:int|str,other_options:list[str]) -> bool:
        try:
            self.instruments[instrument] = {COPIES:int(num),OTHER_OPTIONS:other_options}
            return True
        except Exception:
            return False
    
    #This function search in the list of possibilities(instruments) the str that
    #goes better with the instrument given.
    #Strings returned by priority order:
    #   1-Same instrument same number
    #   2-Same instrument different number -> selects the closest lower number 
    #   3-Same instrument without number -> only returns the instrument
    #   4-Different instrument -> Raise an error that will show a window to select another insturment to print
    @staticmethod
    def solve(instrument:str,possibilities:list[str]) -> str:
        pass

class PresetManager():
    def __init__(self):
        self.presets:list[Preset] = []

    def add_preset(self,preset:Preset):
        self.presets.append(preset)

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







if __name__ == "__main__":
    a = Preset("primer")
    a.add_instrument("oboe_1",3,["clarinete_1","flauta_1"])
    a.add_instrument("o",3,["m,v"])
    b = Preset("segundo_perset")
    b.add_instrument("clarinete_1",1,["clariente"])
    #print(a.instruments)

    pm = PresetManager()
    pm.add_preset(a)
    pm.add_preset(b)
    
    pm.dump("a.json")

    r = PresetManager()
    r.load("a.json")

    print(r.presets[1].instruments)

    




"""class Preset:
    def __init__(self) -> None:
        pass
    
    def solve(self,instrument:str,scores:list[str]):
        for i in scores:
            if instrument == i:
                return i
            elif re.split(r"(\d+)",instrument)[0] == re.split(r"(\d+)",i)[0]:
                if type(re.split(r"(\d+)",instrument)[1]) != any:
                    counter = 1
                    while(int(re.split(r"(\d+)",instrument)[1])-counter != re.split(r"(\d+)",i)[1]):
                        if int(re.split(r"(\d+)",instrument)[1])-counter == 0:
                            return i
                        
                        counter += 1
                    return i
            
            else:
                #There will throw an error because the are not the score of the instrument in the prefab
                pass
        
"""