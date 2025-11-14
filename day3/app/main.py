from fastapi import FastAPI

from app import api_router


def create_app()->FastAPI:
    app = FastAPI(
        title="day3.demo",
        description="day3.demo",
        version="0.1.0",
        docs_url="/api/v1/docs",
        redoc_url="/api/v1/redoc",
        openapi_url="/api/v1/openapi.json"
    )

    # 挂载所有app路由
    app.include_router(api_router)

    return app


app = create_app()