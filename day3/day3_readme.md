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
