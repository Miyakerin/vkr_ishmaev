import traceback

import aiohttp
import sqlalchemy
from fastapi.encoders import jsonable_encoder
from fastapi.requests import Request
from fastapi.responses import Response
from starlette.datastructures import UploadFile
from starlette.responses import JSONResponse

from shared.exceptions.exceptions import CustomException

is_occupied = False


async def connection_exception_handler(
        request: Request, exc: sqlalchemy.exc.InterfaceError
):
    global is_occupied
    if is_occupied:
        raise CustomException(status_code=500, detail="retry later")
    is_occupied = True
    try:
        async with aiohttp.ClientSession() as session:
            method = request.method
            url = str(request.url)
            data = None
            form = None
            try:
                data = await request.body()
            except:
                pass
            try:
                form = await request.form()
            except:
                pass

            if not data or data == b'{}':
                data = None

            params = dict(request.query_params)
            request_headers = dict(request.headers)

            if form:
                data = aiohttp.FormData()
                # Если не убрать header content-type - не отправится запрос с формдатой
                # Если захочется переделать - готовься к расчёту boundary
                request_headers.pop('content-type')

                # multi_items, так как формдата != словарь с уникальными ключами
                # Если использовать items(), то нельзя передать сервисам внутри биста "массивы" чего-либо в формдате
                for k, v in form.multi_items():
                    if not isinstance(v, UploadFile):
                        data.add_field(k, v)
                    else:
                        # TODO
                        data.add_field(name=k, value=await v.read(), filename=v.filename)

            ## Подготовка данных запроса
            request_headers = {k: str(v) for k, v in request_headers.items() if v is not None}

            async with session.request(
                    method=method, url=url, headers=request_headers, params=params, data=data
            ) as resp:
                resp_headers = dict(resp.headers)
                media_type = resp_headers.get("content-type", None)
                content = await resp.content.read()
                status_code = resp.status
                is_occupied = False
                return Response(
                    content=content,
                    headers=resp_headers,
                    media_type=media_type,
                    status_code=status_code,
                )
    except Exception:
        is_occupied = False
        return JSONResponse(content=jsonable_encoder({"message": "try later"}), status_code=500)


async def integrity_error_handler(request: Request, exc: sqlalchemy.exc.IntegrityError):
    if exc.orig.pgcode == "23503":
        raise CustomException(status_code=400, detail="Foreign key violadtion error")
    if exc.orig.pgcode == "23505":
        raise CustomException(status_code=400, detail="Unique violation error")
    raise CustomException(status_code=500, detail="Unhandled SQL error")


async def exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        content={
            'message': 'Произошла ошибка',
            'error': str(exc),
            'traceback': str(traceback.format_tb(exc.__traceback__))
        },
        status_code=400
    )
