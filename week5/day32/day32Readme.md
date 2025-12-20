day32 多工具组合执行链

# 多工具组合执行链详解与实践指南
## 1. 什么是多工具组合执行链？
### 1.1 核心概念
多工具组合执行链是指让一个Agent按照特定逻辑或流程，依次调用多个工具来完成复杂任务的机制。它允许LLM将一个复杂问题分解为多个步骤，每个步骤选择合适的工具执行，最终整合结果。

### 1.2 与传统链式调用的区别
特性	| 传统Chain	|Agent工具链
--|--|--
执行路径	|固定、预定义	|动态、基于LLM推理
工具选择	|硬编码	|LLM实时选择
灵活性	|低	|高
适用场景	|确定流程	|不确定、复杂任务

### 1.3 工作流程

    用户问题 → LLM分析 → 选择工具1 → 执行 → 观察结果 
        → LLM再分析 → 选择工具2 → 执行 → 观察结果
        → ... → 最终整合 → 返回答案

## 2. 多工具组合的关键技术
### 2.1 ReAct框架
Reason + Act 是LangChain Agent的核心模式：

- Reason: LLM思考下一步该做什么

- Act: 调用工具执行动作

- Observe: 观察工具返回结果

### 2.2 工具选择机制
LLM通过以下方式选择工具：

- 工具描述匹配: 基于description字段

- 上下文理解: 考虑对话历史和之前的结果

- 优先级评估: 判断哪个工具最适合当前步骤

### 2.3 执行控制
- 最大迭代次数: 防止无限循环

- 提前终止: 当得到满意答案时停止

- 错误恢复: 工具失败时的处理策略

