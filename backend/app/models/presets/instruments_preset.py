from sqlmodel import SQLModel, Field

class InstrumentConfig(SQLModel):
    copies:int
    other_options:list[str]

class InstrumentsPreset(SQLModel):
    """
    Save a fixed amount of instruments.
    Each instrument has the name, the number of copies and 
    a list with other options if the instrument's score doesn't exit
    Example preset:
    {
        "oboe" : {
            PRESETS_COPIES : 3,
            PRESETS_OTHER_OPTIONS : ["flauta_1","clarinete_1"]
        }
    }
    """
    name:str
    instruments:dict[str, InstrumentConfig] = Field(default_factory=dict)
