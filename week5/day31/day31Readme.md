# 自定义Tool函数详解与实践
## 1. 什么是自定义Tool函数？
### 1.1 核心概念
自定义Tool函数是LangChain中允许开发者根据特定需求创建的工具函数，这些函数可以被Agent调用以执行特定任务。它们是扩展Agent能力的关键机制，让LLM能够与外部系统、API、数据库或自定义逻辑进行交互。

### 1.2 Tool函数的基本结构
一个完整的Tool函数包含三个核心要素：

    函数实现：实际的Python函数逻辑
    
    工具描述：自然语言描述，帮助LLM理解何时使用该工具
    
    输入参数：明确定义的输入参数和模式

### 1.3 为什么需要自定义Tool函数？

    特定领域需求：内置工具无法满足专业领域需求
    
    私有系统集成：连接企业内部系统、数据库或API
    
    定制化逻辑：实现特定的业务逻辑或计算
    
    安全控制：限制LLM对某些资源的访问权限

## 2. Tool函数的组成要素

### 2.1 必需组件
```python
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

# 1. 输入Schema（定义工具接受的参数）
class CalculatorInput(BaseModel):
    """计算器输入参数"""
    a: float = Field(..., description="第一个数字")
    b: float = Field(..., description="第二个数字")
    operation: str = Field(..., description="运算符: add, subtract, multiply, divide")

# 2. 工具类（继承BaseTool）
class CustomCalculatorTool(BaseTool):
    name = "custom_calculator"
    description = "执行基本的数学计算"
    args_schema = CalculatorInput
    
    def _run(self, a: float, b: float, operation: str) -> str:
        """工具的核心执行逻辑"""
        # 实现具体功能
        pass
    
    async def _arun(self, a: float, b: float, operation: str) -> str:
        """异步版本（可选）"""
        pass
```

### 2.2 关键属性说明
属性	| 说明	             |重要性
--|-----------------|--
name	| 工具的唯一标识符	       |⭐⭐⭐⭐⭐
description	| 帮助LLM理解工具用途的描述	 |⭐⭐⭐⭐⭐
args_schema | 	定义输入参数的结构      |	⭐⭐⭐⭐
_run()	| 同步执行方法| 	⭐⭐⭐⭐⭐    
_arun()	| 异步执行方法（可选）|	⭐⭐⭐

