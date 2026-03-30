import os
from backend.app.files_management.archive_file_manager import ArchiveFileManager

def get_scores(piece_std_name: str, file_manager: ArchiveFileManager, extension: bool = True) -> list[str]:
    """
    Get all the scores from a piece.
    
    :param piece_std_name: Standard name of the piece.
    :param file_manager: ArchiveFileManager object.
    :param extension: Whether to include the file extension in the returned strings. Defaults to False.
    :return: A list of string representations of the scores.
    """
    scores = file_manager.get_scores(piece_std_name)
    if not extension:
        return [os.path.splitext(score)[0] for score in scores]
    return scores
