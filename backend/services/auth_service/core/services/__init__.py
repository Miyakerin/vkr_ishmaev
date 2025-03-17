class BaseService:
    def __init__(self, session=None, current_user=None):
        self.__session = session
        self.__current_user = current_user

    @property
    def session(self):
        if not self.__session:
            pass
        return self.__session

    @property
    def current_user(self):
        if not self.__current_user:
            pass
        return self.__current_user
