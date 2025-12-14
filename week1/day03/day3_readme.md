学习 FastAPI 基础与路径参数

📘 FastAPI 入门与实战指南

使用 Python venv + requirements.txt + FastAPI 项目示例
（含与 Java Spring Boot 架构对比）

目录

    什么是 FastAPI？
    
    FastAPI 常见用法
    
    FastAPI 与 Spring Boot 架构区别
    
    在 Python 中创建虚拟环境（venv）
    
    requirements.txt 管理依赖
    
    完整 FastAPI Demo 项目

    运行项目

1. 什么是 FastAPI？

FastAPI 是一个现代、快速（非常快）、基于 Python 类型注解 的 Web 框架。主要特点：

    🚀 性能极高（比 Flask 快很多）
    
    🧠 自动类型校验（基于 Pydantic）
    
    ⚙️ 自动生成 API 文档（Swagger / ReDoc）
    
    ✨ 写法简洁、上手极快
    
    🧩 天然支持异步 async/await

2. FastAPI 常见用法
2.1 基本 GET 接口


    @app.get("/")
    def home():
        return {"message": "Hello FastAPI!"}
    
    2.2 路径参数
    @app.get("/items/{item_id}")
    def get_item(item_id: int):
        return {"item_id": item_id}


FastAPI 自动做类型转换与校验（例如 item_id 必须是 int）

2.3 查询参数

    
    @app.get("/search")
    def search(keyword: str | None = None, limit: int = 10):
        return {"keyword": keyword, "limit": limit}
    //keyword: str | None = None 代表：keyword 是可选的，可以不传，不传时为 None
    //limit: int = 10 代表：limit 是可选的，不传时使用默认值 10
limit: int = 10 代表：limit 是可选的，不传时使用默认值 10
2.4 POST 接收 JSON（使用 Pydantic）


    class Item(BaseModel):
        name: str
        price: float
    
    @app.post("/items")
    def create_item(item: Item):
        return {"status": "ok", "item": item}


FastAPI 自动：

    校验请求体
    
    解析 JSON
    
    构造 Item 对象

2.5 常见 HTTP 方法

    @app.get("/users")
    @app.post("/users")
    @app.put("/users/{id}")
    @app.delete("/users/{id}")

2.6 自动生成文档

    Swagger：http://127.0.0.1:8000/docs
    
    ReDoc：http://127.0.0.1:8000/redoc

## 第一个fastAPI项目demo
1. 进入 day3 目录 & 准备虚拟环境（推荐）
    
        cd day3

# 1. 创建虚拟环境 venv
    python -m venv venv

# 2. 激活虚拟环境（Windows PowerShell）
    .\venv\Scripts\Activate.ps1
# macOS/Linux:
    # source venv/bin/activate

# 3. 安装 FastAPI 和 Uvicorn
    pip install fastapi "uvicorn[standard]"


生成 requirements.txt（可选但推荐）：

    pip freeze > requirements.txt

2. 创建项目目录结构

在 day3 目录下执行：

    mkdir app
    mkdir app/api
    mkdir app/api/v1
    mkdir app/models
    mkdir app/services


现在的结构大概是：

    day3/
    ├── venv/
    ├── app/
    │   ├── api/
    │   │   └── v1/
    │   ├── models/
    │   └── services/
    └── requirements.txt  (可选)


然后创建必要的 __init__.py（把这些目录变成 Python 包）：

# Windows
    echo. > app/__init__.py
    echo. > app/api/__init__.py
    echo. > app/api/v1/__init__.py
    echo. > app/models/__init__.py
    echo. > app/services/__init__.py

3. 定义请求体 Model（app/models/hello.py）

POST 请求要用单独的 model，这里我们建一个最简单的 HelloRequest。

在 app/models/hello.py 写入：

    from pydantic import BaseModel
    
    
    class HelloRequest(BaseModel):
        name: str


这个 model 表示：POST 请求体必须是 JSON，且包含一个字符串字段 name。

4. 编写 Service 层（app/services/hello_service.py）


    Service 负责处理业务逻辑。
    Controller 只负责接收请求、调用 Service。

在 app/services/hello_service.py 写入：

    from app.models.hello import HelloRequest
    
    
    class HelloService:
        @staticmethod
        def get_hello() -> str:
            """
            处理 GET 请求的业务逻辑
            """
            return "hello fastApi (GET)..."
    
        @staticmethod
        def post_hello(req: HelloRequest) -> str:
            """
            处理 POST 请求的业务逻辑
            """
            # 你如果想简单一点，也可以不使用 req.name，直接返回固定字符串
            return f"hello fastApi (POST)... name = {req.name}"
            # 如果你想严格按照题意，只返回固定字符串，也可以这样：
            # return "hello fastApi (POST)..."

5. 编写 Controller / Router 层（app/api/v1/hello_controller.py）

这一层相当于 Spring Boot 中的 Controller：

    定义 URL、请求方法（GET/POST）
    
    调用 Service，返回结果

