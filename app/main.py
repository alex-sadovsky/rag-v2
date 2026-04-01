from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.routers import router

_STATIC_DIR = Path(__file__).parent / "static"


def create_app() -> FastAPI:
    application = FastAPI(
        title=settings.app_title,
        version=settings.app_version,
        description=settings.app_description,
    )
    application.include_router(router)
    application.mount("/static", StaticFiles(directory=_STATIC_DIR), name="static")

    @application.get("/visualize", include_in_schema=False)
    async def visualize():
        return FileResponse(_STATIC_DIR / "visualize.html")

    return application


app = create_app()