## 3. 从0到1创建多工具组合Demo
### 3.1 项目结构
```text
multi_tool_chain/
├── tools/
│   ├── __init__.py
│   ├── finance_tools.py     # 金融相关工具
│   ├── data_tools.py        # 数据处理工具
│   └── web_tools.py         # 网络工具
├── agents/
│   ├── __init__.py
│   └── finance_advisor.py   # 金融顾问Agent
├── config.py               # 配置文件
├── main.py                # 主程序
└── requirements.txt       # 依赖
```
3.2 完整代码实现
```python
# main.py - 多工具组合执行链完整演示
import os
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import json
import requests
from decimal import Decimal, ROUND_HALF_UP

# LangChain核心组件
from langchain.tools import BaseTool, Tool
from langchain.agents import initialize_agent, AgentType
from langchain.agents.agent import AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain.callbacks import StreamingStdOutCallbackHandler
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from pydantic import BaseModel, Field, validator

# 设置API密钥
os.environ["OPENAI_API_KEY"] = "your-api-key-here"  # 替换为你的API密钥

# ==================== 工具1：股票价格查询工具 ====================

class StockPriceInput(BaseModel):
    """股票查询输入参数"""
    symbol: str = Field(..., description="股票代码，例如：AAPL, GOOGL, TSLA")
    timeframe: Optional[str] = Field(
        "today", 
        description="时间范围：'today'（今天）, 'week'（本周）, 'month'（本月）"
    )

class StockPriceTool(BaseTool):
    """获取股票价格信息（模拟数据）"""
    name = "stock_price_lookup"
    description = """
    查询股票价格信息。输入股票代码和时间范围。
    可以获取当前价格、涨跌幅等信息。
    """
    args_schema = StockPriceInput
    
    # 模拟股票数据
    _mock_stock_data = {
        "AAPL": {"price": 175.25, "change": 1.5, "change_percent": 0.86},
        "GOOGL": {"price": 138.42, "change": -0.32, "change_percent": -0.23},
        "TSLA": {"price": 245.18, "change": 5.42, "change_percent": 2.26},
        "MSFT": {"price": 330.15, "change": 2.15, "change_percent": 0.66},
        "AMZN": {"price": 145.80, "change": -1.20, "change_percent": -0.82},
    }
    
    def _run(self, symbol: str, timeframe: str = "today") -> str:
        """查询股票价格"""
        symbol = symbol.upper()
        
        if symbol not in self._mock_stock_data:
            available = ", ".join(self._mock_stock_data.keys())
            return f"错误：股票代码 '{symbol}' 不存在。可用代码：{available}"
        
        stock = self._mock_stock_data[symbol]
        
        # 根据时间范围调整数据（模拟）
        if timeframe == "week":
            # 模拟一周数据波动
            weekly_change = stock["change_percent"] * 5
            return (
                f"{symbol} 本周表现：\n"
                f"  当前价格：${stock['price']:.2f}\n"
                f"  周涨跌幅：{weekly_change:.2f}%\n"
                f"  波动范围：${stock['price']*0.95:.2f} - ${stock['price']*1.05:.2f}"
            )
        elif timeframe == "month":
            # 模拟一月数据
            monthly_change = stock["change_percent"] * 22
            return (
                f"{symbol} 本月表现：\n"
                f"  当前价格：${stock['price']:.2f}\n"
                f"  月涨跌幅：{monthly_change:.2f}%\n"
                f"  30日平均：${stock['price']*0.98:.2f}"
            )
        else:
            # 今日数据
            change_sign = "+" if stock["change"] >= 0 else ""
            return (
                f"{symbol} 今日行情：\n"
                f"  当前价格：${stock['price']:.2f}\n"
                f"  涨跌额：{change_sign}${stock['change']:.2f}\n"
                f"  涨跌幅：{change_sign}{stock['change_percent']:.2f}%"
            )
    
    async def _arun(self, **kwargs):
        return self._run(**kwargs)

# ==================== 工具2：投资组合计算器 ====================

class PortfolioInput(BaseModel):
    """投资组合输入参数"""
    investments: List[Dict[str, Any]] = Field(
        ...,
        description="投资列表，每个投资包含 'symbol'(代码), 'shares'(股数), 'price'(购买价格)"
    )
    current_prices: Optional[Dict[str, float]] = Field(
        None,
        description="当前股价，如果不提供则使用最新价格"
    )

class PortfolioCalculatorTool(BaseTool):
    """计算投资组合表现"""
    name = "portfolio_calculator"
    description = """
    计算投资组合的当前价值、收益、收益率等指标。
    需要提供投资列表（股票代码、股数、购买价格）。
    """
    args_schema = PortfolioInput
    
    def _run(self, investments: List[Dict[str, Any]], 
             current_prices: Optional[Dict[str, float]] = None) -> str:
        """计算投资组合"""
        try:
            total_investment = Decimal('0')
            total_current = Decimal('0')
            results = []
            
            # 获取当前价格（模拟）
            stock_prices = {
                "AAPL": Decimal('175.25'),
                "GOOGL": Decimal('138.42'),
                "TSLA": Decimal('245.18'),
                "MSFT": Decimal('330.15'),
                "AMZN": Decimal('145.80'),
            }
            
            if current_prices:
                for symbol, price in current_prices.items():
                    stock_prices[symbol.upper()] = Decimal(str(price))
            
            for inv in investments:
                symbol = inv['symbol'].upper()
                shares = Decimal(str(inv['shares']))
                buy_price = Decimal(str(inv.get('price', 0)))
                
                if symbol not in stock_prices:
                    return f"错误：无法获取股票 '{symbol}' 的价格"
                
                current_price = stock_prices[symbol]
                
                # 计算投资额
                investment = shares * buy_price if buy_price > 0 else Decimal('0')
                current_value = shares * current_price
                
                total_investment += investment
                total_current += current_value
                
                if investment > 0:
                    profit = current_value - investment
                    profit_percent = (profit / investment * 100).quantize(Decimal('0.01'))
                else:
                    profit = Decimal('0')
                    profit_percent = Decimal('0')
                
                results.append({
                    'symbol': symbol,
                    'shares': shares,
                    'current_price': current_price,
                    'current_value': current_value,
                    'profit': profit,
                    'profit_percent': profit_percent
                })
            
            # 计算总计
            total_profit = total_current - total_investment
            total_profit_percent = (
                (total_profit / total_investment * 100).quantize(Decimal('0.01')) 
                if total_investment > 0 else Decimal('0')
            )
            
            # 格式化输出
            output = "📊 投资组合分析报告\n"
            output += "=" * 40 + "\n"
            
            for r in results:
                profit_sign = "+" if r['profit'] >= 0 else ""
                output += (
                    f"{r['symbol']}:\n"
                    f"  持有：{r['shares']}股\n"
                    f"  现价：${r['current_price']:.2f}\n"
                    f"  现值：${r['current_value']:.2f}\n"
                    f"  收益：{profit_sign}${r['profit']:.2f} ({profit_sign}{r['profit_percent']}%)\n"
                    f"  {'-'*30}\n"
                )
            
            profit_sign_total = "+" if total_profit >= 0 else ""
            output += (
                f"\n📈 总计：\n"
                f"  总投资：${total_investment:.2f}\n"
                f"  总现值：${total_current:.2f}\n"
                f"  总收益：{profit_sign_total}${total_profit:.2f} "
                f"({profit_sign_total}{total_profit_percent}%)\n"
            )
            
            return output
            
        except Exception as e:
            return f"计算投资组合时出错：{str(e)}"
    
    async def _arun(self, **kwargs):
        return self._run(**kwargs)

# ==================== 工具3：财务新闻获取工具 ====================

class NewsInput(BaseModel):
    """新闻查询输入参数"""
    topic: str = Field(..., description="新闻主题或关键词")
    limit: Optional[int] = Field(3, description="返回的新闻数量，默认3条")

class FinancialNewsTool(BaseTool):
    """获取金融新闻（模拟）"""
    name = "financial_news"
    description = """
    获取最新的金融新闻和市场动态。
    可以按主题（如股票代码、公司名称、市场事件）搜索。
    """
    args_schema = NewsInput
    
    def _run(self, topic: str, limit: int = 3) -> str:
        """获取新闻"""
        # 模拟新闻数据
        news_database = {
            "AAPL": [
                "苹果发布新款iPhone，股价上涨2%",
                "苹果与欧盟达成税收协议",
                "苹果将在印度扩大生产"
            ],
            "GOOGL": [
                "谷歌AI新突破，推出Gemini Ultra",
                "谷歌面临反垄断调查",
                "谷歌云业务增长超预期"
            ],
            "TSLA": [
                "特斯拉Cybertruck开始交付",
                "特斯拉在中国降价促销",
                "特斯拉储能业务增长迅速"
            ],
            "市场": [
                "美联储维持利率不变",
                "科技股普遍上涨，纳斯达克创新高",
                "原油价格上涨影响全球市场"
            ],
            "经济": [
                "美国非农就业数据超预期",
                "通胀率继续下降",
                "消费者信心指数回升"
            ]
        }
        
        topic_lower = topic.lower()
        found_news = []
        
        # 查找相关新闻
        for category, news_list in news_database.items():
            if (topic_lower in category.lower() or 
                any(topic_lower in n.lower() for n in news_list)):
                found_news.extend(news_list)
        
        # 如果没有直接匹配，使用通用新闻
        if not found_news:
            found_news = news_database.get("市场", []) + news_database.get("经济", [])
        
        # 限制数量并格式化
        selected_news = found_news[:limit]
        
        output = f"📰 关于 '{topic}' 的最新新闻（{len(selected_news)}条）：\n"
        for i, news in enumerate(selected_news, 1):
            output += f"{i}. {news}\n"
        
        if not selected_news:
            output = f"未找到关于 '{topic}' 的新闻。"
        
        return output
    
    async def _arun(self, **kwargs):
        return self._run(**kwargs)

# ==================== 工具4：风险评估工具 ====================

class RiskInput(BaseModel):
    """风险评估输入参数"""
    symbols: List[str] = Field(..., description="股票代码列表")
    investment_amount: Optional[float] = Field(
        10000, 
        description="投资金额（美元），默认10000"
    )

class RiskAssessmentTool(BaseTool):
    """投资风险评估工具"""
    name = "risk_assessment"
    description = """
    评估投资组合的风险水平，提供风险评分和建议。
    需要提供股票代码列表和可选的投资金额。
    """
    args_schema = RiskInput
    
    def _run(self, symbols: List[str], investment_amount: float = 10000) -> str:
        """评估风险"""
        # 模拟风险数据
        risk_profiles = {
            "AAPL": {"risk": "中等", "volatility": 1.2, "sector": "科技"},
            "GOOGL": {"risk": "中等", "volatility": 1.3, "sector": "科技"},
            "TSLA": {"risk": "高", "volatility": 2.1, "sector": "汽车"},
            "MSFT": {"risk": "低", "volatility": 0.9, "sector": "科技"},
            "AMZN": {"risk": "中等", "volatility": 1.4, "sector": "零售"},
        }
        
        # 分析投资组合
        total_volatility = 0
        sectors = {}
        risk_counts = {"低": 0, "中等": 0, "高": 0}
        
        for symbol in symbols:
            symbol_upper = symbol.upper()
            if symbol_upper in risk_profiles:
                profile = risk_profiles[symbol_upper]
                total_volatility += profile["volatility"]
                sectors[profile["sector"]] = sectors.get(profile["sector"], 0) + 1
                risk_counts[profile["risk"]] += 1
            else:
                # 未知股票，默认高风险
                total_volatility += 2.0
                risk_counts["高"] += 1
        
        if not symbols:
            return "错误：未提供股票代码"
        
        # 计算平均波动性和风险等级
        avg_volatility = total_volatility / len(symbols)
        
        if avg_volatility < 1.0:
            overall_risk = "低风险"
            recommendation = "适合保守型投资者"
        elif avg_volatility < 1.5:
            overall_risk = "中等风险"
            recommendation = "适合平衡型投资者"
        else:
            overall_risk = "高风险"
            recommendation = "适合激进型投资者"
        
        # 检查行业集中度
        sector_warning = ""
        if len(sectors) == 1:
            sector_warning = "⚠️ 警告：投资过于集中在一个行业"
        elif max(sectors.values()) / len(symbols) > 0.7:
            sector_warning = "⚠️ 注意：行业集中度较高"
        
        # 格式化输出
        output = "📊 投资风险评估报告\n"
        output += "=" * 40 + "\n"
        output += f"投资组合：{', '.join(symbols)}\n"
        output += f"投资金额：${investment_amount:,.2f}\n\n"
        
        output += "📈 风险分析：\n"
        output += f"  总体风险等级：{overall_risk}\n"
        output += f"  平均波动性：{avg_volatility:.2f}\n"
        output += f"  风险分布：低({risk_counts['低']}) 中({risk_counts['中等']}) 高({risk_counts['高']})\n\n"
        
        if sectors:
            output += "🏢 行业分布：\n"
            for sector, count in sectors.items():
                percentage = (count / len(symbols)) * 100
                output += f"  {sector}: {count}只股票 ({percentage:.1f}%)\n"
            output += "\n"
        
        if sector_warning:
            output += f"{sector_warning}\n\n"
        
        output += "💡 投资建议：\n"
        output += f"  {recommendation}\n"
        
        if overall_risk == "高风险":
            output += "  • 考虑增加低风险资产配置\n"
            output += "  • 设置止损点\n"
            output += "  • 定期重新平衡投资组合\n"
        elif overall_risk == "中等风险":
            output += "  • 保持多元化投资\n"
            output += "  • 定期监控市场动态\n"
            output += "  • 考虑长期持有策略\n"
        else:
            output += "  • 适合稳健增长目标\n"
            output += "  • 可考虑少量配置高风险资产\n"
        
        return output
    
    async def _arun(self, **kwargs):
        return self._run(**kwargs)

# ==================== 工具5：货币转换工具 ====================

class CurrencyInput(BaseModel):
    """货币转换输入参数"""
    amount: float = Field(..., description="金额")
    from_currency: str = Field(..., description="源货币代码，如：USD, EUR, CNY")
    to_currency: str = Field(..., description="目标货币代码")

class CurrencyConverterTool(BaseTool):
    """货币转换工具（模拟汇率）"""
    name = "currency_converter"
    description = """
    在不同货币之间进行转换。
    支持主要货币：USD, EUR, GBP, JPY, CNY等。
    """
    args_schema = CurrencyInput
    
    def _run(self, amount: float, from_currency: str, to_currency: str) -> str:
        """货币转换"""
        # 模拟汇率数据
        exchange_rates = {
            "USD": {"EUR": 0.92, "GBP": 0.79, "JPY": 148.5, "CNY": 7.18},
            "EUR": {"USD": 1.09, "GBP": 0.86, "JPY": 161.5, "CNY": 7.81},
            "GBP": {"USD": 1.27, "EUR": 1.16, "JPY": 187.9, "CNY": 9.09},
            "CNY": {"USD": 0.14, "EUR": 0.13, "GBP": 0.11, "JPY": 20.7},
        }
        
        from_curr = from_currency.upper()
        to_curr = to_currency.upper()
        
        if from_curr == to_curr:
            return f"{amount} {from_curr} = {amount} {to_curr}（相同货币）"
        
        if (from_curr in exchange_rates and 
            to_curr in exchange_rates[from_curr]):
            rate = exchange_rates[from_curr][to_curr]
            converted = amount * rate
            return (
                f"💱 货币转换：\n"
                f"  {amount:.2f} {from_curr} = {converted:.2f} {to_curr}\n"
                f"  汇率：1 {from_curr} = {rate:.4f} {to_curr}"
            )
        else:
            available = ", ".join(exchange_rates.keys())
            return f"错误：不支持 {from_curr} 到 {to_curr} 的转换。支持货币：{available}"
    
    async def _arun(self, **kwargs):
        return self._run(**kwargs)

# ==================== 创建金融顾问Agent ====================

def create_financial_advisor():
    """创建金融顾问Agent"""
    
    # 初始化LLM
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0.1,  # 较低的temperature使输出更稳定
        streaming=False,
        callbacks=[StreamingStdOutCallbackHandler()]
    )
    
    # 创建工具列表
    tools = [
        StockPriceTool(),
        PortfolioCalculatorTool(),
        FinancialNewsTool(),
        RiskAssessmentTool(),
        CurrencyConverterTool(),
    ]
    
    # 创建对话记忆
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        output_key="output"
    )
    
    # 自定义提示模板
    agent_prompt = PromptTemplate(
        template="""
        你是一位专业的金融顾问助手，专门帮助用户进行投资分析和决策。
        
        你可以使用以下工具：
        {tools}
        
        使用以下格式：
        问题：用户的问题
        思考：你需要思考如何逐步解决问题
        行动：需要使用的工具名称
        行动输入：工具的输入参数
        观察：工具返回的结果
        ...（这个思考/行动/观察可以重复多次）
        最终答案：基于所有观察结果的最终答案
        
        如果你无法使用工具解决问题，请诚实地告知用户。
        
        之前的对话：
        {chat_history}
        
        问题：{input}
        
        开始！
        {agent_scratchpad}
        """,
        input_variables=["input", "chat_history", "agent_scratchpad"]
    )
    
    # 创建Agent执行器
    agent_executor = AgentExecutor.from_agent_and_tools(
        agent=initialize_agent(
            tools=tools,
            llm=llm,
            agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5,
            early_stopping_method="generate"
        ).agent,
        tools=tools,
        memory=memory,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=5,
        return_intermediate_steps=True  # 返回中间步骤，便于调试
    )
    
    return agent_executor

# ==================== 演示多工具链式调用 ====================

def demonstrate_multi_tool_chains():
    """演示多工具组合执行链"""
    
    print("=" * 60)
    print("金融顾问Agent - 多工具组合执行链演示")
    print("=" * 60)
    
    # 创建Agent
    agent = create_financial_advisor()
    
    # 演示场景1：投资组合全面分析
    print("\n🔍 场景1：投资组合全面分析")
    print("-" * 50)
    
    portfolio_query = """
    请帮我分析以下投资组合：
    1. AAPL：100股，购买价格$150
    2. GOOGL：50股，购买价格$120
    3. TSLA：30股，购买价格$200
    
    请完成以下分析：
    1. 查询每只股票的当前价格
    2. 计算整个投资组合的表现
    3. 评估投资风险
    4. 获取相关新闻
    """
    
    print(f"用户查询：{portfolio_query}")
    print("\nAgent执行过程：")
    
    result1 = agent.invoke({"input": portfolio_query})
    print(f"\n最终答案：\n{result1['output']}")
    
    # 演示场景2：跨国投资分析
    print("\n\n💼 场景2：跨国投资分析")
    print("-" * 50)
    
    international_query = """
    我是一名中国投资者，有100,000元人民币想投资美国科技股。
    我关注AAPL和GOOGL。
    
    请帮我：
    1. 将100,000元人民币转换成美元
    2. 查询这两只股票的当前价格
    3. 用转换后的美元计算可以购买多少股
    4. 评估这个投资计划的风险
    """
    
    print(f"用户查询：{international_query}")
    print("\nAgent执行过程：")
    
    result2 = agent.invoke({"input": international_query})
    print(f"\n最终答案：\n{result2['output']}")
    
    # 演示场景3：市场动态跟踪
    print("\n\n📈 场景3：市场动态跟踪")
    print("-" * 50)
    
    market_query = """
    最近科技股市场有什么动态？
    特别关注苹果和特斯拉的新闻。
    同时查看它们本周的股价表现。
    """
    
    print(f"用户查询：{market_query}")
    print("\nAgent执行过程：")
    
    result3 = agent.invoke({"input": market_query})
    print(f"\n最终答案：\n{result3['output']}")
    
    return agent

# ==================== 调试和监控工具 ====================

def analyze_agent_steps(agent_executor, query: str):
    """分析Agent的执行步骤"""
    print(f"\n🔧 分析查询：{query}")
    print("=" * 50)
    
    result = agent_executor.invoke({"input": query})
    
    print("\n执行步骤分析：")
    for i, step in enumerate(result.get('intermediate_steps', []), 1):
        action, observation = step
        print(f"\n步骤 {i}:")
        print(f"  工具调用：{action.tool}")
        print(f"  输入参数：{action.tool_input}")
        print(f"  工具输出：{observation[:200]}...")
    
    print(f"\n总工具调用次数：{len(result.get('intermediate_steps', []))}")
    print(f"最终输出长度：{len(result['output'])} 字符")

# ==================== 高级功能：工具路由 ====================

class ToolRouter:
    """工具路由器，智能选择工具"""
    
    def __init__(self, tools):
        self.tools = {tool.name: tool for tool in tools}
        self.router_llm = ChatOpenAI(temperature=0)
    
    def route_query(self, query: str) -> str:
        """路由查询到合适的工具"""
        tool_descriptions = "\n".join([
            f"- {name}: {tool.description[:100]}..."
            for name, tool in self.tools.items()
        ])
        
        routing_prompt = f"""
        根据用户查询，选择最合适的工具：
        
        可用工具：
        {tool_descriptions}
        
        用户查询：{query}
        
        请返回最合适的工具名称，如果不需要工具则返回"none"。
        只返回工具名称或"none"。
        """
        
        response = self.router_llm.invoke(routing_prompt)
        return response.content.strip()

# ==================== 主程序 ====================

if __name__ == "__main__":
    print("🚀 多工具组合执行链演示系统")
    print("=" * 60)
    
    # 演示基本功能
    agent = demonstrate_multi_tool_chains()
    
    # 分析执行步骤
    print("\n\n🔬 执行步骤深度分析")
    print("=" * 60)
    
    test_query = "我有100股AAPL，购买价格是$160，现在值多少钱？"
    analyze_agent_steps(agent, test_query)
    
    # 演示工具路由
    print("\n\n🔄 工具路由演示")
    print("=" * 60)
    
    # 创建所有工具实例
    all_tools = [
        StockPriceTool(),
        PortfolioCalculatorTool(),
        FinancialNewsTool(),
        RiskAssessmentTool(),
        CurrencyConverterTool(),
    ]
    
    router = ToolRouter(all_tools)
    
    test_queries = [
        "AAPL今天的股价是多少？",
        "将1000美元换成人民币",
        "特斯拉有什么新闻？",
        "AAPL和GOOGL哪个风险更高？",
        "今天天气怎么样？"
    ]
    
    for query in test_queries:
        selected_tool = router.route_query(query)
        print(f"查询：'{query}' → 路由到：'{selected_tool}'")
    
    print("\n" + "=" * 60)
    print("演示完成！")
    print("\n💡 关键观察：")
    print("1. Agent能够理解复杂查询并分解为多个步骤")
    print("2. 工具之间可以传递数据和上下文")
    print("3. Agent根据中间结果动态调整下一步行动")
    print("4. 记忆机制使多轮对话成为可能")
```
---

