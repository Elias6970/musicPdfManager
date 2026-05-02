
from fastapi import APIRouter, Depends
from sqlmodel import Session
from backend.api.dependencies.database import get_session
from backend.api.dependencies.auth import get_current_user
from backend.api.dependencies.file_manager import get_archive_file_manager
from backend.api.dependencies.permissions import RequireArchiveRoleFastAPI, ArchiveRole
from backend.app.files_management.archive_file_manager import ArchiveFileManager
from backend.app.massive_import.massive_importer_services import massive_import
router = APIRouter(prefix="/massive_import", tags=["massive_import"])

@router.post("/", response_model=dict)
def make_import(
    archive_id: int,
    excel_name_path: str,
    archive_name_path: str,
    session: Session = Depends(get_session),
    file_manager: ArchiveFileManager = Depends(get_archive_file_manager),
    ignore_first_excel_row: bool = True,
    _ = Depends(RequireArchiveRoleFastAPI([ArchiveRole.OWNER, ArchiveRole.EDITOR]))
):
    full_added_pieces, pieces_without_files, not_added_pieces =massive_import(
        archive_id=archive_id,
        excel_name_path=excel_name_path,
        archive_name_path=archive_name_path,
        session=session,
        file_manager=file_manager,
        ignore_first_excel_row=ignore_first_excel_row
    )
    return {
        "message": "Massive import completed successfully.",
        "full_added_pieces": [i.std_name for i in full_added_pieces],
        "pieces_without_files": [i.std_name for i in pieces_without_files],
        "not_added_pieces": [{ "std_name": std_name, "error": error } for std_name, error in not_added_pieces]
    }