## 3. 创建自定义Tool的完整流程
### 3.1 从0到1的完整示例
```python

# custom_tools_demo.py
import os
from typing import Optional, Type
from datetime import datetime

# LangChain相关导入
from langchain.tools import BaseTool, Tool
from langchain.agents import initialize_agent, AgentType
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

# 设置API密钥（确保已设置环境变量）
os.environ["OPENAI_API_KEY"] = "your-api-key-here"

# ==================== 示例1：基础计算器工具 ====================

class CalculatorInput(BaseModel):
    """计算器输入参数定义"""
    num1: float = Field(..., description="第一个数字")
    num2: float = Field(..., description="第二个数字")
    operation: str = Field(
        ..., 
        description="要执行的操作: 'add', 'subtract', 'multiply', 'divide'"
    )

class CalculatorTool(BaseTool):
    """自定义计算器工具"""
    name = "calculator"
    description = "执行基本的数学运算。输入两个数字和操作类型。"
    args_schema: Type[BaseModel] = CalculatorInput
    
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

# ==================== 示例2：简易天气查询工具 ====================

class WeatherInput(BaseModel):
    """天气查询输入参数"""
    city: str = Field(..., description="城市名称，例如: '北京', '上海'")
    date: Optional[str] = Field(
        None, 
        description="查询日期，格式: 'YYYY-MM-DD'，默认为今天"
    )

class WeatherTool(BaseTool):
    """模拟天气查询工具（真实场景可接入天气API）"""
    name = "weather_checker"
    description = "查询指定城市的天气信息。需要提供城市名称和可选日期。"
    args_schema: Type[BaseModel] = WeatherInput
    
    # 模拟天气数据（真实应用中应调用API）
    _mock_weather_data = {
        "北京": {"today": "晴，15-25°C", "tomorrow": "多云，16-24°C"},
        "上海": {"today": "小雨，18-22°C", "tomorrow": "阴，19-23°C"},
        "广州": {"today": "雷阵雨，24-30°C", "tomorrow": "多云，25-31°C"},
    }
    
    def _run(self, city: str, date: Optional[str] = None) -> str:
        """查询天气"""
        if date is None:
            date_key = "today"
            date_str = "今天"
        elif date == datetime.today().strftime('%Y-%m-%d'):
            date_key = "today"
            date_str = "今天"
        else:
            date_key = "tomorrow"
            date_str = "明天"
        
        if city in self._mock_weather_data:
            weather = self._mock_weather_data[city][date_key]
            return f"{city}{date_str}天气: {weather}"
        else:
            available_cities = ", ".join(self._mock_weather_data.keys())
            return f"抱歉，未找到{city}的天气数据。可用城市: {available_cities}"
    
    async def _arun(self, **kwargs):
        return self._run(**kwargs)

# ==================== 示例3：使用装饰器创建简单工具 ====================

from langchain.tools import tool

@tool
def text_length_counter(text: str) -> str:
    """计算输入文本的长度（字符数和单词数）"""
    char_count = len(text)
    word_count = len(text.split())
    return f"文本分析结果:\n字符数: {char_count}\n单词数: {word_count}"

# ==================== 示例4：文件内容读取工具 ====================

class FileReadInput(BaseModel):
    """文件读取输入参数"""
    filepath: str = Field(..., description="要读取的文件路径")
    max_lines: Optional[int] = Field(
        10, 
        description="最大读取行数，默认为10"
    )

class FileReadTool(BaseTool):
    """安全地读取本地文件内容"""
    name = "file_reader"
    description = "读取本地文本文件的内容。需要提供文件路径。"
    args_schema: Type[BaseModel] = FileReadInput
    
    def _run(self, filepath: str, max_lines: int = 10) -> str:
        """读取文件"""
        try:
            # 安全检查：限制文件类型和大小
            if not filepath.endswith(('.txt', '.md', '.py', '.json')):
                return "错误：只支持读取文本文件(.txt, .md, .py, .json)"
            
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = []
                for i, line in enumerate(f):
                    if i >= max_lines:
                        lines.append(f"... (已限制显示{max_lines}行)")
                        break
                    lines.append(line.rstrip())
            
            content = "\n".join(lines)
            return f"文件 '{filepath}' 内容 (前{max_lines}行):\n{content}"
            
        except FileNotFoundError:
            return f"错误：找不到文件 '{filepath}'"
        except PermissionError:
            return f"错误：没有权限读取文件 '{filepath}'"
        except Exception as e:
            return f"读取文件时出错: {str(e)}"
    
    async def _arun(self, **kwargs):
        return self._run(**kwargs)

# ==================== 使用Agent测试自定义工具 ====================

def test_custom_tools():
    """测试自定义工具"""
    
    # 初始化LLM
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0
    )
    
    # 创建工具列表
    tools = [
        CalculatorTool(),
        WeatherTool(),
        text_length_counter,  # 装饰器创建的工具
        FileReadTool(),
    ]
    
    # 创建Agent
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,  # 显示详细执行过程
        handle_parsing_errors=True  # 处理解析错误
    )
    
    # 测试查询
    print("=" * 50)
    print("测试1: 数学计算")
    print("=" * 50)
    result1 = agent.run("计算15.5乘以3.2的结果")
    print(f"结果: {result1}\n")
    
    print("=" * 50)
    print("测试2: 天气查询")
    print("=" * 50)
    result2 = agent.run("查询北京今天的天气")
    print(f"结果: {result2}\n")
    
    print("=" * 50)
    print("测试3: 文本分析")
    print("=" * 50)
    result3 = agent.run("统计这句话的长度: 'LangChain是一个强大的LLM应用开发框架'")
    print(f"结果: {result3}\n")
    
    # 注意：文件读取测试需要实际存在的文件
    print("=" * 50)
    print("测试4: 链式工具调用")
    print("=" * 50)
    result4 = agent.run(
        "查询上海明天的天气，然后计算温度平均值。"
        "假设最高温度是查询结果中的第一个数字，最低温度是第二个数字"
    )
    print(f"结果: {result4}")

# ==================== 进阶：带记忆和状态的工具 ====================

class CounterInput(BaseModel):
    """计数器操作输入"""
    action: str = Field(
        ..., 
        description="操作类型: 'increment', 'decrement', 'reset', 'get'"
    )
    step: Optional[int] = Field(1, description="步长，默认为1")

class CounterTool(BaseTool):
    """带状态的计数器工具"""
    name = "counter"
    description = "一个简单的计数器，支持增加、减少、重置和获取当前值"
    args_schema: Type[BaseModel] = CounterInput
    
    def __init__(self):
        super().__init__()
        self._count = 0  # 内部状态
    
    def _run(self, action: str, step: int = 1) -> str:
        """执行计数器操作"""
        if action == "increment":
            self._count += step
            return f"计数器增加了{step}，当前值: {self._count}"
        elif action == "decrement":
            self._count -= step
            return f"计数器减少了{step}，当前值: {self._count}"
        elif action == "reset":
            self._count = 0
            return "计数器已重置为0"
        elif action == "get":
            return f"当前计数器值: {self._count}"
        else:
            return f"错误：不支持的操作 '{action}'"
    
    async def _arun(self, **kwargs):
        return self._run(**kwargs)

def test_counter_tool():
    """测试带状态的工具"""
    print("=" * 50)
    print("测试计数器工具")
    print("=" * 50)
    
    counter = CounterTool()
    
    # 手动测试
    print(counter._run("increment", 5))
    print(counter._run("increment", 3))
    print(counter._run("get"))
    print(counter._run("decrement", 2))
    print(counter._run("reset"))

# ==================== 主程序 ====================

if __name__ == "__main__":
    print("自定义Tool函数演示")
    print("=" * 60)
    
    # 测试基础工具
    test_custom_tools()
    
    # 测试计数器工具
    test_counter_tool()
    
    print("\n" + "=" * 60)
    print("演示完成！")
```

