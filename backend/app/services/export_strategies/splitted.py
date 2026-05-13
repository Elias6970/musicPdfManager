import io
import os
import zipfile
from concurrent.futures import ProcessPoolExecutor

import fitz

from sqlmodel import Session
from backend.app.loggers.default_logger import DefaultLogger
from backend.app.services.export_strategies.base_strategy import PresetExportStrategy
from backend.app.models.presets.resolution_preset import SolvedPreset
from backend.app.models.printers.jobs.preset_print_job import PresetPrintJobConfig
from backend.app.services.archive_services import get_archive_path
from backend.app.services.files_management.archive_file_manager import ArchiveFileManager
from backend.app.constants.constants import DIR_SCORES
from backend.app.utils.name_manager import NameManager
from backend.app.services.pdf_modifiers_service import (
    add_piece_number,
    add_blank_page,
    create_index,
    create_cover_page,
)

logger = DefaultLogger("SplittedExporter")


def _write_document(doc: fitz.Document) -> bytes:
    pdf_bytes = doc.write()
    doc.close()
    return pdf_bytes


def _process_outer_task(
    outer_key: str,
    inner_items: dict,
    archive_paths: dict,
    config: dict,
) -> tuple[str, list[tuple[str, bytes]], list[str]]:
    """Build one folder worth of split PDFs."""
    folder_entries: list[tuple[str, bytes]] = []
    logs: list[str] = []
    element_names: list[str] = []

    for i, (inner_key, item_dict) in enumerate(inner_items.items(), start=1):
        archive_id = item_dict["archive_id"]
        piece_std_name = item_dict["piece_std_name"]
        file_name = item_dict["file"]
        copies = item_dict.get("copies", 1)

        element_names.append(NameManager.get_name(inner_key))

        base_path = archive_paths.get(archive_id, "")
        folder_name = ArchiveFileManager.parse_name_to_file_manager(piece_std_name)
        file_path = os.path.join(base_path, folder_name, DIR_SCORES, file_name)

        if not os.path.exists(file_path):
            logs.append(f"File not found: {file_path}")
            continue

        try:
            with fitz.open(file_path) as inner_doc:
                if config.get("add_piece_number"):
                    add_piece_number(inner_doc, i)

                output_doc = fitz.open()
                for _ in range(copies):
                    output_doc.insert_pdf(inner_doc)

                file_stem = f"{outer_key}_{inner_key}"
                folder_entries.append((f"{file_stem}.pdf", _write_document(output_doc)))
        except Exception as exc:
            logs.append(f"Error processing {file_path}: {exc}")

    folder_entries.extend(_create_extra_documents(config, element_names))

    return outer_key, folder_entries, logs


def _create_extra_documents(config: dict, element_names: list[str]) -> list[tuple[str, bytes]]:
    extra_documents: list[tuple[str, bytes]] = []

    if config.get("add_index"):
        index_doc = create_index(
            elements=element_names,
            title=str(config.get("index_title") or "Índice"),
            subtitle=str(config.get("index_subtitle") or ""),
        )
        extra_documents.append(("index.pdf", _write_document(index_doc)))

    if config.get("add_blank_page_after_index"):
        blank_doc = fitz.open()
        add_blank_page(blank_doc)
        extra_documents.append(("blank_page.pdf", _write_document(blank_doc)))

    if config.get("add_cover_page"):
        cover_doc = create_cover_page(title=str(config.get("cover_title") or "Music Pdf Manager"))
        extra_documents.append(("cover.pdf", _write_document(cover_doc)))

    return extra_documents

class SplittedExporter(PresetExportStrategy):
    def export(self, session: Session, solved_preset: SolvedPreset, config: PresetPrintJobConfig) -> bytes:
        """
        Exports each outer key as a ZIP folder and each inner key as an individual PDF.
        Extra documents such as index, cover, and blank page are exported as separate PDFs.
        """
        logger.info(f"Starting split export with config: {config}")

        unique_archive_ids = set()
        for outer_dict in solved_preset.solution.values():
            for item in outer_dict.values():
                unique_archive_ids.add(item.archive_id)

        archive_paths = {
            archive_id: get_archive_path(session, archive_id)
            for archive_id in unique_archive_ids
        }

        config_dict = config.model_dump()
        futures = []

        #import multiprocessing as mp
        #mp_context = mp.get_context('spawn')
        #with ProcessPoolExecutor(max_workers=max(1, (os.cpu_count() or 2) - 1), mp_context=mp_context) as executor:
        with ProcessPoolExecutor(max_workers=max(1, (os.cpu_count() or 2) - 1)) as executor:
            for outer_key, inner_items in solved_preset.solution.items():
                inner_items_dict = {
                    key: value.model_dump() for key, value in inner_items.items()
                }
                futures.append(
                    executor.submit(
                        _process_outer_task,
                        outer_key,
                        inner_items_dict,
                        archive_paths,
                        config_dict,
                    )
                )

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
            for future in futures:
                outer_key, entries, logs = future.result()

                for log in logs:
                    logger.error(log)

                if entries:
                    zip_file.writestr(f"{outer_key}/", b"")

                for file_name, pdf_bytes in entries:
                    zip_file.writestr(f"{outer_key}/{file_name}", pdf_bytes)

        return zip_buffer.getvalue()
