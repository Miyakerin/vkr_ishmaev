from authlib.jose import RSAKey, jwt
from fastapi import Depends, Security, HTTPException
from fastapi.security import APIKeyHeader
from starlette import status

from shared.db.sql_database import Database
import typing as tp


class DbDependency:
    def __init__(self, engines_params: list[dict[str, tp.Union[int, str, bool]]]):
        self.db = Database(engines_params)

    async def __call__(self) -> Database:

        try:
            yield self.db
            to_commit = []
            for db_name, session in (await self.db.sessions).items():
                await session.commit()
            #     to_commit.append(session.commit())
            # if to_commit:
            #     await asyncio.gather(*to_commit)
        except Exception as e:
            to_rollback = []
            for db_name, session in (await self.db.sessions).items():
                await session.rollback()
            #     to_rollback.append(session.rollback())
            # if to_rollback:
            #     await asyncio.gather(*to_rollback)
            raise e
        finally:
            to_close = []
            for db_name, session in (await self.db.sessions).items():
                await session.close()
            #     to_close.append(session.close())
            # if to_close:
            #     await asyncio.gather(*to_close)


class AuthDependency:
    token_header = APIKeyHeader(name="Authorization")

    def __init__(self, public_jwk: RSAKey):
        self.public_jwk = public_jwk
        pass

    async def __call__(self, token: str = Security(token_header)):
        if not token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        claims = jwt.decode(token, key=self.public_jwk)
        return claims
        pass
