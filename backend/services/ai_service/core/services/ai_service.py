from services.ai_service.core.services import BaseService
from shared.db.sql_database import Database
from shared.dependencies import User
from shared.exceptions.exceptions import CustomException


class AIService(BaseService):

    available_models = {
        "gigachat": [],
        "openai": [],
        "deepseek": []
    }

    def __init__(self, db: Database = None, current_user: User = None):
        super(AIService, self).__init__(db=db, current_user=current_user)
