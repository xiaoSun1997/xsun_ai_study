from sys import prefix

from fastapi import APIRouter

from app.models.hello import HelloRequest
from app.services.hello_service import HelloService

router = APIRouter(
    prefix = '/api/v1/hello',
    tags=["day03.demo"]
)

@router.get("/get",summary="get hello")
def hello_get() ->str :
    return HelloService.get_hell()

@router.post("/post",summary="post hello")
def hello_post(request: HelloRequest) ->str :
    return HelloService.post_hell(request)



