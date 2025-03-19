from services.ai_service.core.services import BaseService
from shared.db.sql_database import Database
from shared.exceptions.exceptions import CustomException


class AIService(BaseService):
    def __init__(self, db:Database=None, current_user=None):
        super(AIService, self).__init__(db=db, current_user=current_user)
