from fastapi import APIRouter, Depends, Query
from starlette import status
from starlette.responses import Response

from services.ai_service.core.dependencies import CustomAuthDependency
from services.ai_service.core.schemas.chat_dto import ChatCreateUpdate, ChatRead, MessageDataCreateUpdate
from services.ai_service.core.services.ai_service import AIService
from services.ai_service.core.settings import settings
from shared.db import Database
from shared.dependencies import DbDependency, User

chat_router = APIRouter(prefix="/chat", tags=["chats"])
db_dependency = DbDependency(engines_params=settings.all_db)
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


@chat_router.post("/{chat_id}/message", response_model=None, status_code=status.HTTP_201_CREATED)
async def new_message(
        body: MessageDataCreateUpdate,
        chat_id: int,
        company_name: str = Query(...),
        model_name: str = Query(...),
        db: Database = Depends(db_dependency),
        current_user: User = Depends(auth_dependency)
) -> Response:
    await AIService(db=db, current_user=current_user).create_new_message(chat_id=chat_id, value=body, company_name=company_name, model_name=model_name)