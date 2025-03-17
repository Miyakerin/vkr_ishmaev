from typing import List

import bcrypt
import sqlalchemy
from sqlalchemy import select, insert

from services.auth_service.core.db_models import User
from services.auth_service.core.services import BaseService
from services.auth_service.core.settings import settings
from shared.db.sql_database import Database
from shared.exceptions.exceptions import CustomException


class UserService(BaseService):
    def __init__(self, db:Database=None, current_user=None):
        super(UserService, self).__init__(db=db, current_user=current_user)

    async def create_user(self, username: str, email: str, password: str) -> User:
        stmt = (
            select(User)
            .where(
                (sqlalchemy.func.lower(User.username) == username.lower())
                | (sqlalchemy.func.lower(User.email) == email.lower())
            )
        )
        result = await (await self.db.sessions)[settings.auth_db_settings.name].execute(stmt)
        result = [x["User"] for x in result.mappings().all()]
        if result:
            raise CustomException(status_code=400, detail="User w/ email or login already exists")

        stmt = (
            insert(User)
            .values(
                username=username,
                email=email,
                password=bcrypt.hashpw(password.encode("UTF-8"), bcrypt.gensalt(12)).decode("UTF-8")
            )
            .returning(User)
        )
        result = await (await self.db.sessions)[settings.auth_db_settings.name].execute(stmt)
        result = result.mappings().one_or_none()
        if result:
            return result["User"]
        raise CustomException(status_code=400, detail="Error while creating user")

    async def get_users(
            self,
            username: str = None,
            email: str = None,
            existing: bool = True,
    ) -> List[User]:
        stmt = select(User)
        if username:
            stmt = stmt.where(sqlalchemy.func.lower(User.username) == username.lower())
        if email:
            stmt = stmt.where(sqlalchemy.func.lower(User.email) == email.lower())
        if existing is True:
            stmt = stmt.where(User.delete_timestamp == None)
        elif existing is False:
            stmt = stmt.where(User.delete_timestamp != None)

        result = await (await self.db.sessions)[settings.auth_db_settings.name].execute(stmt)
        result = [x["User"] for x in result.mappings().all()]
        return result

    async def login_user(self, username: str, password: str, email: str) -> User:
        if username:
            stmt = (
                select(User)
                .where(
                    (sqlalchemy.func.lower(User.username) == username.lower())
                )
            )
        elif email:
            stmt = (
                select(User)
                .where(
                    sqlalchemy.func.lower(User.email) == email.lower()
                )
            )
        else:
            raise CustomException(status_code=400, detail="Invalid credentials")
        result = await (await self.db.sessions)[settings.auth_db_settings.name].execute(stmt)
        result = result.mappings().one_or_none()
        if not result:
            raise CustomException(status_code=404, detail="User does not exist")
        result = result["User"]
        if bcrypt.checkpw(password.encode("UTF-8"), result.password.encode("UTF-8")):
            return result
        raise CustomException(status_code=401, detail="Invalid credentials")
