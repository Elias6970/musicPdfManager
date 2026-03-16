from fastapi import FastAPI
import app.settings as settings
from api.dependencies.permissions import RequireArchiveRoleFastAPI, RequireRoleFastAPI

require_admin = RequireRoleFastAPI(allowed_roles=["admin"])

def create_app() -> FastAPI:
    app = FastAPI(
        title="musicPdfManager API",
        description="FastAPI backend for musicPdfManager",
        version="1.0.0"
    )

    # Attach our external routing here
    #app.include_router(users.router, prefix="/api/v1/users", tags=["users"])

    @app.get("/health")
    def health_check():
        return {"status": "ok"}

    @app.get("/is_authenticated")
    def is_authenticated(iss=require_admin):
        return {"authenticated": True}

    return app

settings.get_server_settings()
app = create_app()
