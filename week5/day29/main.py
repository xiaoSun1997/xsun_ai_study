import datetime

from langchain_classic.agents import initialize_agent, AgentType
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="qwen-plus-latest",
    temperature=0,
    api_key="sk-your-key",
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