from typing import List, Union, Optional

from sqlalchemy import insert, select, update

from services.ai_service.core.db_models import Chat, Message, MessageData, MessageDataXFile, File
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

    default_system_prompts = {
        "ru": "Ты чат-бот помощник, который все силы прилагает, чтобы решить вопрос пользователя",
        "en": "You are chat-bot helper, who do everything you can for solving user problems"
    }

    available_languages = ["ru", "en"]

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
            value.language = value.language.strip().lower()
            if value.language not in self.available_languages:
                raise CustomException(status_code=402, detail="Unavailable language")
            values_.append(
                {
                    "language": value.language,
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
            existing: Optional[bool] = True,

    ) -> List[Chat]:
        stmt = select(Chat)
        if user_ids is not None:
            if isinstance(user_ids, int):
                user_ids = [user_ids]
            stmt = stmt.where(Chat.user_id.in_(user_ids))
        if chat_ids is not None:
            if isinstance(chat_ids, int):
                chat_ids = [chat_ids]
            stmt = stmt.where(Chat.chat_id.in_(chat_ids))
        if existing is True:
            stmt = stmt.where(Chat.delete_timestamp != None)
        elif existing is False:
            stmt = stmt.where(Chat.delete_timestamp == None)
        result = [x["Chat"] for x in (await (await self.db.sessions)[settings.ai_db_settings.name].execute(stmt)).mappings().all()]
        return result

    async def get_chat(self, chat_id: int):
        result = await self.get_chats(chat_ids=chat_id)
        if not result:
            raise CustomException(status_code=404, detail="Chat not found")
        result = result[0]
        if self.current_user.is_admin:
            return result
        if self.current_user.user_id != result.user_id:
            raise CustomException(status_code=403, detail="You are not admin and not allowed to access this chat")
        return result

    async def get_chat_history(self, chat_id: int, bypass: bool = False):
        if not bypass:
            current_chat = await self.get_chat(chat_id=chat_id)

        query = f"""
            SELECT JSON_BUILD_OBJECT(
                'chat_data', JSON_BUILD_OBJECT(
                    'chat_id', chat.chat_id,
                    'user_id', chat.user_id,
                    'language', chat.language,
                    'create_timestamp', chat.create_timestamp
                ),
                'messages', json_agg_strict(message.data)
            ) as data
            FROM {Chat.__tablename__} as chat
            
            LEFT JOIN (
                SELECT message.chat_id,
                JSON_BUILD_OBJECT(
                    'message_id', message.message_id,
                    'company_name', message.company_name,
                    'sender', message.sender,
                    'create_timestamp', message.create_timestamp,
                    'message_data', json_agg_strict(message_data.data)
                ) as data
                FROM {Message.__tablename__} as message
                
                INNER JOIN (
                    SELECT message_data.message_id,
                    JSON_BUILD_OBJECT(
                        'message_data_id', message_data.message_data_id,
                        'text', message_data.text,
                        'is_main', message_data.is_main,
                        'create_timestamp', message_data.create_timestamp,
                        'attachments', json_agg_strict(attachment.data)
                    ) as data
                    FROM {MessageData.__tablename__} as message_data
                    
                    LEFT JOIN (
                        SELECT attachment.message_data_id,
                        JSON_BUILD_OBJECT(
                            'message_data_x_file_id', attachment.message_data_x_file_id,
                            'file_id', attachment.file_id,
                            'create_timestamp', attachment.create_timestamp,
                            'filename', file.filename,
                            's3_key', file.s3_key,
                            'bucket_name', file.bucket_name,
                            'file_create_timestamp', file.create_timestamp
                        ) as data
                        FROM {MessageDataXFile.__tablename__} as attachment
                        
                        INNER JOIN {File.__tablename__} as file
                            ON file.file_id = attachment.file_id AND file.delete_timestamp IS NULL
                        WHERE attachment.delete_timestamp IS NULL
                    ) as attachment
                        ON attachment.message_data_id = message_data.message_data_id
                    
                    WHERE message_data.delete_timestamp IS NULL
                    GROUP BY message_data.message_data_id, message_data.text, message_data.is_main, message_data.create_timestamp
                ) as message_data
                    ON message_data.message_id = message.message_id
                    
                WHERE message.delete_timestamp IS NULL
                GROUP BY message.message_id, message.company_name, message.sender, message.create_timestamp
            ) as message
                ON message.chat_id = chat.chat_id
            WHERE chat.chat_id = :chat_id AND chat.delete_timestamp IS NULL
            GROUP BY chat.chat_id, chat.user_id, chat.create_timestamp, chat.language
        """

        result = await self.db.query(query=query, db_name=settings.ai_db_settings.name, params={"chat_id": chat_id})
        return result[0]

    # async def create_new_message(self, chat_id: int, value: MessageDataCreateUpdate, company_name: str, model_name: str):
    #     company_name, model_name = company_name.strip().lower(), model_name.strip().lower()
    #     await self.get_chat_history(chat_id=chat_id, bypass=True)
    #     if company_name not in self.available_models.keys():
    #         raise CustomException(status_code=400, detail="Invalid company name")
    #     if model_name not in self.available_models[company_name]:
    #         raise CustomException(status_code=400, detail="Invalid model name")
    #     current_chat = await self.get_chat(chat_id=chat_id)
    #
    #     pass
