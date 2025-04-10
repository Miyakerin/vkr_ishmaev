import datetime
from typing import List

from services.ai_service.core.schemas import BaseDTO


class ModelRead(BaseDTO):
    id: int
    company_name: str
    model_name: str


class ManyModelRead(BaseDTO):
    items: List[ModelRead]

