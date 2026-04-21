
from sqlmodel import Session
import os
import fitz
import shutil
import datetime
from backend.app.constants.constants import DIR_SCORES
from backend.app.files_management.archive_file_manager import ArchiveFileManager
from backend.app.models.classification.classification_job import ClassificationJob
from backend.app.models.classification.classified_document import ClassifiedDocument
from backend.app.services.archive_services import get_archive_path
from backend.app.error import ClassificationFileExistsError

def precheck_classification(session: Session, job: ClassificationJob):
    """
    Validates a ClassificationJob prior to execution to ensure all dependencies and configurations are correct.
    
    This function performs the following checks:
    - Verifies the existence of the referenced archive folder and the specific piece folder.
    - Confirms that all provided source PDF files exist.
    - Ensures every page referenced in the expected classifications belongs to the declared source files.
    - Analyzes potential file naming collisions for the resulting output PDFs. It automatically 
      processes collision resolution rules (overwrite or rename) and raises an error if any target files 
      already exist without a valid resolution strategy.
      
    Args:
        session (Session): The active database session.
        job (ClassificationJob): The classification job payload containing files and configurations to validate.
        
    Raises:
        FileNotFoundError: If the archive folder, piece folder, or any source file is not found.
        ValueError: If a source file is not a valid PDF or if a referenced source page is missing from source files.
        ClassificationFileExistsError: If target output files already exist and lack a valid overwrite or rename configuration.
    """
    # Check that archive_id exists
    archive_folder = get_archive_path(session, job.archive_id)
    if not archive_folder or not os.path.exists(archive_folder):
        raise FileNotFoundError(f"Archive loosely tied to ID '{job.archive_id}' not found.")
        
    # Check that piece exists
    piece_folder = ArchiveFileManager.parse_name_to_file_manager(job.piece_std_name)
    piece_path = os.path.join(archive_folder, piece_folder)
    if not os.path.exists(piece_path):
        raise FileNotFoundError(f"Piece folder not found: {piece_path}")
        
    scores_path = os.path.join(piece_path, DIR_SCORES)

    # Check that all source files exist and are valid PDFs
    for filename in job.source_files:
        file_path = os.path.join(scores_path, filename)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Source file not found: {file_path}")
        if not file_path.lower().endswith('.pdf'):
            raise ValueError(f"Invalid file type (not a PDF): {file_path}")

    # Process classifications and validate source pages
    incorrect_keys = []
    
    # Iterate over a copy of the dictionary items because we might modify keys
    for key, doc in list(job.classifications.items()):
        
        # Check that all files in SourcePage are in source_files
        for page in doc.pages:
            if page.file_name not in job.source_files:
                raise ValueError(f"Source page file '{page.file_name}' not found in source_files.")
                
        target_name = f"{key}.pdf"
        target_path = os.path.join(scores_path, target_name)
        
        if os.path.exists(target_path):
            if doc.config.overwrite:
                continue
            elif doc.config.rename and doc.config.rename.strip():
                new_key = doc.config.rename.strip()
                job.classifications[new_key] = job.classifications.pop(key)
            else:
                incorrect_keys.append(key)
                
    if incorrect_keys:
        raise ClassificationFileExistsError(
            f"Target files already exist and no valid rename or overwrite strategy provided for: {', '.join(incorrect_keys)}",
            incorrect_keys
        )

def extract_and_merge_pages(classifications: dict[str, ClassifiedDocument], source_dir: str) -> dict[str, bytes]:
    """
    Extracts specified pages from source PDF files and merges them into new PDFs.
    
    Args:
        session (Session): The active database session.
        classifications (dict[str, ClassifiedDocument]): A dictionary mapping output file identifiers 
            to their specific page structure and configuration.
        source_dir (str): The root directory where the source PDFs are located.
        
    Returns:
        dict[str, bytes]: A dictionary where the keys are the target filenames string (with .pdf extension) 
        and the values are the generated raw PDF bytes.
    """
    generated_pdfs: dict[str, bytes] = {}
    open_source_pdfs: dict[str, fitz.Document] = {}

    try:
        for key, doc in classifications.items():
            target_filename = f"{key}.pdf"
            merged_pdf = fitz.open()
            
            for page_info in doc.pages:
                source_filename = page_info.file_name
                page_idx = page_info.page
                
                # Open source PDF and cache it if not already opened
                if source_filename not in open_source_pdfs:
                    source_path = os.path.join(source_dir, source_filename)
                    open_source_pdfs[source_filename] = fitz.open(source_path)
                    
                source_pdf = open_source_pdfs[source_filename]
                
                # Append the specific page
                merged_pdf.insert_pdf(source_pdf, from_page=page_idx, to_page=page_idx)
                
            # Save newly created document as bytes
            generated_pdfs[target_filename] = merged_pdf.tobytes()
            merged_pdf.close()
            
    finally:
        # Guarantee that all source PDFs are closed properly
        for source_pdf in open_source_pdfs.values():
            source_pdf.close()
            
    return generated_pdfs


