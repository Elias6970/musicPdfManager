from classes.presets.preset import Preset
from classes.constants import PRESETS_COPIES,PRESETS_OTHER_OPTIONS,DIR_SCORES
from classes.presets.preset_resolver_states import PresetResolverStates
from classes.presets.resolved_preset_instrument import ResolvedPresetInstrument
from classes.files_management.dir import Dir
import re,os

#Not implemented
#Si no está el mismo devuelves uno por arriba,
#Prioridades:
#   El mismo
#   Mismo nombre uno por encima
#   Mismo nombre uno por debajo
#   Mismo nombre sin número


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
    #   dir: dir to get the scores and the name of the piece
    #   ignore_copies: boolean to ignore the number of copies of each instrument.
    #                   if false copies=1
    #
    #Return a ResolvedPresetInstrument object 
    @staticmethod
    def resolve(preset:Preset,dir:Dir,ignore_copies:bool) -> list[ResolvedPresetInstrument]:
        result = []
        scores = dir.get_scores_names()
        for i in preset.instruments.keys():
            founded_in_other_options = False
            if ignore_copies:
                copies = 1
            else:
                copies = preset.instruments[i][PRESETS_COPIES]
            # Check if there is the exact same instrument
            if i in scores:
                result.append(ResolvedPresetInstrument(PresetResolverStates.RESOLVED,
                                                       copies,
                                                       dir.name,
                                                       i,
                                                       os.path.join(dir.path,DIR_SCORES,i+".pdf")))
                continue
        
            # Check the other options for the instrument
            for j in preset.instruments[i][PRESETS_OTHER_OPTIONS]:
                
                if j in scores:
                    result.append(ResolvedPresetInstrument(PresetResolverStates.RESOLVED,
                                                           copies,
                                                           dir.name,
                                                           i,
                                                           os.path.join(dir.path,DIR_SCORES,j+".pdf")))
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
            result.append(ResolvedPresetInstrument(PresetResolverStates.NOT_RESOLVED,
                                                   copies,
                                                   dir.name,
                                                   i))
            
        return result