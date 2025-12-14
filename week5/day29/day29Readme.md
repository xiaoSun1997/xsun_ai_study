day29：理解Agent 结构（LLM + Tool + Executor）

# 一、Agent定义 简单介绍

- Agent = 能“思考 → 决策 → 调用工具 → 再思考”的 LLM 程序

公式化一点就是：

    Agent = LLM + Tools + Executor


它和「问 → 答」最大的区别是：

    LLM 不再只是生成文本，而是在“做事”

---
# 二、Agent 结构总览
```text

┌─────────────────────┐
│        User         │
└─────────┬───────────┘
          │
┌─────────▼───────────┐
│        Agent        │
│                     │
│  ┌──────────────┐  │
│  │     LLM      │  │  ← 决策中枢（大脑）
│  └──────┬───────┘  │
│         │ Thought   │
│  ┌──────▼───────┐  │
│  │    Tools     │  │  ← 外部能力
│  └──────┬───────┘  │
│         │ Action    │
│  ┌──────▼───────┐  │
│  │   Executor   │  │  ← 执行与控制循环
│  └──────────────┘  │
└─────────────────────┘
```
# 三、Agent 的三个核心组件（重点）
## 1️⃣ LLM（大脑）
在 Agent 中，LLM 不只是“回答问题”

它负责：

- 🤔 思考（Thought）

- 🧭 决策（是否用工具）

- 🧠 规划（先做什么，再做什么）

典型提示词结构（你不写，LangChain 会自动帮你写）：

```text

Thought: 我需要查询时间
Action: get_current_time
Action Input: {}
Observation: 2025-12-13
Thought: 我可以回答了
Final Answer: 现在是 2025-12-13
```

- 👉 Agent 的本质是让 LLM 输出“结构化思考过程”

## 2️⃣ Tool（工具）
Tool 是什么？

    Tool = Agent 能调用的 Python 函数

例如：

    - 搜索
    
    - 计算
    
    - 查数据库
    
    - 调 API
    
    - 查文件
    
    - 调你写的业务函数

在 LangChain 中，一个 Tool 至少包含：

```python
name
description
callable function
```

LLM 通过 description 来判断“该不该用这个工具”

---
## 3️⃣ Executor（执行器）
- Executor 是 Agent 的“循环控制器”

它负责：

- 把 LLM 输出解析成：

    - Thought

    - Action

    - Action Input

- 调用 Tool

- 把结果塞回给 LLM

- 再让 LLM 思考

- 直到得到 Final Answer

可以理解为：

    Executor = Agent 的 runtime

---

# 四、LangChain 中的 Agent 类型（认识不分）

## ✅ ReAct Agent（最重要）

ReAct = Reason + Act

    Thought → Action → Observation → Thought → Final


👉 这是 LangChain 默认 & 最稳定 & 最好理解 的 Agent 结构
后面你学的基本都是它的变体。

---

# 五、从 0 到 1：一个最小 LangChain Agent Demo（Qwen-Plus）
## Step 0：安装依赖

```python

langchain>=0.1.0
langchain-openai
langchain_classic

pip install -r requirements.txt

```
```python
import datetime

from langchain_classic.agents import initialize_agent, AgentType
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="qwen-plus-latest",
    temperature=0,
    api_key="sk-YOUR-API-KEY",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)


@tool
def get_current_time(query: str) -> str:
    """获取当前时间"""
    return str(datetime.datetime.now())


tools = [get_current_time]

agent = initialize_agent(tools,
                         llm,
                         agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                         verbose=True,
                         handle_parsing_errors=True)


def main():
    res = agent.invoke({"现在是什么时间?"})
    print(res["output"])


if __name__ == "__main__":
    main()

#  (day29venv) PS E:\code\xsun_ai_study\week5\day29> python main.py                  
# E:\code\xsun_ai_study\week5\day29\main.py:23: LangChainDeprecationWarning: LangChain agents will continue to be supported, but it is recommended for new use cases to be built with LangGraph. LangGraph offers a more flexible and full-featured framework for building agents, including support for tool-calling, persistence of state, and human-in-the-loop workflows. For details, refer to the [LangGraph documentation](https://langchain-ai.github.io/langgraph/) as well as guides for [Migrating from AgentExecutor](https://python.langchain.com/docs/how_to/migrate_agent/) and LangGraph's [Pre-built ReAct agent](https://langchain-ai.github.io/langgraph/how-tos/create-react-agent/).
#   agent = initialize_agent(tools,
# 
# 
# > Entering new AgentExecutor chain...
# 需要获取当前时间
# Action: get_current_time
# Action Input: {"query": "current time"}
# Observation: 2025-12-14 14:52:24.744312
# Thought:Final Answer: 现在是2025年12月14日14点52分24秒。
# 
# > Finished chain.
# 现在是2025年12月14日14点52分24秒。
```


你会看到完整的 Agent 思考链：

    Thought: 我需要知道当前时间
    Action: get_current_time
    Action Input: {}
    Observation: 2025-12-13 10:32:11
    Thought: 我已经知道时间了
    Final Answer: 现在是 2025-12-13 10:32:11

# 六、这个 Demo 背后发生了什么（非常重要）

组件	|做了什么
---|---
LLM	|Qwen-Plus
Tool |	Python 函数
Agent |	ReAct 推理模板
Executor |	控制调用循环

👉 这是 90% LangChain Agent 的通用骨架

# 七、Agent 和你之前 RAG 的关系

RAG	|Agent
---|---
查资料 → 回答	| 思考 → 决策 → 行动
单次生成	| 多轮内部循环
被动	|主动
无状态或弱状态	|可引入 Memory

👉 Agent 可以“用 RAG 作为工具”