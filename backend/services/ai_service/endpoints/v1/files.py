import json

from fastapi import APIRouter, UploadFile, Depends, File
from starlette import status
from starlette.responses import Response

from services.ai_service.core.dependencies import CustomAuthDependency
from services.ai_service.core.schemas.file_dto import FileRead
from services.ai_service.core.services.file_service import FileService
from services.ai_service.core.settings import settings
from shared.db import Database
from shared.db.s3 import S3Database
from shared.dependencies import DbDependency, User, S3Dependency

file_router = APIRouter(prefix="/file", tags=["files"])
db_dependency = DbDependency(engines_params=settings.all_db)
s3_dependency = S3Dependency(s3_params=settings.all_s3)
auth_dependency = CustomAuthDependency()


@file_router.post("/", response_model=FileRead, status_code=status.HTTP_201_CREATED)
async def create_file(
        file: UploadFile = File(...),
        current_user: User = Depends(auth_dependency),
        db: Database=Depends(db_dependency),
        s3: S3Database=Depends(s3_dependency)
) -> Response:
    result = await FileService(current_user=current_user, db=db, s3=s3).upload_file(file)
    return Response(
        status_code=status.HTTP_201_CREATED,
        content=FileRead.model_validate(result, from_attributes=True).model_dump_json(),
        headers={"Content-Type": "application/json"}
    )


@file_router.get("/{file_id}", response_model=None, status_code=status.HTTP_200_OK)
async def get_download_url(
        file_id: int,
        current_user: User = Depends(auth_dependency),
        db: Database=Depends(db_dependency),
        s3: S3Database=Depends(s3_dependency)
) -> Response:
    result = await FileService(s3=s3, current_user=current_user, db=db).get_download_url(file_id=file_id)
    return Response(
        status_code=status.HTTP_200_OK,
        content=json.dumps({"url": result}),
        headers={"Content-Type": "application/json"}
    )

