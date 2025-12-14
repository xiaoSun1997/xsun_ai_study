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
