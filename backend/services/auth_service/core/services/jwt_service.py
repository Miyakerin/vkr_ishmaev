from authlib.jose import JsonWebKey, RSAKey

from services.auth_service.core.services import BaseService
from services.auth_service.core.settings import JwtSettings


class JWTService(BaseService):
    def __init__(self,jwt_settings, session=None, current_user=None):
        super(JWTService, self).__init__(session=session, current_user=current_user)
        self.__jwt_settings: JwtSettings = jwt_settings

    @property
    def jwt_settings(self) -> JwtSettings:
        return self.__jwt_settings

    @property
    async def public_jwk(self) -> RSAKey:
        return self.__jwt_settings.public_key

    @property
    async def private_jwk(self) -> RSAKey:
        return self.__jwt_settings.private_key


