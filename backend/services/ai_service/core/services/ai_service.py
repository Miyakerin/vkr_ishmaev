import pprint
from typing import List, Union, Optional

import aiohttp
from sqlalchemy import insert, select, update

from services.ai_service.core.db_models import Chat, Message, MessageData, MessageDataXFile, File, FileXCompany, \
    UserBalance
from services.ai_service.core.schemas.chat_dto import ChatCreateUpdate, MessageDataRead, MessageDataCreateUpdate
from services.ai_service.core.services import BaseService
from services.ai_service.core.settings import settings
from shared.db.sql_database import Database
from shared.dependencies import User
from shared.exceptions.exceptions import CustomException


class AIService(BaseService):

    default_system_prompts = {
        "ru": "Ты чат-бот помощник, который все силы прилагает, чтобы решить вопрос пользователя, ты отвечаешь кратко",
        "en": "You are chat-bot helper, who do everything you can for solving user problems, your responses are short"
    }

    models_settings = {
        "gigachat": {
            "roles": {
                "system": "system",
                "user": "user",
                "assistant": "assistant"
            },
            "models": [x.lower() for x in ["GigaChat-2", "GigaChat-2-Max", "GigaChat"]]
        }
    }

    available_languages = ["ru", "en"]

    type_cast = {
        "int": int,
        "str": str
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
            stmt = stmt.where(Chat.delete_timestamp == None)
        elif existing is False:
            stmt = stmt.where(Chat.delete_timestamp != None)
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

    async def get_chat_history(self, chat_id: int, bypass: bool = False, only_main: bool = False):
        if not bypass:
            current_chat = await self.get_chat(chat_id=chat_id)

        main_array = "true" if only_main else "true, false"
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
                            'file_create_timestamp', file.create_timestamp,
                            'company_file', json_agg_strict(json_build_object(
                                'file_x_company_id', file_company.file_x_company_id,
                                'company_name', file_company.company_name,
                                'file_company_id', file_company.file_company_id,
                                'id_type', file_company.id_type,
                                'create_timestamp', file_company.create_timestamp
                            ))
                        ) as data
                        FROM {MessageDataXFile.__tablename__} as attachment
                        
                        INNER JOIN {File.__tablename__} as file
                            ON file.file_id = attachment.file_id AND file.delete_timestamp IS NULL
                            
                        LEFT JOIN {FileXCompany.__tablename__} as file_company
                            ON file_company.file_id = file.file_id AND file_company.delete_timestamp IS NULL
                            
                        WHERE attachment.delete_timestamp IS NULL
                        GROUP BY attachment.message_data_x_file_id, attachment.file_id, attachment.create_timestamp, file.filename, file.s3_key, file.bucket_name, file.create_timestamp
                    ) as attachment
                        ON attachment.message_data_id = message_data.message_data_id
                    
                    WHERE message_data.delete_timestamp IS NULL AND message_data.is_main = ANY(ARRAY[{main_array}])
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
        return result[0]["data"]

    # todo: better code structure, wrap in sub-functions
    async def create_new_message(self, chat_id: int, value: MessageDataCreateUpdate, company_name: str, model_name: str) -> dict[str, Union[str, int]]:
        company_name, model_name = company_name.strip().lower(), model_name.strip().lower()
        if company_name not in self.models_settings.keys():
            raise CustomException(status_code=400, detail="Invalid company name")
        if model_name not in self.models_settings[company_name]["models"]:
            raise CustomException(status_code=400, detail="Invalid model name")
        current_chat = await self.get_chat(chat_id=chat_id)
        chat_history = await self.get_chat_history(chat_id=chat_id, bypass=True, only_main=True)
        previous_messages = []
        for message in chat_history["messages"]:
            if company_name == "gigachat":
                current_attachments = []
                for file in message["message_data"][0]["attachments"]:
                    file_flag = False
                    for company_file in file["company_file"]:
                        if company_file["company_name"] == company_name:
                            current_attachments.append(self.type_cast[company_file["id_type"]](company_file["file_company_id"]))
                            file_flag = True
                    if not file_flag:
                        # todo upload to company
                        pass
                previous_messages.append({
                    "role": self.models_settings[company_name]["roles"]["user"] if message["sender"] == "user" else self.models_settings[company_name]["roles"]["assistant"],
                    "content": message["message_data"][0]["text"],
                    "attachments": current_attachments
                })
            else:
                raise CustomException(status_code=400, detail="Company currently not supported")

        request_body = {}
        if company_name == "gigachat":
            url = settings.api_settings.gigachat.completions_url
            previous_messages.insert(0, {
                "role": self.models_settings[company_name]["roles"]["system"],
                "content": self.default_system_prompts[chat_history["chat_data"]["language"]],
            })
            previous_messages.append(
                {
                    "role": self.models_settings[company_name]["roles"]["user"],
                    "content": value.message_data
                }
            )
            request_body["model"] = model_name
            request_body["messages"] = previous_messages
        else:
            raise CustomException(status_code=400, detail="Company currently not supported")

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=url,
                json=request_body,
                headers={"Authorization": f"Bearer {settings.api_settings.gigachat.access_token}"},
                ssl=False
            ) as resp:
                if resp.status == 200:
                    json_response = await resp.json()
                    print(json_response)
                    response_message = json_response["choices"][0]["message"]["content"]
                    tokens_consumed = json_response["usage"]["total_tokens"]
                    stmt = insert(Message).values([
                        {
                            "company_name": None,
                            "sender": "user",
                            "chat_id": chat_id,
                        },
                        {
                            "company_name": company_name,
                            "sender": "assistant",
                            "chat_id": chat_id,
                        }
                    ]).returning(Message)
                    result_message = [x["Message"] for x in (await (await self.db.sessions)[settings.ai_db_settings.name].execute(stmt)).mappings().all()]
                    stmt = insert(MessageData).values(
                        [
                            {
                                "message_id": result_message[0].message_id,
                                "text": value.message_data,
                                "is_main": True
                            },
                            {
                                "message_id": result_message[1].message_id,
                                "text": response_message,
                                "is_main": True
                            }
                        ]
                    )
                    await ((await self.db.sessions)[settings.ai_db_settings.name].execute(stmt))

                else:
                    raise CustomException(status_code=400, detail=f"{company_name} not working")
        return {"message": response_message, "total_tokens": tokens_consumed}
