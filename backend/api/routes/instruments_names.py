from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
import json
from backend.app.instruments_names_manager import InstrumentsNamesManager
from backend.api.dependencies.database import get_session
from backend.api.dependencies.permissions import require_user

router = APIRouter(prefix="/instruments_names", tags=["Instruments Names"])

@router.get("/shortcuts_and_instruments", status_code=status.HTTP_200_OK, response_model=dict[str,str])
def get_shortcuts_and_instruments(_: None = Depends(require_user)):
    try:
        return InstrumentsNamesManager.get_shortcuts_and_instruments()
    except (FileNotFoundError, json.JSONDecodeError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/instruments_and_shortcuts", status_code=status.HTTP_200_OK, response_model=dict[str,str])
def get_instruments_and_shortcuts(_: None = Depends(require_user)):
    try:
        return InstrumentsNamesManager.get_instruments_and_shortcuts()
    except (FileNotFoundError, json.JSONDecodeError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/instruments_and_shortcuts/{language_cod}", status_code=status.HTTP_200_OK, response_model=list[tuple[str,str]])
def get_instruments_and_shortcuts_translated(language_cod: str, _: None = Depends(require_user)):
    try:
        return InstrumentsNamesManager.get_instruments_and_shortcuts_translated(language_cod)
    except KeyError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Language code '{language_cod}' not found in translations.")
    except (FileNotFoundError, json.JSONDecodeError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
