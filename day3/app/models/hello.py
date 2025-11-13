from pydantic import BaseModel

class HelloRequest(BaseModel):
    name: str
    age: int