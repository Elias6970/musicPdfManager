from fastapi import FastAPI

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

    return app

app = create_app()
