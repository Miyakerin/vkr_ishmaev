from fastapi import Security

from services.ai_service.core.settings import settings
from shared.dependencies import AuthDependency


class CustomAuthDependency:
    def __init__(self):
        pass

    async def __call__(self, token: str = Security(AuthDependency.token_header)):
        return await AuthDependency(public_jwk=settings.auth_key)(token=token)
