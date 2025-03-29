import enum

class PresetResolverStates(enum.Enum):
    RESOLVED = 1 #Resolved with a direct user input (same name or name in other options)
    AUTO_RESOLVED = 2 #Resolved by the program logic like the same instrument with other name
    NOT_RESOLVED = 3 #Not resolved with any option
