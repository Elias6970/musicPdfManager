from classes.constants.constants import PIECES_PRESETS_PIECES, PIECES_PRESETS_PRESET, PIECES_PRESETS_COPIES

class PiecesPreset:
    """Class to save preset of selected pieces.
    pieces is a list of tuples because with this strucutre we can save the same piece with different presets and copies.
    Example:
        "name" : {
            "preset" : "preset_name",
            "pieces" : [("piece_std_name_1", "preset", "copies"), ("piece_std_name_2", "preset", "copies"),...]
        }
    """

    def __init__(self, name:str, preset_name:str) -> None:
        """
        :param name: Name of the pieces preset
        :param preset_name: Name of the instrument selected
        """
        self.name:str = name
        self.preset_name:str = preset_name
        self.pieces:list[tuple[str,str,str]] = []

    def add_piece(self, piece_std_name:str, preset_name:str, copies:int|str) -> bool:
        """Add a piece to the pieces preset"""
        try:
            self.pieces.append((piece_std_name, preset_name, str(copies)))
            return True
        except Exception:
            return False
    
    def change_all_instruments_presets(self, preset_name: str) -> bool:
        """
        Update the instruments preset for every piece
        
        Args:
            preset_name (str): The new preset identifier to apply to all pieces.

        Returns:
            bool: True if the preset assignments were updated successfully; False otherwise.
        """
        try:
            self.pieces = [(piece_std_name, preset_name, copies) for piece_std_name, _, copies in self.pieces]
            return True
        except Exception:
            return False

    def dump(self) -> dict:
        """Dump the preset to a dict"""
        return {
            self.name: {
                PIECES_PRESETS_PRESET: self.preset_name,
                PIECES_PRESETS_PIECES: self.pieces
            }
        }

    def __str__(self) -> str:
        """String representation of the preset"""
        return f"PiecesPreset(name={self.name}, preset_name={self.preset_name}, pieces={self.pieces})"