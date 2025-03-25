import pprint
from io import BytesIO
from typing import List, Union, Optional, Any

import aiohttp
from aiohttp import FormData
from fastapi import UploadFile
from sqlalchemy import insert, select, update

from services.ai_service.core.db_models import File, FileXCompany
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
        print(result)
        stmt = insert(File).values(
            filename=filename,
            s3_key=result["filename"],
            bucket_name=bucket,
            file_size=size,
            user_id=self.current_user.user_id,
            mimetype=result["content_type"]
        ).returning(File)
        result_2 = await (await self.db.sessions)[settings.ai_db_settings.name].execute(stmt)
        result_2 = result_2.mappings().one_or_none()
        if result_2 is None:
            raise CustomException(status_code=500, detail="File not uploaded")
        return result_2["File"]

    async def get_files(self,
                        file_ids: Optional[Union[int, List[int]]] = None,
                        user_ids: Optional[Union[int, List[int]]] = None,
                        bucket_names: Optional[Union[str, List[str]]] = None,
                        file_names: Optional[Union[str, List[str]]] = None,
                        existing: bool = True
                        ) -> List[File]:
        stmt = select(File)
        if file_ids is not None:
            if isinstance(file_ids, int):
                file_ids = [file_ids]
            stmt = stmt.where(
                File.file_id.in_(file_ids)
            )

        if user_ids is not None:
            if isinstance(user_ids, int):
                user_ids = [user_ids]
            stmt = stmt.where(
                File.user_id.in_(user_ids)
            )

        if bucket_names is not None:
            if isinstance(bucket_names, str):
                bucket_names = [bucket_names]
            stmt = stmt.where(
                File.bucket_name.in_(bucket_names)
            )

        if file_names is not None:
            if isinstance(file_names, str):
                file_names = [file_names]
            stmt = stmt.where(
                File.filename.in_(file_names)
            )

        if existing is True:
            stmt = stmt.where(
                File.delete_timestamp == None
            )
        elif existing is False:
            stmt = stmt.where(
                File.delete_timestamp != None
            )

        result = await (await self.db.sessions)[settings.ai_db_settings.name].execute(stmt)
        result = [x["File"] for x in result.mappings().all()]
        return result

    async def get_download_url(self, file_id: int) -> str:
        result = await self.get_files(file_ids=file_id, user_ids=self.current_user.user_id)
        if not result:
            raise CustomException(status_code=404, detail="File not found")
        result = result[0]
        url = (await self.s3.generate_url(keys=[result.s3_key], bucket=result.bucket_name, s3_name=settings.minio_settings.name))["urls"][0]["url"]
        return url

    async def get_files_x_company(
            self,
            file_x_company_ids: Optional[Union[int, List[int]]] = None,
            file_ids: Optional[Union[int, List[int]]] = None,
            company_names: Optional[Union[str, List[str]]] = None,
            file_company_ids: Optional[Union[str, List[str]]] = None,
            existing: bool = True
    ) -> List[FileXCompany]:
        stmt = select(FileXCompany)
        if file_x_company_ids is not None:
            if isinstance(file_x_company_ids, int):
                file_x_company_ids = [file_x_company_ids]
            stmt = stmt.where(
                FileXCompany.file_x_company_id.in_(file_x_company_ids)
            )
        if file_ids is not None:
            if isinstance(file_ids, int):
                file_ids = [file_ids]
            stmt = stmt.where(
                FileXCompany.file_id.in_(file_ids)
            )
        if company_names is not None:
            if isinstance(company_names, str):
                company_names = [company_names]
            stmt = stmt.where(
                FileXCompany.company_name.in_(company_names)
            )
        if file_company_ids is not None:
            if isinstance(file_company_ids, str):
                file_company_ids = [file_company_ids]
            stmt = stmt.where(
                FileXCompany.file_company_id.in_(file_company_ids)
            )
        if existing is True:
            stmt = stmt.where(
                FileXCompany.delete_timestamp == None
            )
        elif existing is False:
            stmt = stmt.where(
                FileXCompany.delete_timestamp != None
            )
        result = await (await self.db.sessions)[settings.ai_db_settings.name].execute(stmt)
        result = [x["FileXCompany"] for x in result.mappings().all()]
        return result

    async def upload_file_to_company(self, file_id: int, company_name: str) -> Any:
        company_name = company_name.strip().lower()
        if company_name not in self.available_companies:
            raise CustomException(status_code=404, detail="Company not found")
        file = await self.get_files(file_ids=file_id, user_ids=self.current_user.user_id)
        if not file:
            raise CustomException(status_code=404, detail="File not found")
        file = file[0]
        if company_name == self.gigachat:
            formdata = FormData()
            formdata.add_field(
                'file',
                BytesIO(await self.s3.get_file_content(
                    s3_name=settings.minio_settings.name,
                    filename=file.s3_key,
                    bucket=file.bucket_name
                )),
                filename=file.filename,
                content_type=file.mimetype)
            formdata.add_field("purpose", "general")
            async with aiohttp.ClientSession() as session:
                async with session.post(
                        url=settings.api_settings.gigachat.file_upload_url,
                        headers={"Authorization": f"Bearer {settings.api_settings.gigachat.access_token}"},
                        data=formdata,
                        ssl=False
                ) as resp:
                    if resp.status == 200:
                        print(resp.status)
                        print(await resp.json())
                        resp_json = await resp.json()
                        file_company_id = resp_json["id"]
                        id_type = "STRING"
                    else:
                        raise CustomException(status_code=500, detail="File not uploaded")
        else:
            raise CustomException(status_code=404, detail="Company not found")
        stmt = insert(FileXCompany).values(
            file_id=file.file_id,
            company_name=company_name,
            file_company_id=file_company_id,
            id_type=id_type
        )
        await (await self.db.sessions)[settings.ai_db_settings.name].execute(stmt)
        return file_company_id


