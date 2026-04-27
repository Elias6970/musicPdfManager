import os, fitz
from backend.app.constants.constants import DIR_SCORES
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

def get_score_page_count(piece_std_name: str, file_manager: ArchiveFileManager, score_file: str) -> int:
    """
    Get the page count of a specific score.

    :param piece_std_name: Standard name of the piece.
    :param file_manager: ArchiveFileManager object.
    :param score_file: Name of the score file.
    :return: The number of pages in the score.

    Raises:
        FileNotFoundError: If the score file does not exist.
        ValueError: If there is an error opening the PDF file.
    """
    try:
        piece_name = ArchiveFileManager.parse_name_to_file_manager(piece_std_name)
        pdf_path = os.path.join(file_manager.archive_path, piece_name, DIR_SCORES, score_file)
        doc = fitz.open(pdf_path)
        return doc.page_count
    except Exception as e:
        raise ValueError(f"Error opening PDF file: {str(e)}")

def get_scores_and_page_counts(piece_std_name: str, file_manager: ArchiveFileManager) -> list[tuple[str, int]]:
    """
    Get a list of tuples containing score names and their corresponding page counts.

    :param piece_std_name: Standard name of the piece.
    :param file_manager: ArchiveFileManager object.
    :return: A list of tuples where each tuple contains a score name and its page count.

    Raises:
        FileNotFoundError: If any of the score files do not exist.
        ValueError: If there is an error opening any of the PDF files.
    """
    scores = get_scores(piece_std_name, file_manager)
    return [(score, get_score_page_count(piece_std_name, file_manager, score)) for score in scores]