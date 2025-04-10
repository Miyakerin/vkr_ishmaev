from typing import Optional

from fastapi import APIRouter, Depends
from starlette import status

from services.ai_service.core.dependencies import CustomAuthDependency
from services.ai_service.core.schemas.tokens_dto import UpdateToken, GetUserBalance
from services.ai_service.core.services.token_service import TokenService
from services.ai_service.core.settings import settings
from shared.db import Database
from shared.dependencies import DbDependency, User, S3Dependency

token_router = APIRouter(prefix="/tokens", tags=["tokens"])
db_dependency = DbDependency(engines_params=settings.all_db)
s3_dependency = S3Dependency(s3_params=settings.all_s3)
auth_dependency = CustomAuthDependency()


@token_router.get("",  status_code=status.HTTP_200_OK)
async def get_tokens_balance(
        db: Database = Depends(db_dependency),
        current_user: User = Depends(auth_dependency)
) -> Optional[GetUserBalance]:
    result = await TokenService(db=db, current_user=current_user).get_user_balance()
    if not result:
        result = await TokenService(db=db, current_user=current_user).add_n_tokens(0)
    print(result)
    return GetUserBalance.model_validate(result, from_attributes=True)


@token_router.post("", status_code=status.HTTP_201_CREATED)
async def add_tokens(
        body: UpdateToken,
        db: Database = Depends(db_dependency),
        current_user: User = Depends(auth_dependency)
) -> GetUserBalance:
    result = await TokenService(db=db, current_user=current_user).add_n_tokens(n_tokens=body.amount)
    return GetUserBalance.model_validate(result, from_attributes=True)