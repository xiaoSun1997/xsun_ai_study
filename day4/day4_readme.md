今日目标：理解 async/await 异步机制


# 一、Python async / await 是什么？
## 1.1 先说结论
    
    async 用来 定义一个“协程函数”（coroutine function），它不会立刻执行，而是返回一个“协程对象”。
    
    await 用来 在协程内部等待另一个异步操作完成，在等待期间可以把执行权让给事件循环（event loop），去干别的事。

一句话：

    async/await 是 Python 用来做“协程并发”的语法糖，主要用来优化 IO 密集型任务（网络请求、磁盘 IO 等），不是用来跑多核 CPU 密集计算的。

## 1.2 和多线程、多进程的关系？

    多线程/多进程：操作系统级别的并发，切换开销较大。
    
    async/await：单线程内的“协作式并发”，本质是一个线程里跑一个事件循环（event loop），在 IO 等待时主动“让出执行权”。

关键点：
    
    async/await 不会“自动让出执行权”，只有遇到 await 某个异步操作时才会挂起当前协程。
    
    没有 await 的 async def，其实就是一个“写成 async 但像同步的一样阻塞的函数”。

## 1.3 三个核心概念

1. 协程函数：用 async def 定义的函数。

    
    async def foo():
        return 42

调用 foo() 不会立刻执行，而是返回一个 协程对象。

2. 协程对象：需要被事件循环调度才能真正执行，一般用 asyncio.run() 或在别的协程里 await 它。

3. 事件循环（event loop）：调度和执行协程的“调度器”，负责让各个协程在 IO 等待期间切换。

## 1.4 await 到底在干嘛？

    async def foo():
        print("start")
        await asyncio.sleep(1)  # 模拟一个耗时 IO
        print("end")


1. await asyncio.sleep(1) 这行的意思是：

    
    告诉事件循环：我这里需要等待 1 秒，你可以先去执行别的协程，等 1 秒到了再回来继续执行我。

2. 如果没有别的协程，那就是一个简单的“异步 sleep”，但仍然不会阻塞整个线程（事件循环还能响应其他事情）。

## 1.5 适用于什么场景？

✅ 非常适合：

    很多 HTTP 请求：爬虫、调用第三方 API
    
    数据库 IO
    
    文件 IO、大量网络连接（聊天服务、Web 框架等）

❌ 不适合单纯 CPU 算法加速，例如：

    大量数学计算
    
    加密、压缩、图像处理
    
    CPU 密集的任务要用：多进程 / C 扩展 / Numba / Cython 等方式。

# 二、一个完整的 async/await demo（含对比）

我们写一个最简单的场景：

    模拟 同步执行 5 个“网络请求”（用 time.sleep）
    
    然后用 异步执行 5 个“网络请求”（用 asyncio.sleep）

对比一下耗时差别

注意：这里用 sleep 只是模拟 IO 等待，真实情况可以换成 requests.get() vs aiohttp 之类。

## 2.1 demo 目录结构（你可以放在 day3 或任意目录）
    async_demo/
    └── main.py

2.2 完整代码：main.py
    
    import time
    import asyncio


---
## 同步版本：模拟 5 个网络请求

---
    def sync_task(n: int):
        print(f"[sync] start task {n}")
        time.sleep(1)  # 模拟耗时 IO
        print(f"[sync] end task {n}")
    
    
    def run_sync():
        start = time.time()
        for i in range(5):
            sync_task(i)
        end = time.time()
        print(f"[sync] total time: {end - start:.2f} seconds")


---
## 异步版本：模拟 5 个网络请求

---
    async def async_task(n: int):
        print(f"[async] start task {n}")
        # asyncio.sleep 是一个真正的“可等待对象”（异步 IO）
        await asyncio.sleep(1)
        print(f"[async] end task {n}")
    
    
    async def run_async():
        start = time.time()
    
        # 创建 5 个协程任务
        tasks = [asyncio.create_task(async_task(i)) for i in range(5)]
    
        # 等待所有任务完成
        await asyncio.gather(*tasks)
    
        end = time.time()
        print(f"[async] total time: {end - start:.2f} seconds")


---
## 主入口

---

    if __name__ == "__main__":
        print("=== 同步版本 ===")
        run_sync()
    
        print("\n=== 异步版本 ===")
        asyncio.run(run_async())

