from contextlib import asynccontextmanager

from fastapi import FastAPI, APIRouter
from sqlmodel import SQLModel

# Import the models module to register all SQLModel schemas
import backend.app.models

import backend.app.settings as settings
from backend.api.dependencies.database import engine, insert_default_roles
from backend.api.routes import archives, pieces, users

@asynccontextmanager
async def lifespan(app: FastAPI):
    # This runs when the server starts
    SQLModel.metadata.create_all(engine)
    insert_default_roles()
    yield
    # This runs when the server stops


def create_app() -> FastAPI:
    app = FastAPI(
        title="musicPdfManager API",
        description="FastAPI backend for musicPdfManager",
        version="1.0.0",
        lifespan=lifespan
    )
    router = APIRouter(prefix="/api/v1")
    router.include_router(users.router)
    router.include_router(archives.router)
    router.include_router(pieces.router)

    app.include_router(router)
    return app

settings.get_server_settings()
app = create_app()
