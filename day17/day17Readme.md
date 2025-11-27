记忆机制（Memory）

# Memory 的基本概念

1. 记忆的作用：

    - 通过记忆，模型能够“记住”之前的对话内容、用户的偏好、历史问题等信息。

    - 这使得模型可以根据上下文调整回答，而不仅仅是基于单一输入生成响应。

    - 记忆对于构建智能助手、聊天机器人、问答系统等场景非常有用。

2. 类型：

    - 简单记忆（Simple Memory）： 适用于存储少量上下文信息。

    - 长期记忆（Long-Term Memory）： 适用于更复杂的记忆场景，可以跨对话保存大量的信息。

    - 短期记忆： 保留在当前对话期间有效的上下文，但一旦对话结束，记忆会被清除。

3. Memory 组件：

    - LangChain 提供了多个记忆组件来管理对话状态，例如 ConversationBufferMemory（记录对话的输入和输出）和 ConversationSummaryMemory（基于摘要记录对话内容）。

4. 工作原理：

    - 在每次交互中，模型会基于当前的输入和之前的记忆生成回答。

    - 当对话结束时，记忆会根据预设的策略决定是否继续保留。

---

# 如何使用 Memory

在 LangChain 中，你可以使用 Memory 来跟踪与用户的对话历史，并在后续的交互中结合之前的对话信息来生成更合适的回答。

常见 Memory 类型：(已Discard)

    ConversationBufferMemory：适用于简单的对话记忆，可以保存对话中的所有消息（用户的输入和模型的输出）。
    
    ConversationSummaryMemory：会定期总结对话内容，以节省存储空间。
    

---

## ChatMessageHistory：

    保存一段对话的所有消息（通常是一个 session 的消息）。

- 内存要在多个会话中复用（session1 / session2）

- 需要实现“带历史上下文的连续对话”

- 新版 LangChain 不再推荐 ConversationBufferMemory 的老方式。所以统一改用 MessageHistory + RunnableWithMessageHistory。

```python
# 让不同 session 拥有独立历史记录。
def get_session_history(session_id):
    if session_id not in SESSION_STORE:
        SESSION_STORE[session_id] = ChatMessageHistory()
    return SESSION_STORE[session_id]

```
## RunnableWithMessageHistory:
- RunnableWithMessageHistory 是 LangChain 新版会话记忆系统的核心。
- 管理整个链的输入、输出与历史记录之间的交互。

旧版 Memory	|新版 RunnableWithMessageHistory
---|---
只能用于 LLMChain|	可用于任何 Runnable（LLM、RAG、ToolChain、Agent 等）
与 LangChain 新架构兼容性差	|与 LCEL 完全兼容
手动插历史	|自动注入/追加历史
只能用于 prompt	|可作用于整个链路

RunnableWithMessageHistory 的工作流程

假设调用：

    chain.invoke(
        {"question": "你好"},
        config={"configurable": {"session_id": "default"}}
    )


整个过程如下：

① 获取历史记录

调用：

    history = get_session_history("default")


假如是第一次调用，history 为空。

② 组织 prompt

Runnable 将：

    历史记录 → 注入 MessagesPlaceholder("history")

当前输入 question → 注入 prompt

最终 prompt 会长这样：

    [system] 你是助手...
    [history]（空）
    [human] 用户的问题是：你好

③ 执行 base_chain

即：

    prompt → llm → StrOutputParser


得到模型输出，例如：

    "你好，我是你的助手"

④ 把新消息写入 history

将用户新输入和 AI 新回复追加到 ChatMessageHistory：

    User: 你好
    AI: 你好，我是你的助手

⑤ 返回最终结果给用户
# DEMO


## 步骤：

1. 使用 ConversationBufferMemory 来存储和更新对话记录。

2. 创建一个简单的 LLMChain，结合记忆来实现对话功能。

