from classes.presets.preset_resolver_states import PresetResolverStates
import re

#Class to wrap the resolution of an instrument + score
class ResolvedPresetInstrument:
    def __init__(self,state:PresetResolverStates,copies:int,piece:str,instrument:str,resolution:str|None=None):
        self.state:PresetResolverStates = state
        self.copies:int = copies
        self.piece:str = piece
        self.instrument:str = instrument
        self.resolution:str|None = resolution #Path to the pdf for this instrument
    
    