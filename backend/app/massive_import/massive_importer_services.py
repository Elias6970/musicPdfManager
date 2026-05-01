

from sqlmodel import Session

from backend.app.files_management.archive_file_manager import ArchiveFileManager
from backend.app.massive_import.excell_extractor_services import read_data
from backend.app.settings import get_server_settings
from backend.app.services.archive_services import add_piece_to_archive, add_file_to_existing_piece
from backend.app.models.piece import Piece, PieceCreate
from backend.app.massive_import.file_decompressor.file_decompressor_services import extract_nested_archives_in_memory
from backend.app.error import FileCouldNotBeReadException

import os

def massive_import(
    archive_id: int,
    excel_name_path: str,
    archive_name_path: str,
    session: Session,
    file_manager: ArchiveFileManager,
    ignore_first_excel_row: bool = True
) -> tuple[list[Piece], list[Piece], list[tuple[int, str, str]]]:
    """
    Perform a massive import of pieces and their associated files based on an Excel file and an archive. 
    It takes the cod from the excel and search for a folder with the same name in the archive, if it exist, it import the files in that folder to the system.
    
    Features:
    - It can uncompress files in the archive and add them to the archive. 
    - It delete duplicated files.

    Format:
    - The excell need to have the following format:
    | Piece Code | Piece Name | Author | Type |

    - The archive need to have the following format.
    /archive_name_path
        /cod-piece_name
            /score.pdf
            /extra_file_1.ext
            ...
    Args:
        excel_name_path (str): Name to the Excel file containing piece information in the temporary folder.
        archive_name_path (str): Name of the archive containing the pieces files in the temporary folder.
        file_manager (ArchiveFileManager): An instance of ArchiveFileManager to handle file operations.
    Returns:
        tuple(list[Piece], list[Piece], list[tuple[int, str, str]]): A tuple containing the list of successfully added pieces and files, the list of added pieces without files, and the list of pieces that could not be created.
    """
    full_added_pieces: list[Piece] = []
    pieces_without_files: list[Piece] = []
    not_added_pieces: list[tuple[int, str, str]] = [] # List of tuples with the code, name and error for the pieces that could not be created
    settings = get_server_settings()
    temp_folder = settings.temp_upload_folder

    data = read_data(file=os.path.join(temp_folder, excel_name_path), 
                      ignore_first_row=ignore_first_excel_row)
    
    for cod, name, author, type in data:
        piece = PieceCreate(
            archive_id=archive_id,
            cod=cod, 
            name=name, 
            author_name=author, 
            author_id=None,
            type_name=type,
            type_id=None,
            handwrited=False,
            parted=False,
            digitalized=False
        )
        try:
            piece_added = add_piece_to_archive(session=session, piece=piece, files = [], file_manager=file_manager)
        except Exception as e: #TODO: Change to a more specific exception
            print(f"Error adding piece {name}: {e}")
            not_added_pieces.append((cod, name, str(e)))
            continue

        if piece_added is not None and piece_added.id is not None:
            archive_piece_folder = None
            for i in os.listdir(os.path.join(temp_folder, archive_name_path)):
                file_path = os.path.join(temp_folder, archive_name_path, i)
                if os.path.isdir(file_path) and os.path.basename(i).startswith(str(cod)):
                    archive_piece_folder = file_path
                    break # Only detect the first folder that match with the code

            if not archive_piece_folder:
                print(f"No folder found in the archive for piece {piece_added.std_name}. Skipping file import for this piece.")
                pieces_without_files.append(piece_added)
                continue
            full_added_pieces.append(piece_added)

            if os.path.exists(archive_piece_folder) and os.path.isdir(archive_piece_folder):
                for root, dirs, files in os.walk(archive_piece_folder):
                    if 'partituras_sin_clasificar' in dirs:
                        dirs.remove('partituras_sin_clasificar') # Skip this folder because it was a backup folder from the old version of the application
                    
                    for filename in files:
                        file_path = os.path.join(root, filename)
                        if os.path.isfile(file_path) and not filename in [".DS_Store"] and not filename.startswith(("._", ".Spotlight")):
                            for file_name, file_bytes in extract_nested_archives_in_memory(file_path, file_path): # It need the path not the name because it needs to read the file
                                try:
                                    add_file_to_existing_piece(
                                    session=session, 
                                    piece_id=piece_added.id, 
                                    filename=os.path.basename(file_name), 
                                    file_bytes=file_bytes, 
                                    file_manager=file_manager
                                )
                                except ValueError as e:
                                    print(f"Error adding file '{file_name}' to piece '{piece_added.name}': {e}")
                                except FileCouldNotBeReadException as e:
                                    print(f"Error reading file '{file_name}' for piece '{piece_added.name}': {e}")

    
    return full_added_pieces, pieces_without_files, not_added_pieces