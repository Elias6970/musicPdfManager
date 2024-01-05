import re
from classes.classifier import Text_analizer
from classes.db_manage import Db_presets

class Preset:
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
        


if __name__ == "__main__":
    pass
    #print(re.split(r"(\d+)","clarinete")[0])
