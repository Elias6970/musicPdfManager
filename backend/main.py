from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter
from sqlmodel import SQLModel

# Import the models module to register all SQLModel schemas
import backend.app.models

import backend.app.settings as settings
from backend.api.dependencies.database import engine, insert_default_roles, insert_root_user
from backend.api.routes import archives, instruments_presets, pieces_presets, pieces, users, uploads, printers, preview, classification, instruments_names, roles
from backend.app.services.upload_services import cleanup_temp_uploads_routine
import asyncio

@asynccontextmanager
async def lifespan(app: FastAPI):
    # This runs when the server starts
    SQLModel.metadata.create_all(engine)
    insert_default_roles()
    insert_root_user()
    
    # Start the background task for cleaning up temporary uploads
    cleanup_task = asyncio.create_task(cleanup_temp_uploads_routine())
    
    yield
    # This runs when the server stops
    cleanup_task.cancel()


def create_app() -> FastAPI:
    app = FastAPI(
        title="musicPdfManager API",
        description="FastAPI backend for musicPdfManager",
        version="1.0.0",
        lifespan=lifespan
    )
    router = APIRouter(prefix="/api/v1")
    router.include_router(users.router)
    router.include_router(roles.router)
    router.include_router(archives.router)
    router.include_router(pieces.router)
    router.include_router(uploads.router)
    router.include_router(printers.router)
    router.include_router(instruments_presets.router)
    router.include_router(pieces_presets.router)
    router.include_router(preview.router)
    router.include_router(classification.router)
    router.include_router(instruments_names.router)
    
    app.include_router(router)
    return app

settings.save_server_settings(settings.get_server_settings()) # Ensure settings file exists with defaults
app = create_app()
