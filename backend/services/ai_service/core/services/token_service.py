from typing import Optional

from sqlalchemy import select, insert, update
from sqlalchemy.sql.functions import current_user

from services.ai_service.core.db_models import UserBalance
from services.ai_service.core.services import BaseService
from services.ai_service.core.settings import settings
from shared.db import Database
from shared.db.s3 import S3Database
from shared.dependencies import User
from shared.exceptions import CustomException


class TokenService(BaseService):

    def __init__(self, db: Database = None, current_user: User = None, s3: S3Database = None):
        super(TokenService, self).__init__(db=db, current_user=current_user, s3=s3)

    async def get_amount(self) -> int:
        result = await self.get_user_balance()
        if not result:
            return 0
        return result.balance

    async def get_user_balance(self) -> Optional[UserBalance]:
        stmt = (
            select(UserBalance)
            .where(
                (UserBalance.user_id == self.current_user.user_id)
                & (UserBalance.delete_timestamp == None)
            )
        )
        result = (await (await self.db.sessions)[settings.ai_db_settings.name].execute(stmt)).mappings().one_or_none()
        if not result:
            return None
        return result["UserBalance"]

    async def create_user_balance(self, amount: int) -> UserBalance:
        stmt = (
            insert(UserBalance)
            .values(
                user_id=self.current_user.user_id,
                balance=amount,
            )
            .returning(UserBalance)
        )
        result = (await (await self.db.sessions)[settings.ai_db_settings.name].execute(stmt)).mappings().one_or_none()
        if not result:
            raise CustomException(status_code=500, detail="error while creating user balance")
        return result["UserBalance"]

    async def add_n_tokens(self, n_tokens: int) -> UserBalance:
        if n_tokens < 0:
            raise CustomException(status_code=500, detail="invalid n_tokens")
        user_balance = await self.get_user_balance()
        if not user_balance:
            return await self.create_user_balance(n_tokens)
        stmt = (
            update(UserBalance)
            .values(balance=n_tokens + user_balance.balance)
            .where(
                (UserBalance.user_id == self.current_user.user_id)
                & (UserBalance.delete_timestamp == None)
            )
            .returning(UserBalance)
        )
        result = (await (await self.db.sessions)[settings.ai_db_settings.name].execute(stmt)).mappings().one_or_none()
        if not result:
            raise CustomException(status_code=500, detail="error while creating user balance")
        return result["UserBalance"]

    async def remove_n_tokens(self, n_tokens: int):
        if n_tokens < 0:
            raise CustomException(status_code=500, detail="invalid n_tokens")
        user_balance = await self.get_user_balance()
        if not user_balance:
            return await self.create_user_balance(n_tokens)
        stmt = (
            update(UserBalance)
            .where(
                (UserBalance.user_id == self.current_user.user_id)
                & (UserBalance.delete_timestamp == None)
            )
            .values(balance=user_balance.balance - n_tokens)
            .returning(UserBalance)
        )
        result = (await (await self.db.sessions)[settings.ai_db_settings.name].execute(stmt)).mappings().one_or_none()
        if not result:
            raise CustomException(status_code=500, detail="error while creating user balance")
        return result["UserBalance"]

