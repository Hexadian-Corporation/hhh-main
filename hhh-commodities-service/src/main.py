import uvicorn
from fastapi import FastAPI

from src.infrastructure.config.settings import Settings


def create_app() -> FastAPI:
    settings = Settings()

    app = FastAPI(title=settings.app_name)

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok", "service": settings.app_name}

    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8007, reload=True)
