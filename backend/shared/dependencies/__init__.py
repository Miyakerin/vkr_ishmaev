from authlib.jose import RSAKey, jwt
from fastapi import Depends, Security, HTTPException
from fastapi.security import APIKeyHeader
from starlette import status

from shared.db.s3 import S3Database
from shared.db.sql_database import Database
import typing as tp


class S3Dependency:
    def __init__(self, s3_params: list[dict[str, tp.Union[int, str, bool]]]):
        self.s3 = S3Database(s3_params=s3_params)

    async def __call__(self) -> S3Database:
        yield self.s3


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


class User:
    def __init__(self, user_id: int, is_admin: bool):
        self.user_id: int = user_id
        self.is_admin: bool = is_admin


class AuthDependency:
    token_header = APIKeyHeader(name="Authorization")

    def __init__(self, public_jwk: RSAKey):
        self.public_jwk = public_jwk
        print(self.public_jwk)
        pass

    async def __call__(self, token: str = Security(token_header)) -> User:
        if not token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        if "Bearer " in token:
            token = token.replace("Bearer ", "")

        claims = jwt.decode(token, key=self.public_jwk)
        return User(claims['user_id'], claims['is_admin'])
