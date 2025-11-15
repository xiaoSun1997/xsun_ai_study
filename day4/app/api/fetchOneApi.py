from typing import List
from fastapi import FastAPI, Query, APIRouter
import asyncio

from app.service.fetchUrl import fecthUrl
import httpx

app = FastAPI(title="Aysnc DEMO", prefix="/api/v1/async", tags=["async"])

async_router = APIRouter(
    prefix="/fetch-multi",
    tags=["async"]
)

fecthUrl = fecthUrl()

@async_router.get("", summary="并发抓取多个 URL")
async def fetch_more(
        urls: List[str] = Query(..., example=["https://www.baidu.com",
                                              "https://www.python.org"])
):
    async with httpx.AsyncClient() as client:
        tasks = [fecthUrl.fetch_one(url) for url in urls]
        responses = await asyncio.gather(*tasks)
        return {
            "count": len(responses),
            "results": responses,
        }