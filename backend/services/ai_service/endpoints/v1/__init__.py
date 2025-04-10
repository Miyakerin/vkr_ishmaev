from fastapi import APIRouter

from services.ai_service.endpoints.v1.chats import chat_router
from services.ai_service.endpoints.v1.files import file_router
from services.ai_service.endpoints.v1.models import models_router
from services.ai_service.endpoints.v1.tokens import token_router

v1_router = APIRouter(prefix="/v1")

v1_router.include_router(chat_router)
v1_router.include_router(file_router)
v1_router.include_router(models_router)
v1_router.include_router(token_router)
