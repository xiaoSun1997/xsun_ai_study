from typing import Type

from langchain_core.tools import BaseTool
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

    name = "Calculator"
    description = "执行基础的数学计算，输入两个数字的操作以及操作类型"
    args_schema = Type[BaseModel] = CalculatorInput

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
