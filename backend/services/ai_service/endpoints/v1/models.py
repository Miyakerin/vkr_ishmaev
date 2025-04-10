import json

from fastapi import APIRouter, Depends, Query
from starlette import status
from starlette.responses import Response

from services.ai_service.core.dependencies import CustomAuthDependency
from services.ai_service.core.schemas.models_dto import ManyModelRead
from services.ai_service.core.services.ai_service import AIService
from services.ai_service.core.settings import settings
from shared.db import Database
from shared.dependencies import DbDependency, User, S3Dependency

models_router = APIRouter(prefix="/models", tags=["models"])
db_dependency = DbDependency(engines_params=settings.all_db)
s3_dependency = S3Dependency(s3_params=settings.all_s3)
auth_dependency = CustomAuthDependency()


@models_router.get("", response_model=ManyModelRead, status_code=status.HTTP_201_CREATED)
async def get_models(
        db: Database = Depends(db_dependency),
        current_user: User = Depends(auth_dependency)
) -> Response:
    result = await AIService(db=db, current_user=current_user).get_models_list()
    return Response(
        status_code=status.HTTP_200_OK,
        content=ManyModelRead.model_validate({"items": result}, from_attributes=True).model_dump_json(),
        headers={"Content-Type": "application/json"}
    )