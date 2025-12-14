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