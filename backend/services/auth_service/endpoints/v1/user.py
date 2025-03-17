from fastapi import APIRouter, Depends
from starlette import status
from starlette.responses import Response

from services.auth_service.core.schemas.user_dtos import UserCreateUpdate, UserRead
from services.auth_service.core.services.user_service import UserService
from services.auth_service.core.settings import settings
from shared.db.sql_database import DbDependency, Database

user_router = APIRouter(prefix="/user", tags=["user"])
db_dependency = DbDependency(engines_params=settings.all_db)


@user_router.post("/login", response_model=UserRead, status_code=status.HTTP_200_OK)
async def login(
        body: UserCreateUpdate,
        db: Database = Depends(db_dependency),
):
    result = await UserService(db=db).login_user(username=body.username, password=body.password, email=body.email)
    return Response(
        status_code=status.HTTP_200_OK,
        content=UserRead.model_validate(
            result,
            from_attributes=True
        ).model_dump_json(),
        headers={"content-type": "application/json"}
    )


@user_router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(
        body: UserCreateUpdate,
        db: Database = Depends(db_dependency),
) -> Response:
    result = await UserService(db=db).create_user(username=body.username, email=body.email, password=body.password)
    return Response(
        status_code=status.HTTP_201_CREATED,
        content=UserRead.model_validate(
            result,
            from_attributes=True
        ).model_dump_json(),
        headers={"content-type": "application/json"}
    )
