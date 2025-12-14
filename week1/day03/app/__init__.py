from fastapi import APIRouter

from app.api.v1 import hello_api

api_router = APIRouter()

# 集中注册
api_router.include_router(
    hello_api.router
)

