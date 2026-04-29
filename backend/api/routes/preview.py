from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlmodel import Session
from backend.api.dependencies.database import get_session
from backend.api.dependencies.permissions import require_archive_viewer
from backend.app.models.preview import PreviewRequest
from backend.app.services.preview_services import generate_preview_bytes

router = APIRouter(prefix="/preview", tags=["Preview"])

@router.get("/")
def get_pdf_preview(
    request: PreviewRequest = Depends(),
    session: Session = Depends(get_session),
    _ = Depends(require_archive_viewer)
):
    """
    Generate and return a PNG preview of a specific PDF page.
    This endpoint utilizes HTTP caching so repeated requests return instantly on the client side.
    The total number of pages is returned in the 'X-Total-Pages' header.
    """
    try:
        img_bytes, total_pages = generate_preview_bytes(session=session, request=request)
    except FileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except IndexError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except (ValueError, RuntimeError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
    # Return cacheable HTTP response (Cache duration: 1 Week)
    return Response(
        content=img_bytes,
        media_type="image/png",
        headers={
            "Cache-Control": "public, max-age=604800",
            "Access-Control-Expose-Headers": "X-Total-Pages",
            "X-Archive-ID": str(request.archive_id),
            "X-Piece_Std-Name": request.piece_std_name,
            "X-File-Name": request.file,
            "X-Page-Number": str(request.page_number),
            "X-Total-Pages": str(total_pages),
            "X-DPI": str(request.dpi)
        }
    )
