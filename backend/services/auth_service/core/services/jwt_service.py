import datetime

from authlib.jose import RSAKey, jwt

from services.auth_service.core.services import BaseService
from services.auth_service.core.settings import JwtSettings
from shared.db.sql_database import Database


class JWTService(BaseService):
    exp_timedelta = datetime.timedelta(days=30)

    def __init__(self,jwt_settings, db:Database=None, current_user=None):
        super(JWTService, self).__init__(db=db, current_user=current_user)
        self.__jwt_settings: JwtSettings = jwt_settings

    @property
    def jwt_settings(self) -> JwtSettings:
        return self.__jwt_settings

    @property
    def public_jwk(self) -> RSAKey:
        return self.__jwt_settings.public_key

    @property
    async def private_jwk(self) -> RSAKey:
        return self.__jwt_settings.private_key

    async def generate_jwt(self, user_id: int, is_admin: bool = False):
        header = {"alg": "RS256", "exp": int((datetime.datetime.now() + self.exp_timedelta).timestamp())}
        payload = {"user_id": user_id, "is_admin": is_admin}
        result = jwt.encode(header, payload, await self.private_jwk)
        return result
