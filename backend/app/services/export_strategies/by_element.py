import io
import os
import zipfile
import fitz
from concurrent.futures import ProcessPoolExecutor

from sqlmodel import Session
from backend.app.loggers.default_logger import DefaultLogger
from backend.app.services.export_strategies.base_strategy import PresetExportStrategy
from backend.app.models.presets.resolution_preset import SolvedPreset
from backend.app.models.printers.jobs.preset_print_job import PresetPrintJobConfig
from backend.app.services.archive_services import get_archive_path
from backend.app.files_management.archive_file_manager import ArchiveFileManager
from backend.app.constants.constants import DIR_SCORES
from backend.app.utils.name_manager import NameManager
from backend.app.services.pdf_modifiers_service import (
    add_piece_number,
    add_index_page,
    add_blank_page,
    add_cover_page
)

logger = DefaultLogger("ByElementExporter")


def _process_element_task(
    element_name: str,
    inner_items: dict,
    archive_paths: dict,
    config: dict
) -> tuple[str, bytes, list[str]]:
    """Worker function to process a single element's PDF and apply decorators."""
    doc = fitz.open()
    elements_list = []
    logs = []
    
    # 1. Merge all inner items (files)
    for i, (inner_key, item_dict) in enumerate(inner_items.items(), start=1):
        archive_id = item_dict["archive_id"]
        piece_std_name = item_dict["piece_std_name"]
        file_name = item_dict["file"]
        copies = item_dict.get("copies", 1) # Ignore preset copies is applied in preprocessing
        
        elements_list.append(NameManager.get_name(inner_key)) # get_name to remove the internal code if it is a piece. If not it stays the same
        
        base_path = archive_paths.get(archive_id, "")
        folder_name = ArchiveFileManager.parse_name_to_file_manager(piece_std_name)
        file_path = os.path.join(base_path, folder_name, DIR_SCORES, file_name)
        
        if not os.path.exists(file_path):
            logs.append(f"File not found: {file_path}")
            continue
        
        try:
            inner_doc = fitz.open(file_path)
            if config.get("add_piece_number"):
                add_piece_number(inner_doc, i)
            
            for _ in range(copies):
                doc.insert_pdf(inner_doc)
        except Exception as e:
            logs.append( f"Error processing {file_path}: {e}")

    # 2. Apply decorators independently to the merged document
    if len(doc) > 0: # The order is inverted because the inserting is done in the first page    
        # Index
        if config.get("add_blank_page_after_index"): # It is independient from add_index to give the user the option to add a blank page
            add_blank_page(doc)

        if config.get("add_index"):
            add_index_page(doc, elements=elements_list, title=config.get("index_title"), subtitle=config.get("index_subtitle"))

        # Cover page
        if config.get("add_cover_page"):
            add_cover_page(doc, title=config.get("cover_title"))
        
        pdf_bytes = doc.write()
        doc.close()
        return (element_name, pdf_bytes, logs)
        
    doc.close()
    return (element_name, b"", logs)


class ByElementExporter(PresetExportStrategy):
    def export(self, session: Session, solved_preset: SolvedPreset, config: PresetPrintJobConfig) -> bytes:
        """
        Iterates outer keys, merges inner keys per element into separate documents.
        Applies decorators independently to each generated element document.
        Zips all the PDFs and returns ZIP bytes.
        """
        logger.info(f"Starting export by element with config: {config}")
        
        # Fetch base paths for all used archives
        # It should be only one archive per job but we are prepared to handle multiple archives
        unique_archive_ids = set()
        for outer_dict in solved_preset.solution.values():
            for item in outer_dict.values():
                unique_archive_ids.add(item.archive_id)
        
        archive_paths = {
            arch_id: get_archive_path(session, arch_id)
            for arch_id in unique_archive_ids
        }
        
        config_dict = config.model_dump()
        
        # Prepare parallel jobs
        futures = []
        with ProcessPoolExecutor(max_workers=max(1, (os.cpu_count() or 2) - 1)) as executor:
            for element_name, inner_items in solved_preset.solution.items():
                inner_items_dict = {
                    k: v.model_dump() for k, v in inner_items.items()
                }
                futures.append(
                    executor.submit(
                        _process_element_task,
                        element_name,
                        inner_items_dict,
                        archive_paths,
                        config_dict
                    )
                )
                
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
            for future in futures:
                element_name, pdf_bytes, logs = future.result()

                map(lambda log: logger.error(log), logs) #Print logs in the main process to avoid concurrency issues with the logger
                        
                if pdf_bytes:
                    zip_file.writestr(f"{element_name}.pdf", pdf_bytes)
                    
        return zip_buffer.getvalue()
