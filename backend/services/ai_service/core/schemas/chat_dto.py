from datetime import datetime

from pydantic import model_validator
import typing as tp

from services.ai_service.core.schemas import BaseDTO


class ChatCreateUpdate(BaseDTO):
    language: str


class ChatRead(BaseDTO):
    chat_id: int
    user_id: int
    language: str
    create_timestamp: datetime


class ChatsRead(BaseDTO):
    items: tp.List[ChatRead]


class MessageDataCreateUpdate(BaseDTO):
    message_data: str


class MessageDataRead(BaseDTO):
    message_data_id: int
    message_id: int
    create_timestamp: datetime


class MessageRead(BaseDTO):
    message_id: int
    chat_id: int
    create_timestamp: datetime
    message_data: tp.List[MessageDataRead]
