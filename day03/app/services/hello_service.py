from app.models.hello import HelloRequest

class HelloService:
    @staticmethod
    def get_hell() -> str:
        return "hello fastApi (GET)..."

    @staticmethod
    def post_hell( request: HelloRequest) -> str:
        return f"hello fastApi (POST)... name = {request.name}，age = {request.age}"