## 4. 多工具组合的高级技巧
### 4.1 工具间的数据传递
```python
# 方法1：通过LLM上下文传递
# Agent自动在工具调用之间传递观察结果

# 方法2：创建数据管道工具
class DataPipelineTool(BaseTool):
    """处理多个工具输出的管道"""
    def _run(self, steps: List[Dict]) -> str:
        results = {}
        for step in steps:
            tool_name = step["tool"]
            tool_input = step["input"]
            # 调用工具并存储结果
            results[tool_name] = self._call_tool(tool_name, tool_input)
        return self._aggregate_results(results)
```
### 4.2 并行工具执行
```python
import asyncio

class ParallelToolExecutor:
    """并行执行多个工具"""
    
    async def execute_parallel(self, tools_to_execute):
        tasks = []
        for tool_info in tools_to_execute:
            task = self._execute_tool_async(tool_info)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return self._combine_results(results)
```       
### 4.3 工具依赖管理
```python
class ToolDependencyManager:
    """管理工具间的依赖关系"""
    
    def __init__(self):
        self.dependencies = {
            "portfolio_calculator": ["stock_price_lookup"],
            "risk_assessment": ["stock_price_lookup", "portfolio_calculator"],
        }
    
    def get_execution_order(self, target_tool: str) -> List[str]:
        """获取工具执行顺序"""
        order = []
        visited = set()
        
        def dfs(tool):
            if tool in visited:
                return
            visited.add(tool)
            
            if tool in self.dependencies:
                for dep in self.dependencies[tool]:
                    dfs(dep)
            
            order.append(tool)
        
        dfs(target_tool)
        return order
```
## 5. 最佳实践
### 5.1 设计原则
    单一职责：每个工具只做一件事
    
    明确接口：输入输出清晰定义
    
    错误隔离：一个工具失败不影响其他
    
    状态管理：谨慎使用有状态的工具

