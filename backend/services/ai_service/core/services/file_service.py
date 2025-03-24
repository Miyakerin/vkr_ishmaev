import pprint
from typing import List, Union, Optional

import aiohttp
from fastapi import UploadFile
from sqlalchemy import insert, select, update

from services.ai_service.core.db_models import Chat, Message, MessageData, MessageDataXFile, File, FileXCompany, \
    UserBalance
from services.ai_service.core.schemas.chat_dto import ChatCreateUpdate, MessageDataRead, MessageDataCreateUpdate
from services.ai_service.core.services import BaseService
from services.ai_service.core.settings import settings
from shared.db.s3 import S3Database
from shared.db.sql_database import Database
from shared.dependencies import User
from shared.exceptions.exceptions import CustomException


class FileService(BaseService):

    def __init__(self, db: Database = None, current_user: User = None, s3: S3Database = None):
        super(FileService, self).__init__(db=db, current_user=current_user, s3=s3)

    async def upload_file(self, file: UploadFile, filename: str=None, bucket:str="private"):
        result = await self.s3.upload_file(file=file, s3_name=settings.minio_settings.name, filename=filename, bucket=bucket)