## 4. 注意事项
### 4.1 编写建议
#### 4.1.1 描述要清晰具体
```python
# ❌ 不好的描述
description = "处理数据"

# ✅ 好的描述
description = """
分析用户提供的CSV数据文件。支持以下操作：
1. 显示前N行数据
2. 计算数值列的统计信息（平均值、中位数、标准差）
3. 按指定列排序数据
需要提供文件路径和操作类型。
"""
```

#### 4.1.2 错误处理要完善
```python
def _run(self, **kwargs):
    try:
        # 业务逻辑
        return result
    except ValueError as e:
        return f"输入错误: {str(e)}"
    except ConnectionError as e:
        return f"连接失败: {str(e)}"
    except Exception as e:
        return f"未知错误: {str(e)}"
```

#### 4.1.3 参数验证要严格
```python
class SearchInput(BaseModel):
    query: str = Field(..., min_length=1, max_length=100)
    max_results: int = Field(5, ge=1, le=50)
    
    @validator('query')
    def validate_query(cls, v):
        if 'DROP TABLE' in v.upper() or 'DELETE' in v.upper():
            raise ValueError('查询包含非法关键词')
        return v
```

### 4.2 性能优化技巧
#### 4.2.1 使用缓存
```python
from functools import lru_cache

class APITool(BaseTool):
    @lru_cache(maxsize=128)
    def _call_api(self, params):
        # API调用逻辑
        pass
```

#### 4.2.2 实现异步版本
```python
async def _arun(self, **kwargs):
    # 异步调用API或IO操作
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()
```
## 5. 常见问题与解决方案
### Q1: Tool函数不执行怎么办？
检查点：

1. 确认description是否足够清晰

2. 检查args_schema是否正确定义了参数

3. 确保工具已正确添加到Agent的tools列表中

### Q2: 参数解析失败？
解决方案：

```python
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    handle_parsing_errors=True,  # 启用错误处理
    max_iterations=5  # 限制最大迭代次数
)
```
### Q3: 如何调试Tool的调用？
```python
# 1. 启用verbose模式
agent = initialize_agent(verbose=True)

# 2. 手动测试工具
tool = CalculatorTool()
print(tool._run(num1=5, num2=3, operation="add"))

# 3. 检查工具描述
print(f"工具名称: {tool.name}")
print(f"工具描述: {tool.description}")
```


