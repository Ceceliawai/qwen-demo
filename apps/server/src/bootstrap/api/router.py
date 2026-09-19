from fastapi import APIRouter

from bootstrap.config.settings import get_settings
from modules.conversation.presentation.router import router as conversation_router

api_router = APIRouter()
api_router.include_router(conversation_router)


@api_router.get("/health", tags=["system"])
async def health_check() -> dict[str, str]:
    settings = get_settings()
    return {"status": "ok", "service": settings.app_name}
