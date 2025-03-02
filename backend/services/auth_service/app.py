from fastapi import FastAPI

from endpoints import api_router

app = FastAPI(
    title="Auth Service",
    description="Auth Service",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

app.include_router(api_router, prefix="/auth")