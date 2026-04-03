from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from backend.api.dependencies.database import get_session
from backend.api.dependencies.permissions import require_user
from backend.app.models.user import User
from backend.app.models.presets.pieces_preset import PiecesPreset
from backend.app.services.pieces_preset_service import (
    get_preset,
    get_all_presets,
    get_all_preset_names,
    add_preset,
    update_preset,
    delete_preset
)
from backend.app.error import (
    UserConfigNotFoundError,
    PresetNotFoundError,
    PresetAlreadyExistsError
)

router = APIRouter(prefix="/presets/pieces", tags=["pieces_presets"])

@router.get("", response_model=list[PiecesPreset])
def get_all_pieces_presets(
    session: Session = Depends(get_session),
    user: User = Depends(require_user)
):
    try:
        return get_all_presets(session=session, user_id=user.id) # type: ignore
    except UserConfigNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/names", response_model=list[str])
def get_all_pieces_preset_names(
    session: Session = Depends(get_session),
    user: User = Depends(require_user)
):
    try:
        return get_all_preset_names(session=session, user_id=user.id) # type: ignore
    except UserConfigNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/{preset_name}", response_model=PiecesPreset)
def get_pieces_preset(
    preset_name: str,
    session: Session = Depends(get_session),
    user: User = Depends(require_user)
):
    try:
        return get_preset(session=session, user_id=user.id, preset_name=preset_name) # type: ignore
    except UserConfigNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PresetNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.post("", response_model=PiecesPreset, status_code=status.HTTP_201_CREATED)
def create_pieces_preset(
    preset: PiecesPreset,
    session: Session = Depends(get_session),
    user: User = Depends(require_user)
):
    try:
        return add_preset(session=session, user_id=user.id, preset=preset) # type: ignore
    except UserConfigNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PresetAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

@router.put("", response_model=PiecesPreset)
def update_pieces_preset(
    preset: PiecesPreset,
    session: Session = Depends(get_session),
    user: User = Depends(require_user)
):
    try:
        return update_preset(session=session, user_id=user.id, preset=preset) # type: ignore
    except UserConfigNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PresetNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.delete("/{preset_name}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pieces_preset(
    preset_name: str,
    session: Session = Depends(get_session),
    user: User = Depends(require_user)
):
    try:
        delete_preset(session=session, user_id=user.id, preset_name=preset_name) # type: ignore
    except UserConfigNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PresetNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
