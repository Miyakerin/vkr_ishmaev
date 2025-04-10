from services.ai_service.core.schemas import BaseDTO


class UpdateToken(BaseDTO):
    amount: int


class GetUserBalance(BaseDTO):
    user_balance_id: int
    user_id: int
    balance: int