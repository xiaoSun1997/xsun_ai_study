目标：周五：封装 LLMClient 类，统一调用接口


# 一、什么是「LLMClient」

一般在项目里你不会到处写这种散装代码：

    import requests
    
    resp = requests.post(
        "https://api.xxx.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={...}
    )


这样会有几个问题：

- 每个地方都要配置一次 base_url / api_key / model / 超参

- 业务代码混着一堆 HTTP 细节、异常处理、重试逻辑，很乱

- 换模型 / 换服务商时要全项目大规模替换

所以通常会封一层 LLMClient：
    
    一个「大模型客户端」类，负责：
    
    - 统一管理配置（模型名、base_url、api_key、超时、重试…）
    
    - 统一调用入口（比如 .chat()、.complete()）
    
    - 统一做日志 / 监控 / 异常处理 / 重试
    
    - 上层业务只关心：client.chat("帮我写个文案")，不用管底层 HTTP 细节

---
# 二、设计一个最常用的统一接口

我们先定一个最小、实用的 API 目标：

1. 统一入口方法：


    chat(messages=...)：标准 ChatCompletions 风格
    
    complete(prompt=...)：普通「给字符串 prompt、返回字符串」的封装

2. 统一配置：


    model / api_key / base_url
    
    timeout / max_retries

3. 兼容 OpenAI API 风格 / OpenAI 兼容服务

下面这个实现就是为「任意 OpenAI 风格接口」准备的（包括自建的 OpenAI-compatible 服务）。

---
# 三、Python 实战封装 LLMClient

为了通用性，目前业界最流行的是**“OpenAI 兼容格式”**。因为国内的 DeepSeek、月之暗面（Moonshot）、阿里的通义千问，以及本地部署的 Ollama，大多都支持 OpenAI 的 SDK 调用方式。

---
1. 准备工作

安装 OpenAI 的官方库（虽然我们可能调用的不是 OpenAI，但用它的客户端协议）：

    pip install openai python-dotenv

---
2. 代码实现 (llm_client.py)


```python
        import os
        from typing import List, Optional, Dict, Union
        from openai import OpenAI, OpenAIError
        class LLMClient:
            def __init__(self, 
                         api_key: str, 
                         base_url: str = "https://api.openai.com/v1", 
                         model: str = "gpt-3.5-turbo",
                         temperature: float = 0.7):
                """
                初始化 LLM 客户端
                :param api_key: API 密钥
                :param base_url: API 地址 (如果是 OpenAI 用默认，如果是 DeepSeek/Moonshot 等需替换)
                :param model: 模型名称
                :param temperature: 创造性 (0-1)，越高越发散
                """
                self.client = OpenAI(api_key=api_key, base_url=base_url)
                self.model = model
                self.temperature = temperature
        
            def chat(self, 
                     prompt: str, 
                     system_prompt: str = "You are a helpful assistant.",
                     history: Optional[List[Dict]] = None) -> str:
                """
                统一的对话接口
                :param prompt: 用户的当前问题
                :param system_prompt: 系统人设 (System Prompt)
                :param history: 历史对话记录 (可选，用于多轮对话)
                :return: 模型返回的文本内容
                """
                
                # 1. 构建消息列表 (Messages)
                messages = [{"role": "system", "content": system_prompt}]
                
                # 如果有历史记录，追加进去 (Few-shot 也可以放在这里)
                if history:
                    messages.extend(history)
                    
                # 追加当前用户的问题
                messages.append({"role": "user", "content": prompt})
        
                try:
                    # 2. 发起 API 调用
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        temperature=self.temperature,
                        # max_tokens=2000, # 根据需要开启
                    )
                    
                    # 3. 提取并返回核心内容
                    return response.choices[0].message.content.strip()
        
                except OpenAIError as e:
                    # 4. 统一错误处理
                    print(f" LLM 调用失败: {e}")
                    # 在实际生产中，这里可能会写入日志或抛出自定义异常
                    return "抱歉，AI 服务暂时不可用，请稍后再试。"
        
            def set_model(self, new_model: str):
                """动态切换模型"""
                print(f"🔄 切换模型为: {new_model}")
                self.model = new_model
```

---
3. 使用这个 LLMClient

