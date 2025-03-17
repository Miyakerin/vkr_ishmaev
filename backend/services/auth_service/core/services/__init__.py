from fastapi import HTTPException

from shared.db.sql_database import Database


class BaseService:
    def __init__(self, db:Database=None, current_user=None):
        self.__db = db
        self.__current_user = current_user

    @property
    def db(self) -> Database:
        if not self.__db:
            raise HTTPException(status_code=404, detail='Database not provided')
        return self.__db

    @property
    def current_user(self):
        if not self.__current_user:
            raise HTTPException(status_code=404, detail='User not provided')
        return self.__current_user
