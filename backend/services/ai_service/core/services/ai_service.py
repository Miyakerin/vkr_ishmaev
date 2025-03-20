from typing import List, Union, Optional

from sqlalchemy import insert

from services.ai_service.core.db_models import Chat
from services.ai_service.core.schemas.chat_dto import ChatCreateUpdate, MessageDataRead, MessageDataCreateUpdate
from services.ai_service.core.services import BaseService
from services.ai_service.core.settings import settings
from shared.db.sql_database import Database
from shared.dependencies import User
from shared.exceptions.exceptions import CustomException


class AIService(BaseService):

    available_models = {
        "gigachat": [],
        "openai": [],
        "deepseek": []
    }

    def __init__(self, db: Database = None, current_user: User = None):
        super(AIService, self).__init__(db=db, current_user=current_user)

    async def create_chat(self, value: ChatCreateUpdate):
        result = await self.create_chats(values=[value])
        if not result:
            raise CustomException(status_code=500, detail="Failed to create chat")
        return result[0]

    async def create_chats(self, values: List[ChatCreateUpdate]):
        if not values:
            raise CustomException(status_code=400, detail="provided empty values for chats")
        values_ = []
        for value in values:
            values_.append(
                {
                    "user_id": self.current_user.user_id
                }
            )
        stmt = (
            insert(Chat)
            .values(values_)
            .returning(Chat)
        )
        result = [x["Chat"] for x in (await (await self.db.sessions)[settings.ai_db_settings.name].execute(stmt)).mappings().all()]
        return result

    async def get_chats(
            self,
            user_ids: Optional[Union[List[int], int]] = None,
            chat_ids: Optional[Union[List[int], int]] = None,

    ):
        pass

    async def create_new_message(self, chat_id: int, value: MessageDataCreateUpdate):

        pass
