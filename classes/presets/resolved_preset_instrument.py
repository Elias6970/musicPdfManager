from classes.presets.preset_resolver_states import PresetResolverStates

#Class to wrap the resolution of an instrument + score
class ResolvedPresetInstrument:
    def __init__(self,state:PresetResolverStates,copies:int,piece:str,instrument:str,resolution:str|None=None):
        self.state:PresetResolverStates = state
        self.copies:int = copies
        self.piece:str = piece
        self.instrument:str = instrument
        self.resolution:str|None = resolution #Path to the pdf for this instrument
    
    def __eq__(self, value):
        if isinstance(value,ResolvedPresetInstrument):
            return (self.state == value.state and
                   self.copies == value.copies and
                   self.piece == value.piece and
                   self.instrument == value.instrument and
                   self.resolution == value.resolution)
        
        return super().__eq__(value)
    