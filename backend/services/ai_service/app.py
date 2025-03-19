from contextlib import asynccontextmanager

import asyncio
import sqlalchemy
from fastapi import FastAPI

from services.ai_service.core.scripts import refresh_key_every_n_minutes, refresh_api_tokens_n_minutes


@asynccontextmanager
async def lifespan(app: FastAPI):
    from core.scripts import init
    await init()

    from endpoints import api_router
    app.include_router(api_router, prefix="/auth")
    asyncio.create_task(refresh_key_every_n_minutes(settings_=settings, minutes=30))
    asyncio.create_task(refresh_api_tokens_n_minutes(settings_=settings, minutes=15))
    yield

app = FastAPI(
    title="AI Service",
    description="AI Service",
    docs_url="/docs",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

from fastapi.middleware.cors import CORSMiddleware
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

from shared.exceptions.exception_handlers import exception_handler, connection_exception_handler, integrity_error_handler
app.add_exception_handler(sqlalchemy.exc.IntegrityError, integrity_error_handler)
app.add_exception_handler(sqlalchemy.exc.InterfaceError, connection_exception_handler)
app.add_exception_handler(Exception, exception_handler)

if __name__ == "__main__":
    import uvicorn
    from core.settings import settings
    uvicorn.run(app, host="0.0.0.0", port=settings.service_settings.port_container)