在 app/api/v1/hello_controller.py 写入：

    from fastapi import APIRouter
    from app.models.hello import HelloRequest
    from app.services.hello_service import HelloService
    
    router = APIRouter(
        prefix="/api/v1/hello",   # 路由前缀
        tags=["Hello API"],       # 在文档里的分组名字
    )
    
    
    @router.get("", summary="Hello GET 接口")
    def hello_get() -> str:
        """
        GET 接口：返回 hello fastApi (GET)...
        """
        return HelloService.get_hello()
    
    
    @router.post("", summary="Hello POST 接口")
    def hello_post(body: HelloRequest) -> str:
        """
        POST 接口：接收一个 JSON 请求体，并返回字符串
        """
        return HelloService.post_hello(body)


注意这里把两个接口都挂在 /api/v1/hello 上：

    GET /api/v1/hello
    
    POST /api/v1/hello

6. 汇总路由（app/api/init.py）

这一层相当于「API 入口」，统一把 v1 的所有 router 收集起来，提供给 main 应用挂载。

在 app/api/__init__.py 中写入：
    
    from fastapi import APIRouter
    from app.api.v1.hello_controller import router as hello_router
    
    api_router = APIRouter()
    
    # 在这里不断 include 其他模块的 router
    api_router.include_router(hello_router)


以后你有别的模块，比如 user_controller.py，也可以在这里再 include_router 一次。

7. 创建应用入口 main.py（app/main.py）

这个文件类似 Spring Boot 的 Application 启动类：
创建 FastAPI 实例、挂载所有 router。

在 app/main.py 写入：
    
    from fastapi import FastAPI
    from app.api import api_router
    
    
    def create_app() -> FastAPI:
        app = FastAPI(
            title="Day3 FastAPI Demo",
            description="A demo project with controller & service layers",
            version="1.0.0",
        )
    
        # 挂载所有 API 路由
        app.include_router(api_router)
    
        return app


# 供 uvicorn 使用的全局 app 实例
app = create_app()

8. 当前项目完整结构检查

此时 day3 目录结构应大致为：
    
    day3/
    ├── venv/
    ├── app/
    │   ├── __init__.py
    │   ├── main.py
    │   ├── api/
    │   │   ├── __init__.py
    │   │   └── v1/
    │   │       ├── __init__.py
    │   │       └── hello_controller.py
    │   ├── models/
    │   │   ├── __init__.py
    │   │   └── hello.py
    │   └── services/
    │       ├── __init__.py
    │       └── hello_service.py
    └── requirements.txt   (可选)

9. 启动项目

确保你在 day3 根目录，并且 venv 已激活：

    uvicorn app.main:app --reload


看到类似日志就成功了：

    INFO:     Uvicorn running on http://127.0.0.1:8000

10. 测试两个接口
1）GET 接口


    URL：http://127.0.0.1:8000/api/v1/hello

方法：GET

预期返回（示例）：

    "hello fastApi (GET)..."


（因为返回的是纯字符串，FastAPI 会直接返回字符串）

2）POST 接口

    URL：http://127.0.0.1:8000/api/v1/hello

方法：POST

Body（JSON）示例：

    {
      "name": "dawn"
    }


可能返回（根据你在 service 中写的逻辑）：

    "hello fastApi (POST)... name = dawn"


或者你如果改成固定字符串，就会直接返回：

    "hello fastApi (POST)..."

11. Swagger 文档查看

浏览器访问：

    接口文档：http://127.0.0.1:8000/docs
    
    备用文档：http://127.0.0.1:8000/redoc

你会看到 Hello API 这一组下面有两个接口：GET / POST。

---
上述demo的几个问题回答：
## 1. 每个目录下都要有 __init__.py 吗？有什么用？
1.1 作用是什么？

__init__.py 的作用是：把一个目录标记为 Python 包（package）。

有了它之后，你才能：

    from app.models.hello import HelloRequest


这个 app.models.hello 就是：

    app：一个包（有 app/__init__.py）
    
    models：子包（有 app/models/__init__.py）
    
    hello：模块（hello.py 文件）

可以理解为：没有 __init__.py，Python 可能就把这个目录当普通文件夹，而不是“可以用点号导入的包”。

### 1.2 现在是不是必须要有？

从 Python 3.3 开始有“namespace package”的概念，一些情况下可以不写 __init__.py 也能导入。

但是在实际项目中（尤其是：
    
    需要清晰包层级结构
    
    配合 IDE（PyCharm 等）
    
    做大项目 / 多层结构

👉 依然推荐所有包目录加上 __init__.py，比较省心。

### 1.3 目录里还有其他 .py 文件要不要 __init__.py？
    
    目录里有多少 .py 文件 跟需不需要 __init__.py 没关系。
    
    是否需要 __init__.py 取决于：这个目录是不是要当成一个“包”来用（被 import）。

举例：

    app/
    ├── __init__.py        # app 是包
    ├── main.py
    ├── models/
    │   ├── __init__.py    # models 是子包
    │   └── hello.py
    └── utils/
        └── string_utils.py  # 如果你希望 from app.utils import string_utils，就建议也有 __init__.py
    

如果你只是随手放了一些脚本，从不 import，那可以不管；但作为项目结构，统一加上 __init__.py 是好习惯。

