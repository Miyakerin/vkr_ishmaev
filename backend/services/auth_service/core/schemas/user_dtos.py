from datetime import datetime
from typing import Optional

from services.auth_service.core.schemas import BaseDTO


class UserCreateUpdate(BaseDTO):
    username: Optional[str] = None
    password: str
    email: Optional[str] = None


class UserRead(BaseDTO):
    user_id: int
    username: str
    email: str
    is_admin: bool
    create_timestamp: datetime
