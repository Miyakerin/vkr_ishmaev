from fastapi import APIRouter, Depends
from starlette import status
from starlette.responses import Response

from services.auth_service.core.schemas.jwk import JWTToken
from services.auth_service.core.schemas.user_dtos import UserCreateUpdate, UserRead, ForgetDTO
from services.auth_service.core.services.jwt_service import JWTService
from services.auth_service.core.services.user_service import UserService
from services.auth_service.core.settings import settings
from shared.db.sql_database import Database
from shared.dependencies import DbDependency, AuthDependency, User
from shared.exceptions.exceptions import CustomException

user_router = APIRouter(prefix="/user", tags=["user"])
jwt_service = JWTService(jwt_settings=settings.jwt_settings)

db_dependency = DbDependency(engines_params=settings.all_db)
auth_dependency = AuthDependency(public_jwk=jwt_service.public_jwk)


@user_router.post("/login", response_model=JWTToken, status_code=status.HTTP_200_OK)
async def login(
        body: UserCreateUpdate,
        db: Database = Depends(db_dependency),
):
    user = await UserService(db=db).login_user(username=body.username, password=body.password, email=body.email)
    result = await jwt_service.generate_jwt(user_id=user.user_id, is_admin=user.is_admin)
    return Response(
        status_code=status.HTTP_200_OK,
        content=JWTToken.model_validate(
            {"access_token": result.decode("UTF-8")},
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

@user_router.post("/email_code", response_model=None, status_code=status.HTTP_204_NO_CONTENT)
async def send_email_conde(
        body: ForgetDTO,
        db: Database = Depends(db_dependency)
) -> Response:
    await UserService(db=db).send_restore_code(username=body.username, code_type=UserService.email_code_type, is_verified=None)
    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )

@user_router.post("/forget_password", response_model=None, status_code=status.HTTP_204_NO_CONTENT)
async def forget(
        body: ForgetDTO,
        db: Database = Depends(db_dependency)
) -> Response:
    await UserService(db=db).send_restore_code(username=body.username, code_type=UserService.password_code_type)
    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )


@user_router.post("/restore_password", response_model=None, status_code=status.HTTP_204_NO_CONTENT)
async def restore_password(
        body: ForgetDTO,
        db: Database = Depends(db_dependency)
) -> Response:
    if not body.username or not body.code:
        raise CustomException(status_code=422, detail="Username or Code is invalid")
    await UserService(db=db).restore_password(username=body.username, code=body.code)
    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )


@user_router.post("/verify_email", response_model=None, status_code=status.HTTP_204_NO_CONTENT)
async def verify_email(
        body: ForgetDTO,
        db: Database = Depends(db_dependency)
) -> Response:
    if not body.username or not body.code:
        raise CustomException(status_code=422, detail="Username or Code is invalid")
    await UserService(db=db).verify_email(username=body.username, code=body.code)
    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )


@user_router.post("/verify", response_model=None, status_code=status.HTTP_200_OK)
async def verify(
    current_user: User = Depends(auth_dependency),
) -> Response:
    return Response("ok", status_code=status.HTTP_200_OK)


@user_router.get("/{user_id}", response_model=None, status_code=status.HTTP_200_OK)
async def get_user(
        user_id: int,
        db: Database = Depends(db_dependency),
        current_user: User = Depends(auth_dependency),
):
    if current_user.user_id == user_id or current_user.is_admin:
        user = await UserService(db=db).get_users(user_ids=user_id)
        if user:
            user = user[0]
        return Response(
            status_code=status.HTTP_200_OK,
            headers={"content-type": "application/json"},
            content=UserRead.model_validate(
                user,
                from_attributes=True
            ).model_dump_json()
        )
    raise CustomException(status_code=status.HTTP_401_UNAUTHORIZED)