def backup_source_files(session: Session, archive_id: int, piece_std_name: str, filenames: list[str]) -> str:
    """
    Moves a specified list of source files from the scores directory into a backup folder.
    
    Returns:
        str: The name of the created backup folder (format YYYY-MM-DD_HH-MM-SS).
    """
    archive_folder = get_archive_path(session, archive_id)
    piece_folder = ArchiveFileManager.parse_name_to_file_manager(piece_std_name)
    piece_path = os.path.join(archive_folder, piece_folder)
    scores_path = os.path.join(piece_path, DIR_SCORES)
    backup_path = os.path.join(piece_path, "backup")

    date_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    target_backup_path = os.path.join(backup_path, date_str)
    
    if not os.path.exists(target_backup_path):
        os.makedirs(target_backup_path)

    for filename in filenames:
        file_path = os.path.join(scores_path, filename)
        if os.path.exists(file_path):
            shutil.move(file_path, os.path.join(target_backup_path, filename))

    return date_str


def restore_last_backup(session: Session, archive_id: int, piece_std_name: str):
    """
    Moves files from the most recent backup folder back to the original scores directory.
    """
    archive_folder = get_archive_path(session, archive_id)
    piece_folder = ArchiveFileManager.parse_name_to_file_manager(piece_std_name)
    piece_path = os.path.join(archive_folder, piece_folder)
    scores_path = os.path.join(piece_path, DIR_SCORES)
    backup_path = os.path.join(piece_path, "backup")

    if not os.path.exists(backup_path):
        raise FileNotFoundError(f"Backup folder not found at {backup_path}")

    # List only directories inside the backup folder
    backups = [d for d in os.listdir(backup_path) if os.path.isdir(os.path.join(backup_path, d))]
    
    if not backups:
        raise FileNotFoundError("No backups found to restore.")

    # Sort to easily get the latest by date/time string
    last_backup_folder = sorted(backups)[-1]
    last_backup_path = os.path.join(backup_path, last_backup_folder)

    # Move files back to scores directory
    for filename in os.listdir(last_backup_path):
        file_path = os.path.join(last_backup_path, filename)
        if os.path.isfile(file_path):
            shutil.move(file_path, os.path.join(scores_path, filename))

    # Clean up empty backup directory
    shutil.rmtree(last_backup_path)


def save_generated_pdfs(session: Session, archive_id: int, piece_std_name: str, generated_pdfs: dict[str, bytes]):
    """
    Saves the generated PDF bytes to the piece's scores directory.
    
    Args:
        session (Session): The active database session.
        archive_id (int): The unique identifier of the archive.
        piece_std_name (str): The standardized name of the music piece.
        generated_pdfs (dict[str, bytes]): A dictionary mapping filenames to PDF bytes.
    """
    archive_folder = get_archive_path(session, archive_id)
    piece_folder = ArchiveFileManager.parse_name_to_file_manager(piece_std_name)
    scores_path = os.path.join(archive_folder, piece_folder, DIR_SCORES)
    
    for filename, pdf_bytes in generated_pdfs.items():
        file_path = os.path.join(scores_path, filename)
        with open(file_path, "wb") as f:
            f.write(pdf_bytes)


def classify(session: Session, job: ClassificationJob) -> bool:
    """
    Executes the complete classification pipeline.
    
    This function coordinates the multi-step process for classifying pages:
    1. Validates the existence of required directories and files, and handles collision rules.
    2. Extracts the exact specified pages from the source PDF files and merges them in memory.
    3. Moves the original source PDF files into a safe backup folder.
    4. Writes the newly created PDF files into the scores directory.
    
    If saving the new PDFs fails, it attempts to rollback by restoring the source files from the backup.
    
    Args:
        session (Session): The active database session.
        job (ClassificationJob): The classification job payload.
        
    Returns:
        bool: True if the process completed successfully.
        
    Raises:
        FileNotFoundError: If the archive folder, piece folder, or any required source file is missing.
        ValueError: If a source file is invalid or a source page reference doesn't match the source files.
        ClassificationFileExistsError: If target files already exist with no valid overwrite/rename rule.
        Exception: Any arbitrary exception triggered during PDF writing or processing (will trigger a rollback before re-raising).
    """
    # 1. Precheck
    precheck_classification(session, job)
    
    # Resolve scores directory
    archive_folder = get_archive_path(session, job.archive_id)
    piece_folder = ArchiveFileManager.parse_name_to_file_manager(job.piece_std_name)
    scores_path = os.path.join(archive_folder, piece_folder, DIR_SCORES)

    # 2. Extract and merge pages
    generated_pdfs = extract_and_merge_pages(job.classifications, scores_path)
    
    # 3. Remove/Move source files to backup
    backup_source_files(session, job.archive_id, job.piece_std_name, job.source_files)
    
    # 4. Save new PDFs to disk
    try:
        save_generated_pdfs(session, job.archive_id, job.piece_std_name, generated_pdfs)
    except Exception as e:
        # Rollback: attempt to restore the last backup if saving fails
        restore_last_backup(session, job.archive_id, job.piece_std_name)
        raise e

    # 5. Return result
    return True