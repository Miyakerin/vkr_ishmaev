from fastapi import APIRouter, UploadFile, Depends, File
from starlette import status

from services.ai_service.core.dependencies import CustomAuthDependency
from services.ai_service.core.services.file_service import FileService
from services.ai_service.core.settings import settings
from shared.db import Database
from shared.db.s3 import S3Database
from shared.dependencies import DbDependency, User, S3Dependency

file_router = APIRouter(prefix="/file", tags=["files"])
db_dependency = DbDependency(engines_params=settings.all_db)
s3_dependency = S3Dependency(s3_params=settings.all_s3)
auth_dependency = CustomAuthDependency()


@file_router.post("/", response_model=None, status_code=status.HTTP_201_CREATED)
async def create_file(file: UploadFile = File(...), current_user: User = Depends(auth_dependency), db: Database=Depends(db_dependency), s3: S3Database=Depends(s3_dependency)):
    result = await FileService(current_user=current_user, db=db, s3=s3).upload_file(file)
    pass

