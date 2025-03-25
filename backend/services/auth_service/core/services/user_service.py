from typing import List, Optional, Union

import bcrypt
import sqlalchemy
from sqlalchemy import select, insert

from services.auth_service.core.db_models import User
from services.auth_service.core.services import BaseService
from services.auth_service.core.settings import settings
import shared.dependencies as dep
import shared.exceptions as ex
import shared.db as db_


class UserService(BaseService):
    def __init__(self, db: db_.Database = None, current_user: dep.User = None):
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
            raise ex.CustomException(status_code=400, detail="User w/ email or login already exists")

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
        raise ex.CustomException(status_code=400, detail="Error while creating user")

    async def get_users(
            self,
            username: Optional[str] = None,
            email: Optional[str] = None,
            existing: Optional[bool] = True,
            user_ids: Optional[Union[List[int], int]] = None
    ) -> List[User]:
        stmt = select(User)
        if user_ids:
            if isinstance(user_ids, int):
                user_ids = [user_ids]
            user_ids = tuple(user_ids)
            stmt = stmt.where(User.user_id.in_(user_ids))
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
        if username is None and email is None:
            raise ex.CustomException(status_code=400, detail="Username or email is required")
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
            raise ex.CustomException(status_code=400, detail="Invalid credentials")
        result = await (await self.db.sessions)[settings.auth_db_settings.name].execute(stmt)
        result = result.mappings().one_or_none()
        if not result:
            raise ex.CustomException(status_code=404, detail="User does not exist")
        result = result["User"]
        if bcrypt.checkpw(password.encode("UTF-8"), result.password.encode("UTF-8")):
            return result
        raise ex.CustomException(status_code=401, detail="Invalid credentials")