## 代码实现：
```python

from typing import Dict

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables import RunnablePassthrough, RunnableWithMessageHistory
from langchain_openai import ChatOpenAI

SESSION_STORE: Dict[str, ChatMessageHistory] = {}


def get_session_history(session_id) -> ChatMessageHistory:
    if session_id not in SESSION_STORE:
        SESSION_STORE[session_id] = ChatMessageHistory()
    return SESSION_STORE[session_id]


def build_chain():
    llm = ChatOpenAI(
        model="qwen-plus",
        api_key="sk-YourKey",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "你是一个虚拟助手，帮助用户解答问题。"
                "你需要根据用户的历史对话和当前问题来回答，并用简体中文回答。",
            ),
            # 这里放历史对话，由 RunnableWithMessageHistory 自动填充
            MessagesPlaceholder(variable_name="history"),
            ("human", "用户的问题是：{question}"),
        ]
    )

    base_chain = (
             prompt
            | llm
            | StrOutputParser()
    )

    memory = RunnableWithMessageHistory(
        base_chain,
        get_session_history,
        input_messages_key="question",
        history_messages_key="history",
    )
    return memory


if __name__ == "__main__":
    chain = build_chain()
    session_id = "default_session"

    while True:
        question = input("请输入问题：")
        if question == "q":
            break
        result = chain.invoke({"question": question},
                              config={"configurable": {"session_id": session_id}}
        )
        print(result)

# 请输入问题：今天天气怎么样
# 要了解今天的天气情况，请告诉我您所在的城市或地区，这样我可以为您提供准确的天气信息。
# 请输入问题：苏州
# 今天苏州的天气情况如下：
# 
# 目前气温约为20℃，多云，空气质量良好。白天天气较为舒适，适合外出活动；但早晚温差较大，请注意适时增减衣物。未来几天预计会有短暂降雨，建议随身携带雨具。
# 
# 如需更详细的天气预报（如具体时间段、风力、湿度等），可告知我具体需求。
# 请输入问题：明天呢
# 明天苏州的天气预报如下：
# 
# 预计明天（具体日期根据当前时间）阴转小雨，气温在18℃～23℃之间，东北风3-4级。有降水可能，建议出门携带雨具，注意路面湿滑。空气湿度较大，体感较为凉爽。
# 
# 请注意：天气预报存在一定不确定性，建议出行前查看实时更新信息。
# 
# 如需更详细的时段预报（如上午、夜间等），也可以告诉我。
# 请输入问题：q
```
下述已经废弃：

```python


# file: demo_memory.py

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.memory import ConversationBufferMemory
from langchain_core.chains import LLMChain

def build_chain():
    # 1. 初始化 LLM（语言模型）
    llm = ChatOpenAI(
        model="gpt-4o-mini",   # 你可以选择不同的模型
        temperature=0.7,       # 控制生成的创意程度，值越大，生成的内容越丰富
    )

    # 2. 定义对话的 Prompt 模板
    prompt = ChatPromptTemplate.from_template(
        """
你是一个虚拟助手，帮助用户解答问题。你需要根据用户的问题来提供准确的回答。
记住，用户的历史对话会影响你接下来的回答。

用户说：{history}
用户的问题是：{question}
助手回答：
"""
    )

    # 3. 使用 ConversationBufferMemory 来保存对话历史
    memory = ConversationBufferMemory(memory_key="history", return_messages=True)

    # 4. 将 Prompt 模板与 LLM 结合形成 LLMChain
    chain = LLMChain(prompt=prompt, llm=llm, memory=memory)

    return chain

def main():
    # 1. 获取构建好的链（Chain）
    chain = build_chain()

    print("虚拟助手启动，输入 'exit' 来退出对话。")

    while True:
        # 2. 获取用户输入
        user_input = input("\n你：")

        if user_input.lower() == "exit":
            print("再见！")
            break

        # 3. 调用 Chain 来生成回答，并更新记忆
        result = chain.invoke({"question": user_input})

        # 4. 输出模型的回答
        print("\n助手：", result)

if __name__ == "__main__":
    main()
```
