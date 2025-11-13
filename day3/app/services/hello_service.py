from day3.app.models.hello import HelloRequest

class HelloService:
    def get_hell(self) -> str:
        return "hello fastApi (GET)..."

    def post_hell(self, request: HelloRequest) -> str:
        return "hello fastApi (POST)... name = {req.name}"