from fastapi import APIRouter

from app.routers.health import router as health_router
from app.routers.query import router as query_router
from app.routers.resume_analytics import router as resume_analytics_router
from app.routers.upload import router as upload_router
from app.routers.vectors import router as vectors_router

router = APIRouter()

router.include_router(health_router)
router.include_router(upload_router)
router.include_router(query_router)
router.include_router(vectors_router)
router.include_router(resume_analytics_router)
