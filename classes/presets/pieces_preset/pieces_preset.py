from classes.constants.constants import PIECES_PRESETS_PIECES, PIECES_PRESETS_PRESET, PIECES_PRESETS_COPIES

class PiecesPreset:
    """Class to save preset of selected pieces.
    Example:
        "name" : {
            "preset" : "preset_name",
            "copies" : "copies",
            "pieces" : [("piece_std_name_1", "preset"), ("piece_std_name_2", "preset"),...]
        }
    """

    def __init__(self, name:str, preset_name:str) -> None:
        """
        :param name: Name of the pieces preset
        :param preset_name: Name of the instrument selected
        """
        self.name:str = name
        self.preset_name:str = preset_name
        self.pieces:list[tuple[str,str]] = []
        self.copies:int = 1

    def add_piece(self, piece_std_name:str, preset_name:str) -> bool:
        """Add a piece to the pieces preset"""
        try:
            self.pieces.append((piece_std_name, preset_name))
            return True
        except Exception:
            return False


    def dump(self) -> dict:
        """Dump the preset to a dict"""
        return {
            self.name: {
                PIECES_PRESETS_PRESET: self.preset_name,
                PIECES_PRESETS_COPIES: str(self.copies),
                PIECES_PRESETS_PIECES: self.pieces
            }
        }
