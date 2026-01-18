from classes.files_management.archive import Archive

class AddPieceController:
    def __init__(self,archive:Archive):
        self.archive = archive

    
    def add_piece(self, cod:int|str, name:str, author:str, type:str, files:list[str], handwritten:bool, digitalized:bool, parted:bool):
        """Add a musical piece to the archive if basic validation passes.
        Args:
            cod (int): Unique identifier for the piece; must be non-negative.
            name (str): Name of the piece; must not be empty or whitespace.
            author (str): Author or composer of the piece.
            type (str): The category or type of the piece.
            files (list[str]): Collection of file paths or file objects related to the piece. Can be empty.
            handwritten (bool): Flag indicating if the piece is handwritten.
            digitalized (bool): Flag indicating if the piece has been digitized.
            parted (bool): Flag indicating if the piece is separated into parts.
        Returns:
            bool: True if the piece is added successfully; False if validation fails or the archive rejects the addition.
        """
        
        if int(cod) < 0 or name.strip() == "":
            return False
        
        is_added = self.archive.add_piece(cod=int(cod),
                                          name=name,
                                          author=author,
                                          type=type,
                                          files=files,
                                          handwritten=handwritten,
                                          digitalized=digitalized,
                                          parted=parted)
        return is_added
    
    def add_files_to_piece(self, parsed_name:str, files:list[str]) -> bool:
        """Add files to an existing piece in the archive.
        Args:
            parsed_name (str): Standardized name of the piece to which files will be added.
            files (list[str]): List of file paths or file objects to add to the piece.
        Returns:
            bool: True if files are added successfully; False otherwise.
        """
        return self.archive.add_files_to_piece(parsed_name,files)
