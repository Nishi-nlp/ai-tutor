from fastapi import APIRouter

from app.api.health import router as health_router
from app.api.knowledge_components import router as knowledge_components_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(knowledge_components_router)
