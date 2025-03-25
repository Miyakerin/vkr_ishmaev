import json

from fastapi import APIRouter, Depends, Query
from starlette import status
from starlette.responses import Response

from services.ai_service.core.dependencies import CustomAuthDependency
from services.ai_service.core.schemas.chat_dto import ChatCreateUpdate, ChatRead, MessageDataCreateUpdate, ChatsRead
from services.ai_service.core.services.ai_service import AIService
from services.ai_service.core.settings import settings
from shared.db import Database
from shared.db.s3 import S3Database
from shared.dependencies import DbDependency, User, S3Dependency

chat_router = APIRouter(prefix="/chat", tags=["chats"])
db_dependency = DbDependency(engines_params=settings.all_db)
s3_dependency = S3Dependency(s3_params=settings.all_s3)
auth_dependency = CustomAuthDependency()


@chat_router.post("", response_model=ChatRead, status_code=status.HTTP_201_CREATED)
async def create_chat(
        body: ChatCreateUpdate,
        db: Database = Depends(db_dependency),
        current_user: User = Depends(auth_dependency)
) -> Response:
    result = await AIService(db=db, current_user=current_user).create_chat(value=body)
    return Response(
        status_code=status.HTTP_201_CREATED,
        content=ChatRead.model_validate(result, from_attributes=True).model_dump_json(),
        headers={"Content-Type": "application/json"}
    )

@chat_router.get("", response_model=ChatsRead, status_code=status.HTTP_200_OK)
async def get_current_user_chats(
        db: Database = Depends(db_dependency),
        current_user: User = Depends(auth_dependency)
) -> Response:
    result = await AIService(db=db, current_user=current_user).get_chats(user_ids=current_user.user_id)
    return Response(
        status_code=status.HTTP_200_OK,
        content=ChatsRead.model_validate({"items": result}, from_attributes=True).model_dump_json(),
        headers={"Content-Type": "application/json"}
    )


@chat_router.get("/{chat_id}/history", response_model=None, status_code=status.HTTP_200_OK)
async def get_chat_history(
        chat_id: int,
        db: Database = Depends(db_dependency),
        current_user: User = Depends(auth_dependency)
) -> Response:
    result = await AIService(db=db, current_user=current_user).get_chat_history(chat_id=chat_id)
    return Response(
        status_code=status.HTTP_200_OK,
        content=json.dumps(result, default=str),
        headers={"Content-Type": "application/json"}
    )


@chat_router.post("/{chat_id}/message", response_model=None, status_code=status.HTTP_201_CREATED)
async def new_message(
        body: MessageDataCreateUpdate,
        chat_id: int,
        company_name: str = Query(...),
        model_name: str = Query(...),
        db: Database = Depends(db_dependency),
        s3: S3Database = Depends(s3_dependency),
        current_user: User = Depends(auth_dependency)
) -> Response:
    return await AIService(db=db, current_user=current_user, s3=s3).create_new_message(chat_id=chat_id, value=body, company_name=company_name, model_name=model_name)
