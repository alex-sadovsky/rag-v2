from fastapi import APIRouter

from app.routers.health import router as health_router
from app.routers.upload import router as upload_router
from app.routers.vectors import router as vectors_router

router = APIRouter()

router.include_router(health_router)
router.include_router(upload_router)
router.include_router(vectors_router)
