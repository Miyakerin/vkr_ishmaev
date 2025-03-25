import base64
import copy
import io
import mimetypes
import os
import typing as tp
import uuid

import aioboto3
from botocore.exceptions import ClientError
from fastapi import UploadFile


class S3_error(Exception):
    ...

class S3Session:
    """Класс для хранения и управления сессией подключения к s3
    """
    def __init__(self, s3_access_key, s3_secret_key, s3_uri):
        self.__s3_access_key = s3_access_key
        self.__s3_secret_key = s3_secret_key
        self.__s3_uri = s3_uri

        ## Создание сессии, отложено до востребования
        self.__session = None

    @property
    def uri(self):
        return self.__s3_uri

    @property
    def session(self):
        if not self.__session:
            self.__session = aioboto3.Session(
                    aws_access_key_id=self.__s3_access_key,
                    aws_secret_access_key=self.__s3_secret_key,
                    # region_name=settings.MINIO_REGION_NAME
                )
        return self.__session

    @property
    def client(self):
        client = self.session.client(
                "s3",
                endpoint_url=self.__s3_uri,
                use_ssl=True,
                verify=False
            )
        return client


class S3Database:
    """Класс для кэширования сессий aioboto
    """

    def __init__(self, s3_params: list[dict[str, tp.Union[int, str, bool]]]):
        self.__sessions: dict[str, tp.Optional[S3Session]] = {}
        self.__s3_params = {}

        for s3_param in s3_params:
            s3_param_ = copy.deepcopy(s3_param)
            name = s3_param_.pop("name")
            self.__s3_params[name] = s3_param_

    @property
    def sessions(self) -> dict[str, tp.Optional[S3Session]]:
        if not self.__sessions:
            for s3_name, s3_param in self.__s3_params.items():
                self.__sessions[s3_name] = S3Session(
                    s3_access_key=s3_param["s3_access_key"],
                    s3_secret_key=s3_param["s3_secret_key"],
                    s3_uri=s3_param["s3_uri"]
                )
        return self.__sessions

    def get_session(self, s3_name: str):
        sessions = self.sessions
        try:
            return sessions[s3_name]
        except KeyError:
            raise S3_error(f"Базы данных с name = {s3_name} не найдено")

    async def _generate_unique_key(self, filename: str, bucket: str, s3_name: str) -> str:
        base_name, extension = os.path.splitext(filename)
        key = filename
        counter = 1
        while True:
            try:
                async with self.get_session(s3_name=s3_name).client as s3_client:
                    await s3_client.head_object(Bucket=bucket, Key=key)
                    key = f"{base_name}_{counter}{extension}"
                    counter += 1
            except ClientError as e:
                if e.response['Error']['Code'] == '404':
                    break
                else:
                    raise
        return key

    async def upload_file(self, file: UploadFile, s3_name: str, bucket='private',
                          filename: tp.Optional[str] = None,
                          ACL='private'):
        """ACL: public-read | private
        MINIO не поддерживает ACL
        """

        file_content = await file.read()
        if not filename:
            filename = file.filename
        kind = get_filetype(filename=filename)
        key = await self._generate_unique_key(filename=filename, bucket=bucket, s3_name=s3_name)

        async with self.get_session(s3_name=s3_name).client as s3_client:
            response = await s3_client.put_object(
                Bucket=bucket,
                Key=key,
                Body=file_content,
                ContentType=kind,
                ACL=ACL
            )

        return {
            's3_response': response,
            'filename': key,
            'content_type': kind,
            'bucket': bucket,
            'ACL': ACL
        }

    async def generate_url(self, keys: tp.List[str], s3_name: str, bucket: str = 'private', expires_in=3600):

        if type(keys) is str:
            keys = [keys]

        files_urls = []
        for key in keys:
            async with self.get_session(s3_name=s3_name).client as s3_client:
                response = await s3_client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': bucket, 'Key': key},
                    ExpiresIn=expires_in
                )
                files_urls.append(
                    {
                        'key': key,
                        'url': response
                    }
                )

        return {
            'urls': files_urls
        }

    async def upload_base64(self, base64_code: str, s3_name: str, bucket: str = 'private', acl: str = 'private'):
        """ Загрузить файл в формате base64 """

        file_extension = '.png'

        split_base64_code = base64_code.split(',')
        if len(split_base64_code) == 2:
            start = split_base64_code[0].find('/') + 1
            end = split_base64_code[0].find(';')
            file_extension = f'.{split_base64_code[0][start:end]}'
            base64_code = split_base64_code[1]

        filename = uuid.uuid4().hex + file_extension

        file = UploadFile(file=io.BytesIO(base64.b64decode(base64_code)), filename=filename)

        resp = await self.upload_file(file=file, filename=filename, bucket=bucket, ACL=acl, s3_name=s3_name)

        return resp

    async def get_file_content(self,s3_name: str, filename: str = None, bucket='private') -> bytes:
        async with self.get_session(s3_name=s3_name).client as s3_client:
            s3_response = await s3_client.get_object(
                Bucket=bucket,
                Key=filename
            )
            s3_object_body = s3_response.get('Body')

            content = await s3_object_body.read()
        return content

    async def get_file(self, s3_name: str, filename: str = None, bucket='private') -> UploadFile:
        """
        Пример записи результата в файл:
        import aiofiles

        async with aiofiles.open('./data/test_s3_download_upload_file.jpg', 'wb') as out_file:
            content = await file.read()  # async read
            await out_file.write(content)  # async write
        """
        file_content = await self.get_file_content(filename=filename, s3_name=s3_name, bucket=bucket)
        file_bytes = io.BytesIO(file_content)
        file_bytes.seek(0)
        file_bytes.name = filename
        file_buffered_reader = io.BufferedReader(file_bytes)

        file = UploadFile(
            file=file_buffered_reader,
            filename=filename
        )

        return file


def get_filetype(filename: str):
    kind = mimetypes.guess_type(filename)[0]

    if kind is None:
        kind = 'text/plain'
    if str(filename.split('.')[-1]) == 'webp':
        kind = 'image/webp'
    return kind