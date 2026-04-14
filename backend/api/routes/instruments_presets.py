from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from backend.api.dependencies.database import get_session
from backend.api.dependencies.permissions import require_user
from backend.app.models.user import User
from backend.app.models.presets.instruments_preset import InstrumentsPreset
from backend.app.services.instruments_preset_service import (
    get_preset,
    get_all_presets,
    get_all_presets_names,
    add_preset,
    update_preset,
    delete_preset
)
from backend.app.error import (
    UserConfigNotFoundError,
    PresetNotFoundError,
    PresetAlreadyExistsError
)

router = APIRouter(prefix="/presets/instruments", tags=["instrument_presets"])

@router.get("", response_model=list[InstrumentsPreset])
def get_all_instrument_presets(
    session: Session = Depends(get_session),
    user: User = Depends(require_user)
):
    try:
        return get_all_presets(session=session, user_id=user.id) # type: ignore
    except UserConfigNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/names", response_model=list[str])
def get_all_instrument_preset_names(
    session: Session = Depends(get_session),
    user: User = Depends(require_user)
):
    try:
        return get_all_presets_names(session=session, user_id=user.id) # type: ignore
    except UserConfigNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/{preset_name}", response_model=InstrumentsPreset)
def get_instrument_preset(
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

@router.post("", response_model=InstrumentsPreset, status_code=status.HTTP_201_CREATED)
def create_instrument_preset(
    preset: InstrumentsPreset,
    session: Session = Depends(get_session),
    user: User = Depends(require_user)
):
    try:
        return add_preset(session=session, user_id=user.id, preset=preset) # type: ignore
    except UserConfigNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PresetAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.put("/{preset_name}", response_model=InstrumentsPreset)
def update_instrument_preset(
    preset_name: str,
    preset: InstrumentsPreset,
    session: Session = Depends(get_session),
    user: User = Depends(require_user)
):
    # Ensure the preset name in URL matches the preset payload
    if preset_name != preset.name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Preset name in URL must match the name in the payload"
        )
        
    try:
        return update_preset(session=session, user_id=user.id, preset=preset) # type: ignore
    except UserConfigNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PresetNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.delete("/{preset_name}", status_code=status.HTTP_204_NO_CONTENT)
def delete_instrument_preset(
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