2.3 如何运行

在终端中：

    python main.py


你大概会看到类似输出（大致示意）：

=== 同步版本 ===

    [sync] start task 0
    [sync] end task 0
    [sync] start task 1
    [sync] end task 1
    [sync] start task 2
    [sync] end task 2
    [sync] start task 3
    [sync] end task 3
    [sync] start task 4
    [sync] end task 4
    [sync] total time: 5.00 seconds

=== 异步版本 ===

    [async] start task 0
    [async] start task 1
    [async] start task 2
    [async] start task 3
    [async] start task 4
    [async] end task 0
    [async] end task 1
    [async] end task 2
    [async] end task 3
    [async] end task 4
    [async] total time: 1.00 seconds


解释：

    同步版：5 个任务串行执行，每个 1 秒，总共 ≈ 5 秒。
    
    异步版：5 个任务并发执行，等待时间被重叠，总共 ≈ 1 秒。

三、顺带说一下：在 FastAPI 里 async/await 怎么用？

其实你已经在用 FastAPI 了，很容易结合：
    
    from fastapi import FastAPI
    import asyncio
    
    app = FastAPI()
    
    
    async def fake_io(n: int):
        await asyncio.sleep(1)
        return f"task {n} done"
    
    
    @app.get("/async-demo")
    async def async_demo():
        tasks = [asyncio.create_task(fake_io(i)) for i in range(5)]
        results = await asyncio.gather(*tasks)
        return {"results": results}


这里的关键点：
    
    FastAPI 的接口函数如果是 async def：
    
    就可以在里面 await 异步 IO
    
    FastAPI 会接入事件循环，帮你调度

四、再压缩成几句记忆点

    async def 定义 协程函数，调用时不会立刻执行，而是返回协程对象。
    
    await 只能在 async def 里面用，用来“等待一个异步任务完成并把执行权让给 event loop”。
    
    异步主要优化 IO 密集 场景，不是为 CPU 算力提速而设计。
    
    asyncio.run() 是启动异步世界的一个入口。
    
    多个协程并发执行常用 asyncio.gather() 或 asyncio.create_task()。
---
# async/await + asyncio 和 Java 的 CompletableFuture 对比
1. 🟢 相似点： 都是在解决“异步任务 + 组合 + 等待结果”的问题，避免传统回调地狱。

2. 🔴 核心区别：
    

    Python async/await 通常是单线程 + 事件循环 + 协程并发（协作式）
    Java CompletableFuture 通常是线程池 + 真实多线程并发（抢占式）
---
## 二、相似点：为什么你会本能地把它们联想到一起？

---
### 1. 都是在表示“一个未来才会有结果的任务”

Python：协程函数 + Task

    async def foo():
        ...
        return 42
    
    task = asyncio.create_task(foo())   # 表示“未来会有个结果”
    result = await task


Java：CompletableFuture

    CompletableFuture<Integer> future =
        CompletableFuture.supplyAsync(() -> 42);
    
    Integer result = future.join();  // 或 get()


相似点：都有一个“Future”概念：现在拿到的是一个“占位符”，真正结果之后才会填充进来。

---

### 2. 都支持并发执行多个任务并等待全部完成

Python：asyncio.gather
    
    tasks = [asyncio.create_task(job(i)) for i in range(5)]
    results = await asyncio.gather(*tasks)


Java：CompletableFuture.allOf
    
    CompletableFuture<?>[] futures = ...;
    CompletableFuture.allOf(futures).join();


相似点：都有“多个异步任务 → 全部完成后再继续”的组合操作。

---
### 3. 都支持结果转换、链式调用

Python：await 之后继续写逻辑，其实就是链式：
    
    data = await fetch_data()
    processed = process_data(data)


Java：显式链式 API：

    CompletableFuture.supplyAsync(this::fetchData)
                     .thenApply(this::processData)
                     .thenAccept(this::save);


相似点：都是在做“异步结果出来后再干啥”的链式组合，只是：

Python 用语法糖：await + 普通顺序写法

Java 用方法链：thenApply/thenCompose/thenAccept 等

---

### 4. 都有异常传递 & 取消机制

Python：try/except 包裹 await，task.cancel()

Java：异常包装进 CompletionException，future.cancel(true)

本质都支持：

    异步任务出错 → 流到调用方
    
    可以尝试中断/取消未完成的任务

