day30: 了解部分内置工具（PythonREPL、Search API）的作用

# 一、 Agent 一定要有「内置工具」的原因

一句话结论：

    LLM ≠ 会做事，Tool 才是“手”

LLM 的天然短板：

能力	    |   问题
--------|---------
数学	|易算错
时间	|不知道现在
实时信息	|不知道
代码执行	|不能

👉 Tool 是在补 LLM 的“物理能力”

---
# 二、PythonREPL 工具（最重要的内置工具之一）
## 1. PythonREPL 是什么？

- PythonREPL = Agent 可调用的 Python 运行环境

你可以把它理解为：

- 一个受控的 exec()

- 一个可以：

    - 计算
    - 处理数据
    - 跑简单脚本
    - 验证中间结果

---
## 2. PythonREPL 能解决什么问题？
❌ LLM 不擅长的事

    27 * 43 / 19 的结果？

✅ Agent + PythonREPL

    27 * 43 / 19

常见用途总结

用途	|示例
----|----
数学	|复杂计算
数据	|列表、dict 处理
验证	|推理中间结果
简单算法 | 排序、统计

⚠️ 不适合：

- 网络请求

- 长时间任务

- 高安全风险代码

## 3. 核心知识点（非常重要）
### 🔹 1. PythonREPL 是 Tool，不是 Notebook

    LLM 用自然语言决定是否调用
    
    Executor 真的执行 Python

### 🔹 2. LLM 写代码 ≠ 你写代码

LLM 写的 Python 往往是：

    一次性
    
    偏脚本
    
    不优雅但能跑

👉 这是预期行为，不是 Bug

### 🔹 3. Tool 描述决定调用成功率

PythonREPL 的 description 会告诉 LLM：

    “当你需要计算或执行 Python 时，用我”

4️⃣ 从 0 到 1 Demo：PythonREPL Agent
Step 0：安装依赖

langchain>=0.1.0
langchain-openai

```python
from langchain_classic.agents import initialize_agent, AgentType
from langchain_experimental.tools import PythonREPLTool
from langchain_openai import ChatOpenAI


llm = ChatOpenAI(
    model="qwen-plus-latest",
    temperature=0,
    api_key="sk-Your-key",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

python_tool = PythonREPLTool()

tools = [python_tool]
agent = initialize_agent(tools,
                         llm,
                         agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                         verbose=True,
                         handle_parsing_errors=True)

def main():
    res = agent.invoke({"计算 (127 * 39 - 58) / 13"})
    print(res["output"])

if __name__ == "__main__":
    main()

# Observation: NameError("name 'py' is not defined")
# Thought:The issue is that the tool expects only the raw Python expression, without any markdown code block syntax or "py" keyword. I'll input just the expression directly.
#                                                                                                                                                                                                                                     
# Action: Python_REPL                                                                                                                                                                                                                 
# Action Input:                                                                                                                                                                                                                       
# (127 * 39 - 58) / 13                                                                                                                                                                                                                
# Observation: 
# Thought:377.0
# Final Answer: 377.0                                                                                                                                                                                                                 
# 
# > Finished chain.
# 377.0
```

# 三、Search API（让 Agent 连接真实世界）
## 1. Search API 是什么？

- Search API = Agent 可用的“外部信息获取工具”

解决的问题：

问题	|LLM
---|---
实时新闻|	❌
最新政策	|❌
实时价格|	❌
当前事件	|❌

## 2. LangChain 常见 Search Tool

Tool	| 特点
---|---
TavilySearch|	官方推荐、简单
SerpAPI|	老牌、强
Bing / Google|	商用

👉 推荐学习阶段用 Tavily

## 3. Tavily Search 的核心认知
Tavily 是什么？

- 专为 LLM 设计的搜索 API

返回的是：

    精简摘要
    
    可读文本
    
    低噪声

Agent 使用方式
```text
Thought: 我需要最新信息
Action: tavily_search
Action Input: 查询内容
Observation: 搜索结果
```


4️⃣ 从 0 到 1 Demo：Search Agent
```python
export TAVILY_API_KEY=your_key
# 1. Tavily API Key 获取方法
# 步骤：
# 
# 访问 Tavily 官网
# 
# 点击 "Get Started" 或 "Sign Up"
# 
# 注册账户（可能需要邮箱验证）
# 
# 登录后进入 Dashboard
# 
# 在 API Keys 部分生成新的 API Key
# 
# 通常有免费额度供试用
```
```python
from langchain_classic.agents import initialize_agent, AgentType
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch

llm = ChatOpenAI(
    model="qwen-plus-latest",
    temperature=0,
    api_key="sk-YOURKEY",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

search_tool = TavilySearch(k=3)
tools = [search_tool]
agent = initialize_agent(tools,
                         llm,
                         agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                         verbose=True,
                         handle_parsing_errors=True)

def main():
    res = agent.invoke({"2024 年诺贝尔和平奖是谁"})
    print(res["output"])

if __name__ == "__main__":
    main()

```