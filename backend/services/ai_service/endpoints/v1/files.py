from fastapi import APIRouter, UploadFile
from starlette import status

from services.ai_service.core.db_models import File
from services.ai_service.core.dependencies import CustomAuthDependency
from services.ai_service.core.settings import settings
from shared.dependencies import DbDependency

file_router = APIRouter(prefix="/file", tags=["files"])
db_dependency = DbDependency(engines_params=settings.all_db)
auth_dependency = CustomAuthDependency()

# @file_router.post("/", response_model=None, status_code=status.HTTP_201_CREATED)
# async def create_file(file: UploadFile = File(...)):
#     pass

