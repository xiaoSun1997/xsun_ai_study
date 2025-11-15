from fastapi import FastAPI

from app.api.fetchOneApi import async_router


def create_app()->FastAPI:
    app = FastAPI(
        title="day4.demo",
        description="day4.demo",
        version="0.1.0",
        docs_url="/api/v1/docs",
        redoc_url="/api/v1/redoc",
        openapi_url="/api/v1/openapi.json"
    )
    app.include_router(async_router)
    return app

app = create_app()