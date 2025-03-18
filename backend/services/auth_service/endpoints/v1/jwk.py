from fastapi import APIRouter
from starlette import status
from starlette.responses import Response

from services.auth_service.core.schemas.jwk import JWKRead
from services.auth_service.core.services.jwt_service import JWTService
from services.auth_service.core.settings import settings
jwk_router = APIRouter(prefix="/jwk", tags=["jwk"])


@jwk_router.get("")
async def get_public_jwk() -> Response:
    result = JWTService(jwt_settings=settings.jwt_settings).public_jwk
    return Response(
        status_code=status.HTTP_200_OK,
        headers={"Content-Type": "application/json"},
        content=JWKRead.model_validate(
            result.as_dict()
        ).model_dump_json()
    )
