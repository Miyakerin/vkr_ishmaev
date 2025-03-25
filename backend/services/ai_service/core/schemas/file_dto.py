import datetime

from services.ai_service.core.schemas import BaseDTO


class FileRead(BaseDTO):
    file_id: int
    filename: str
    s3_key: str
    bucket_name: str
    file_size: int
    user_id: int
    create_timestamp: datetime.datetime

