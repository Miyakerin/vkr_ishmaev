from datetime import datetime

from services.auth_service.core.schemas import BaseDTO


class UserCreateUpdate(BaseDTO):
    username: str
    password: str
    email: str


class UserRead(BaseDTO):
    user_id: int
    username: str
    email: str
    is_admin: bool
    create_timestamp: datetime
