from typing import Type

from langchain_classic.agents import initialize_agent, AgentType
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field


class CalculatorInput(BaseModel):
    """计算器输入参数定义"""
    num1: float = Field(..., description="第一个数字")
    num2: float = Field(..., description="第二个数字")
    operation: str = Field(
        ...,
        description="要执行的操作: 'add', 'subtract', 'multiply', 'divide'"
    )


class CalculatorTool(BaseTool):
    """Calculator tool."""

    name: str = "Calculator"
    description: str = "执行基础的数学计算，输入两个数字的操作以及操作类型"
    args_schema : Type[BaseModel] = CalculatorInput

    def _run(self, num1: float, num2: float, operation: str) -> str:
        """执行计算"""
        try:
            if operation == "add":
                result = num1 + num2
            elif operation == "subtract":
                result = num1 - num2
            elif operation == "multiply":
                result = num1 * num2
            elif operation == "divide":
                if num2 == 0:
                    return "错误：除数不能为零"
                result = num1 / num2
            else:
                return f"错误：不支持的操作 '{operation}'"

            return f"计算结果: {result}"

        except Exception as e:
            return f"计算错误: {str(e)}"


    async def _arun(self, **kwargs):
        """异步执行（简单调用同步版本）"""
        return self._run(**kwargs)


def main():
    """主函数"""
    tools = [CalculatorTool()]
    llm = ChatOpenAI(model="qwen-plus-latest",
                     api_key="sk-YOUR-KEY",
                     base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                     temperature=0.7)

    agent = initialize_agent(tools,
                             llm,
                             agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
                             verbose=True,
                             handle_parsing_errors=True
                             )
    print("=" * 50)
    print("测试1: 数学计算")
    print("=" * 50)
    result1 = agent.run("计算15.5乘以3.2的结果")
    print(f"结果: {result1}\n")


if __name__ == "__main__":
    main()

    # (day31venv) PS E:\code\xsun_ai_study\week5\day31> python custom_tools_demo.py
    # E:\code\xsun_ai_study\week5\day31\custom_tools_demo.py:61: LangChainDeprecationWarning: LangChain agents will continue to be supported, but it is recommended for new use cases to be built with LangGraph. LangGraph offers a more flexible and full-featured framework for building agents, including support for tool-calling, persistence of state, and human-in-the-loop workflows. For details, refer to the [LangGraph documentation](https://langchain-ai.github.io/langgraph/) as well as guides for [Migrating from AgentExecutor](https://python.langchain.com/docs/how_to/migrate_agent/) and LangGraph's [Pre-built ReAct agent](https://langchain-ai.github.io/langgraph/how-tos/create-react-agent/).
    #   agent = initialize_agent(tools,
    # ==================================================
    # 测试1: 数学计算
    # ==================================================
    # E:\code\xsun_ai_study\week5\day31\custom_tools_demo.py:70: LangChainDeprecationWarning: The method `Chain.run` was deprecated in langchain-classic 0.1.0 and will be removed in 1.0. Use `invoke` instead.
    #   result1 = agent.run("计算15.5乘以3.2的结果")
    #
    #
    # > Entering new AgentExecutor chain...
    # Thought: 需要使用计算器工具来执行乘法运算。
    # Action:
    # ```json
    # {
    #   "action": "Calculator",
    #   "action_input": {"num1": 15.5, "num2": 3.2, "operation": "multiply"}
    # }
    # ```
    # Observation: 计算结果: 49.6
    # Thought:我已得到计算结果。
    # Action:
    # ```json
    # {
    #   "action": "Final Answer",
    #   "action_input": "49.6"
    # }
    # ```
    #
    # > Finished chain.
    # 结果: 49.6