---
## 三、核心差异：本质模型完全不同

---
### 差异 1：并发模型不同（协程 vs 多线程）
Python async/await + asyncio

    通常：单线程（一个 event loop 线程）
    
    所有 async def 协程在一个事件循环里“轮流执行”
    
    只有遇到 await 某个“可等待对象”（比如网络 IO）时才会挂起当前协程，让出执行权
    
    并发是“协作式”的：协程自己通过 await 让出 CPU

Java CompletableFuture

    底层通常依赖 Executor / ForkJoinPool / 线程池
    
    每个 supplyAsync/runAsync 对应的是提交任务到线程池
    
    真正由 多个 OS 线程 并发执行（只要线程池大小 > 1）
    
    并发是“抢占式”的：线程由操作系统调度，不需要用户显式“让出”

👉 结论：

    Python async/await：默认不等于多线程
    
    Java CompletableFuture：通常是跑在多线程上（线程池），但 CompletableFuture 本身不是“线程”，而是“结果容器 + 回调机制”。

---
### 差异 2：语法 vs 库 API

Python：async/await 是语言级语法，跟 for/if 一样一等公民。

    async def main():
        data = await fetch()
        ...


Java：CompletableFuture 是类库（java.util.concurrent），靠泛型 + lambda 实现。

    CompletableFuture.supplyAsync(this::fetch)
                     .thenApply(this::process);


这也导致：

    Python 写异步代码看起来更像“同步代码”；
    
    Java 则明显呈现出“链式回调风格”。

---
### 差异 3：调度核心不同（事件循环 vs 线程池）

Python async：中心是 asyncio 事件循环

    asyncio.run(main())     # 启动 event loop


Java CompletableFuture：中心是 Executor / 线程池

    CompletableFuture.supplyAsync(task, executor);


这意味着：

    Python 并发能力受限于 单线程 + GIL，适合 IO 密集
    
    Java 可以真正利用多核 CPU，对 CPU 计算任务 也比较友好（线程池开多核执行）

---

### 差异 4：应用场景重心略有不同

Python async：

    更偏向：高并发 IO（网络、数据库、文件），例如：
    
    HTTP API 调用、爬虫
    
    FastAPI / aiohttp 之类 Web 服务
    
    CPU 密集的任务依旧推荐：多进程、C 扩展等

Java CompletableFuture：

    既可以用于 IO 异步调用
    
    也可以用来把耗时 CPU 计算扔进线程池执行，避免阻塞主线程
    
    当然，Python 也可以 loop.run_in_executor 把 CPU 任务扔到线程池，Java 也可以使用 async IO 框架，总体上更灵活。

---

### 差异 5：组合与错误处理体验上差异

Python async/await：

    async def main():
        try:
            res1 = await job1()
            res2 = await job2(res1)
        except Exception as e:
            ...


异常传播 + 捕获和同步写法几乎一模一样

asyncio.gather 可以 return_exceptions=True 控制行为

Java CompletableFuture：

    CompletableFuture.supplyAsync(this::job1)
        .thenCompose(res1 -> CompletableFuture.supplyAsync(() -> job2(res1)))
        .exceptionally(e -> {
            ...
            return fallback;
        });
    

需要通过 exceptionally, handle, whenComplete 等处理异常

异常通常被包在 CompletionException 里，需要 getCause()

体验上：

    Python async 更像“同步 + try/except”
    
    Java CF 更像“回调链 + 异常装饰器”


| 维度 | Python async/await + asyncio | Java CompletableFuture |
|------|------------------------------|-------------------------|
| **并发模型** | 单线程协程（事件循环） | 通常基于线程池的多线程 |
| **语法/库** | 语言级语法（`async`/`await`） | 类库 API（`CompletableFuture`） |
| **调度核心** | `asyncio` event loop | Executor / ForkJoinPool |
| **典型用途** | 高并发 IO、异步 Web | 异步 IO、后台计算、链式处理 |
| **多核利用** | 默认没多核（除非自己用线程/进程） | 可以利用多核（线程池） |
| **组合方式** | `await` + `asyncio.gather` | `thenApply`/`thenCompose` + `allOf`/`anyOf` |
| **异常处理** | `try`/`except` + `await` | `exceptionally`/`handle`/`whenComplete` |
| **本体是不是线程** | 不是 | 也不是 |