```python
        # main.py
        import os
        from llm_client import LLMClient
        
        # 假设这里配置的是 DeepSeek 或者 Moonshot 的 Key，或者 OpenAI 的
        # 如果是 DeepSeek，base_url 通常是 https://api.deepseek.com
        API_KEY = "sk-xxxxxxxxxxxxxxxxxxxxxxxx" 
        BASE_URL = "https://api.openai.com/v1" # 替换为你的供应商地址
        
        # 1. 实例化客户端
        bot = LLMClient(api_key=API_KEY, base_url=BASE_URL, model="gpt-3.5-turbo")
        
        # --- 场景 A: 普通对话 ---
        print("--- 普通对话 ---")
        ans = bot.chat("用一句话解释什么是量子纠缠")
        print(f"AI: {ans}\n")
        
        # --- 场景 B: 结合 Few-shot CoT (day11) ---
        print("--- Few-shot CoT 推理 ---")
        
        # 定义系统提示词
        sys_prompt = "你是一个逻辑严密的数学助手，请按照示例的思维过程进行回答。"
        
        # 定义 Few-shot 历史 (作为 history 传入)
        few_shot_examples = [
            {"role": "user", "content": "小红有 2 个咕噜币，能换多少硬币？(1咕噜=3咔嚓, 1咔嚓=5硬币, >5咕噜奖励10硬币)"},
            {"role": "assistant", "content": "思维过程：\n1. 2咕噜 * 3 = 6咔嚓\n2. 6咔嚓 * 5 = 30硬币\n3. 2咕噜<5，无奖励。\n答案：30硬币"},
            {"role": "user", "content": "大壮有 10 个咕噜币，能换多少硬币？"},
            {"role": "assistant", "content": "思维过程：\n1. 10咕噜 * 3 = 30咔嚓\n2. 30咔嚓 * 5 = 150硬币\n3. 10咕噜>5，奖励10硬币。\n4. 150+10=160。\n答案：160硬币"}
        ]
        
        # 提问
        user_question = "小明有 6 个咕噜币，能换多少硬币？"
        
        # 调用接口
        final_answer = bot.chat(
            prompt=user_question, 
            system_prompt=sys_prompt, 
            history=few_shot_examples
        )
        
        print(f"AI: {final_answer}")
```
---
4. 流式输出：

4.1 在原本的LLMClient中，添加一个流式输出的接口。
```python
        def chat_stream(self, 
                    prompt: str, 
                    system_prompt: str = "You are a helpful assistant.",
                    history: Optional[List[Dict]] = None) -> Generator[str, None, None]:
        """
        流式对话接口
        :return: 一个生成器，每次 yield 一个字符或片段
        """
        messages = [{"role": "system", "content": system_prompt}]
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": prompt})

        try:
            # 1. 开启 stream=True
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                stream=True  # <--- 关键开关
            )

            # 2. 迭代响应器
            for chunk in response:
                # 在流式模式下，内容在 chunk.choices[0].delta.content 中
                # 普通模式是 message.content，流式是 delta.content
                content = chunk.choices[0].delta.content
                
                # 有些 chunk 可能是空的（比如结束标记），需要过滤
                if content:
                    yield content  # <--- 只要有货，立刻抛给前端

        except OpenAIError as e:
            # 流式报错通常需要 yield 一个错误提示，防止前端死等
            print(f" LLM 流式调用失败: {e}")
            yield f"[Error: {str(e)}]"
```
4.2. 如何调用流式接口 (main.py)
```python        
        import os
        import time
        from llm_client import LLMClient
        
        # 配置你的 Key
        API_KEY = "sk-xxxxxxxxxxxx" 
        BASE_URL = "https://api.openai.com/v1"
        
        bot = LLMClient(api_key=API_KEY, base_url=BASE_URL)
        
        print("--- 开始流式输出测试 ---\n")
        print("AI: ", end="") # 打印头部，end="" 表示不换行
        
        # 1. 获取生成器
        stream = bot.chat_stream("请写一首关于程序员熬夜写代码的五言绝句，要幽默一点。")
        
        # 2. 循环消费生成器
        for chunk in stream:
            # end="" 防止 print 自动换行
            # flush=True 强制立即刷新缓冲区，不然终端可能会等攒够一堆字才显示，就没有打字机效果了
            print(chunk, end="", flush=True) 
            
            # (可选) 模拟网络卡顿，让你看清流式效果
            # time.sleep(0.05) 
        
        print("\n\n--- 结束 ---")
```