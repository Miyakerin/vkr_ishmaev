from fastapi import HTTPException

from shared.db.s3 import S3Database
from shared.db.sql_database import Database
from shared.dependencies import User


class BaseService:
    gigachat = "gigachat"
    openai = "openai"
    deepseek = "deepseek"
    available_companies = [gigachat, openai, deepseek]

    def __init__(self, db: Database = None, current_user: User = None, s3: S3Database = None):
        self.__db = db
        self.__current_user = current_user
        self.__s3 = s3

    @property
    def db(self) -> Database:
        if not self.__db:
            raise HTTPException(status_code=404, detail='Database not provided')
        return self.__db

    @property
    def current_user(self) -> User:
        if not self.__current_user:
            raise HTTPException(status_code=404, detail='User not provided')
        return self.__current_user

    @property
    def s3(self) -> S3Database:
        if not self.__s3:
            raise HTTPException(status_code=404, detail='Database not provided')
        return self.__s3
