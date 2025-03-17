from fastapi import APIRouter
from services.auth_service.endpoints.v1.jwk import jwk_router
v1_router = APIRouter(prefix="/v1")

v1_router.include_router(jwk_router)
