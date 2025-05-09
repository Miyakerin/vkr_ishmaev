from services.auth_service.core.schemas import BaseDTO


class JWKRead(BaseDTO):
    n: str
    e: str
    kty: str
    kid: str


class JWTToken(BaseDTO):
    access_token: str
