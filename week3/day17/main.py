# from langchain_classic.chains.llm import LLMChain
# from langchain_classic.memory import ConversationBufferMemory
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

    # 这段代码定义了一个聊天提示模板 prompt。其中：
    #
    # 系统提示："你是一个虚拟助手，帮助用户解答问题..."
    #
    # 使用 MessagesPlaceholder 动态填充历史消息。
    #
    # "用户的问题是：{question}" 这里的 {question} 是一个占位符，会被实际的问题内容替换。
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
    # ConversationBufferMemory已经弃用，切换成RunnableWithMessageHistory + ChatMessageHistory
    # memory = ConversationBufferMemory(
    #     memory_key="history",
    #     input_key="question",
    #     return_messages=True,
    # )
    base_chain = (
             prompt
            | llm
            | StrOutputParser()
    )

    # RunnableWithMessageHistory 是一个带有会话历史的执行单元：
    #
    # base_chain 是执行的基础任务链。
    #
    # get_session_history 函数用来获取当前会话的历史记录。
    #
    # input_messages_key="question" 和 history_messages_key="history" 指定了输入和历史消息的键名。
    # memory 带有消息历史的链式任务
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