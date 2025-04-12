import datetime
import random
import string
from email.mime.text import MIMEText
from typing import List, Optional, Union

import bcrypt
import sqlalchemy
from sqlalchemy import select, insert, update

from services.auth_service.core.db_models import User, UserCode
from services.auth_service.core.services import BaseService
from services.auth_service.core.settings import settings
import shared.dependencies as dep
import shared.exceptions as ex
import shared.db as db_
from shared.utils.email import send_email


class UserService(BaseService):

    max_attempts = 5

    def __init__(self, db: db_.Database = None, current_user: dep.User = None):
        super(UserService, self).__init__(db=db, current_user=current_user)

    async def create_user(self, username: str, email: str, password: str) -> User:
        username = username.strip().lower()
        email = email.strip().lower()
        password = password.strip()
        stmt = (
            select(User)
            .where(
                (User.username == username)
                | (User.email == email)
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

    async def patch_user(self, user_id: int, username: str = None, email: str = None, password: str = None, is_admin: bool = None) -> User:
        values = {}
        if username is not None:
            username = username.strip().lower()
            values["username"] = username
        if email is not None:
            email = email.strip().lower()
            values["email"] = email
        if password is not None:
            password = password.strip()
            password = bcrypt.hashpw(password.encode("UTF-8"), bcrypt.gensalt(12)).decode("UTF-8")
            values["password"] = password
        if is_admin is not None:
            values["is_admin"] = is_admin
        stmt = (
            update(User)
            .values(values)
            .where((User.user_id == user_id) & (User.delete_timestamp == None))
            .returning(User)
        )
        result = (await (await self.db.sessions)[settings.auth_db_settings.name].execute(stmt)).mappings().one_or_none()
        if not result:
            raise ex.CustomException(status_code=400, detail="Error while updating user")
        return result["User"]

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

    async def get_user_by_id(self, user_id: int) -> User:
        result = await self.get_users(user_ids=[user_id])
        if result:
            return result[0]
        raise ex.CustomException(status_code=400, detail="User does not exist")

    async def get_user_by_email(self, email: str) -> User:
        email = email.strip().lower()
        result = await self.get_users(email=email)
        if result:
            return result[0]
        raise ex.CustomException(status_code=400, detail="User does not exist")

    async def get_user_by_username(self, username: str) -> User:
        username = username.strip().lower()
        result = await self.get_users(username=username)
        if result:
            return result[0]
        raise ex.CustomException(status_code=400, detail="User does not exist")

    async def login_user(self, username: str, password: str, email: str) -> User:
        if username is None and email is None:
            raise ex.CustomException(status_code=400, detail="Username or email is required")
        username = username.strip().lower()
        password = password.strip()
        email = email.strip().lower()
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

    async def send_restore_code(self, username) -> None:
        user = await self.get_user_by_username(username)
        code_db, code_str = await self.generate_restore_code(user_id=user.user_id)
        html_attachment = f"""
            Ваш код восстановления пароля - {code_str}
        """
        html_attachment = MIMEText(html_attachment, "html")
        await send_email(
            from_addr=settings.email_settings.email,
            password=settings.email_settings.password,
            to=user.email, subject="Password Restore", attachments=[html_attachment],
            host=settings.email_settings.host, host_port=settings.email_settings.port
        )
        return None

    async def restore_password(self, username: str, code: str) -> None:
        current_user = await self.get_user_by_username(username=username)
        current_code = await self.get_current_restore_code(user_id=current_user.user_id)
        if not current_code:
            raise ex.CustomException(status_code=400, detail="Invalid code")
        if bcrypt.checkpw(code.encode("UTF-8"), current_code.code.encode("UTF-8")):
            new_password = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for _ in range(16))
            await self.patch_user(user_id=current_user.user_id, password=new_password)
            html_attachment = f"""
                        Ваш код восстановления пароля - {new_password}
                    """
            html_attachment = MIMEText(html_attachment, "html")
            await send_email(
                from_addr=settings.email_settings.email,
                password=settings.email_settings.password,
                to=current_user.email, subject="Password Restore", attachments=[html_attachment],
                host=settings.email_settings.host, host_port=settings.email_settings.port
            )
            await self.delete_restore_codes(user_id=current_user.user_id)
        else:
            delete_timestamp = None if current_code.attempt_number + 1 > 5 else None
            attempt_number = current_code.attempt_number + 1
            stmt = (
                update(UserCode)
                .values(attempt_number=attempt_number, delete_timestamp=delete_timestamp)
                .where(UserCode.user_code_id == current_code.user_code_id)
            )
            await (await self.db.sessions)[settings.auth_db_settings.name].execute(stmt)
            await (await self.db.sessions)[settings.auth_db_settings.name].commit()
            raise ex.CustomException(status_code=400, detail="Invalid code")
        return None

    async def get_current_restore_code(self, user_id: int) -> Optional[UserCode]:
        stmt = (
            select(UserCode)
            .where(
                (UserCode.user_id == user_id)
                & (UserCode.attempt_number < self.max_attempts)
                & (UserCode.delete_timestamp == None)
                & (UserCode.create_timestamp + datetime.timedelta(minutes=30) > datetime.datetime.now())
            )
        )
        results = await (await self.db.sessions)[settings.auth_db_settings.name].execute(stmt)
        results = results.mappings().all()
        if not results:
            return None
        return results[0]["UserCode"]

    async def delete_restore_codes(self, user_id: int) -> None:
        stmt = (
            update(UserCode)
            .values(delete_timestamp=datetime.datetime.now())
            .where(
                (UserCode.user_id == user_id)
                & (UserCode.delete_timestamp == None)
            )
        )
        await (await self.db.sessions)[settings.auth_db_settings.name].execute(stmt)
        return None

    async def generate_restore_code(self, user_id) -> tuple[UserCode, str]:
        await self.delete_restore_codes(user_id=user_id)
        code = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(8))
        stmt = (
            insert(UserCode)
            .values(
                user_id=user_id,
                attempt_number=0,
                create_timestamp=datetime.datetime.now(),
                delete_timestamp=None,
                code=bcrypt.hashpw(code.encode("UTF-8"), bcrypt.gensalt(12)).decode("UTF-8")
            )
            .returning(UserCode)
        )
        result = await (await self.db.sessions)[settings.auth_db_settings.name].execute(stmt)
        result = result.mappings().one_or_none()
        if not result:
            raise ex.CustomException(status_code=404, detail="User does not exist")
        return result["UserCode"], code
