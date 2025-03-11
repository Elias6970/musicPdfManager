from classes.presets.preset import Preset
from classes.constants import PRESETS_COPIES,PRESETS_OTHER_OPTIONS
import enum,re

#Si no está el mismo devuelves uno por arriba,
#Prioridades:
#   El mismo
#   Mismo nombre uno por encima
#   Mismo nombre uno por debajo
#   Mismo nombre sin número


class PresetResolverStates(enum.Enum):
    RESOLVED = 1 #Resolved with a direct user input (same name or name in other options)
    AUTO_RESOLVED = 2 #Resolved by the program logic like the same instrument with other name
    NOT_RESOLVED = 3 #Not resolved with any option

class PresetResolver():
    # Check if there is the same instrument with a lower number or no number 
    # NOT WORKING NOT TESTED
    @staticmethod
    def same_instrument_different_number(preset_instrument:str,scores:list[str]) -> str|None:
        #Comprobation because maybe it is in the list (function not used in this class)
        if preset_instrument in scores:
            return  preset_instrument
        

        splitted = re.split(r"(_\d+)",preset_instrument)
        re_to_split = r"(_\d+)"
        
        matched_scores = filter(lambda x: len(re.split(re_to_split,x)[0] == preset_instrument),scores)
        matched_scores = filter
        matched_scores = list(matched_scores).sort()

        #The preset instrument has number
        if len(re.split(re_to_split,preset_instrument)) > 1:
            return matched_scores[0]
        
        #for i,value in enumerate(matched_scores,start=1):
            #if matched_scores[i-1] < matched_scores[i]

            
        return None
    
    #Decide the scores that will be printed with the preset
    #   preset: Preset to resolve
    #   scores: List of scores to resolve
    #
    # Returns a list in which each element is an instrument in the preset:
    #   1- int: State of the preset resolution
    #   2- int: Number of copies of the instrument
    #   3- str: Preset's instrument
    #   4- str|None: Resolved score related to the preset. If the state is NOT_RESOLVED it is None
    @staticmethod
    def resolve(preset:Preset,scores:list[str]) -> list[tuple[int,int,str,str|None]]:
        result = []
        for i in preset.instruments.keys():
            founded_in_other_options = False

            # Check if there is the exact same instrument
            if i in scores:
                result.append((PresetResolverStates.RESOLVED,preset.instruments[i][PRESETS_COPIES],i,i))
                continue
        
            # Check the other options for the instrument
            for j in preset.instruments[i][PRESETS_OTHER_OPTIONS]:
                
                if j in scores:
                    result.append((PresetResolverStates.RESOLVED,preset.instruments[i][PRESETS_COPIES],i,j))
                    founded_in_other_options = True
                    break
            if founded_in_other_options:
                continue

            #Check the same instrument but a higher number
            #sol = PresetResolver.same_instrument_different_number(i,scores)
            #if sol != None:
            #  result.append((PresetResolverStates.AUTO_RESOLVED,preset.instruments[i][PRESETS_COPIES],i,sol))
            #  continue


            #Special options like principal clarinet

            #Unresolved
            result.append((PresetResolverStates.NOT_RESOLVED,preset.instruments[i][PRESETS_COPIES],i))

        return result