### 5.2 性能优化
```python
# 1. 缓存常用结果
from functools import lru_cache

class CachedTool(BaseTool):
    @lru_cache(maxsize=128)
    def _get_data(self, key):
        return expensive_operation(key)

# 2. 批量处理
class BatchProcessorTool(BaseTool):
    def _run_batch(self, inputs: List) -> List:
        # 批量处理提高效率
        pass

# 3. 异步优化
async def _arun(self, **kwargs):
    # 使用异步IO
    async with aiohttp.ClientSession() as session:
        # 并行请求
        pass
```
### 5.3 调试策略
```python
# 创建调试代理工具
class DebugProxyTool(BaseTool):
    """包装其他工具，添加调试信息"""
    
    def __init__(self, wrapped_tool):
        self.wrapped_tool = wrapped_tool
        super().__init__()
    
    def _run(self, **kwargs):
        print(f"[DEBUG] 调用工具: {self.wrapped_tool.name}")
        print(f"[DEBUG] 输入参数: {kwargs}")
        start_time = time.time()
        
        result = self.wrapped_tool._run(**kwargs)
        
        elapsed = time.time() - start_time
        print(f"[DEBUG] 执行时间: {elapsed:.2f}秒")
        print(f"[DEBUG] 输出结果: {result[:100]}...")
        
        return result
```
## 6. 常见问题与解决方案
### Q1: Agent陷入循环调用怎么办？
解决方案：

```python
agent = initialize_agent(
    max_iterations=5,  # 限制最大迭代次数
    early_stopping_method="generate",  # 提前停止
    handle_parsing_errors=True,
)
```
### Q2: 如何提高工具选择准确性？
策略：

    优化工具描述，包含使用示例

    使用few-shot prompting提供示例

    实现工具路由层预处理

### Q3: 工具间如何共享复杂数据？
模式：

```python
# 使用共享数据上下文
class SharedContext:
    def __init__(self):
        self.data = {}
    
    def set(self, key, value):
        self.data[key] = value
    
    def get(self, key, default=None):
        return self.data.get(key, default)

# 在工具中使用
class ToolWithContext(BaseTool):
    def __init__(self, context):
        self.context = context
        super().__init__()
```
