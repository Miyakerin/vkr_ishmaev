import pprint
from typing import List, Union, Optional

import aiohttp
from fastapi import UploadFile
from sqlalchemy import insert, select, update

from services.ai_service.core.db_models import File
from services.ai_service.core.services import BaseService
from services.ai_service.core.settings import settings
from shared.db.s3 import S3Database
from shared.db.sql_database import Database
from shared.dependencies import User
from shared.exceptions.exceptions import CustomException


class FileService(BaseService):

    def __init__(self, db: Database = None, current_user: User = None, s3: S3Database = None):
        super(FileService, self).__init__(db=db, current_user=current_user, s3=s3)

    async def upload_file(self, file: UploadFile, filename: str=None, bucket:str="private") -> File:
        filename = filename or file.filename
        size = file.size
        result = await self.s3.upload_file(file=file, s3_name=settings.minio_settings.name, filename=filename, bucket=bucket)
        stmt = insert(File).values(
            filename=filename,
            s3_key=result["filename"],
            bucket_name=bucket,
            file_size=size,
            user_id=self.current_user.user_id
        ).returning(File)
        result_2 = await (await self.db.sessions)[settings.ai_db_settings.name].execute(stmt)
        result_2 = result_2.mappings().one_or_none()
        if result_2 is None:
            raise CustomException(status_code=500, detail="File not uploaded")
        return result_2["File"]

    async def get_download_url(self, file_id: int) -> str:
        stmt = (
            select(File)
            .where(
                (file_id == File.file_id)
                & (File.user_id == self.current_user.user_id)
            )
        )
        result = await (await self.db.sessions)[settings.ai_db_settings.name].execute(stmt)
        result = result.mappings().one_or_none()
        if result is None:
            raise CustomException(status_code=404, detail="File not found")
        result = result["File"]
        url = (await self.s3.generate_url(keys=[result.s3_key], bucket=result.bucket_name, s3_name=settings.minio_settings.name))["urls"][0]["url"]
        return url

