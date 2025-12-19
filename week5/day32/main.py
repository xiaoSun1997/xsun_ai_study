
from langchain_classic.agents import AgentExecutor, initialize_agent, AgentType
from langchain_classic.memory import ConversationBufferMemory
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from tools.CurrencyConverterTool import CurrencyConverterTool
from tools.FinancialNewsTool import FinancialNewsTool
from tools.PortfolioCalculatorTool import PortfolioCalculatorTool
from tools.RiskAssessmentTool import RiskAssessmentTool
from tools.StockPriceTool import StockPriceTool


def create_financial_adviser():
    """创建金融顾问Agent"""
    llm = ChatOpenAI(
        model="qwen-plus",
        temperature=0.7,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        api_key="sk-your-key",
        streaming=False
    )

    tools = [
        StockPriceTool(),
        PortfolioCalculatorTool(),
        FinancialNewsTool(),
        RiskAssessmentTool(),
        CurrencyConverterTool(),
    ]
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True, output_key="output")

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
    agent_executor = AgentExecutor.from_agent_and_tools(
        agent=initialize_agent(
            llm=llm,
            tools=tools,
            agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=10,
            early_stopping_method="generate").agent,
        tools=tools,
        memory=memory,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=10,
        return_intermediate_steps=True
    )

    return agent_executor

def demonstrate_multi_tool_chains():
    """演示多工具组合执行链"""
    print("=" * 60)
    print("金融顾问Agent - 多工具组合执行链演示")
    print("=" * 60)
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

    agent = create_financial_adviser()
    result1 = agent.invoke({"input": portfolio_query})
    print(f"\n最终答案：\n{result1['output']}")


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

class ToolRouter:
    """工具路由器，智能选择工具"""

    def __init__(self, tools):
        self.tools = {tool.name: tool for tool in tools}
        self.router_llm = ChatOpenAI(
            model="qwen-plus",
            temperature=0,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            api_key="sk-YOUR-KEY"
        )

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
    demonstrate_multi_tool_chains()

    # 分析执行步骤
    print("\n\n🔬 执行步骤深度分析")
    print("=" * 60)

    agent = create_financial_adviser()
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


# (day32venv) PS E:\code\xsun_ai_study\week5\day32> python main.py
# 🚀 多工具组合执行链演示系统
# ============================================================
# ============================================================
# 金融顾问Agent - 多工具组合执行链演示
# ============================================================
#
# 🔍 场景1：投资组合全面分析
# --------------------------------------------------
# 用户查询：
#     请帮我分析以下投资组合：
#     1. AAPL：100股，购买价格$150
#     2. GOOGL：50股，购买价格$120
#     3. TSLA：30股，购买价格$200
#
#     请完成以下分析：
#     1. 查询每只股票的当前价格
#     2. 计算整个投资组合的表现
#     3. 评估投资风险
#     4. 获取相关新闻
#
#
# Agent执行过程：
# E:\code\xsun_ai_study\week5\day32\main.py:31: LangChainDeprecationWarning: Please see the migration guide at: https://python.langchain.com/docs/versions/migrating_memory/
#   memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True, output_key="output")
# E:\code\xsun_ai_study\week5\day32\main.py:63: LangChainDeprecationWarning: LangChain agents will continue to be supported, but it is recommended for new use cases to be built with LangGraph. LangGraph offers a more flexible and full-featured framework for building agents, including support for tool-calling, persistence of state, and human-in-the-loop workflows. For details, refer to the [LangGraph documentation](https://langchain-ai.github.io/langgraph/) as well as guides for [Migrating from AgentExecutor](https://python.langchain.com/docs/how_to/migrate_agent/) and LangGraph's [Pre-built ReAct agent](https://langchain-ai.github.io/langgraph/how-tos/create-react-agent/).
#   agent=initialize_agent(
#
#
# > Entering new AgentExecutor chain...
# Action:
# ```
# {
#   "action": "stock_price_lookup",
#   "action_input": {
#     "symbol": "AAPL",
#     "timeframe": "today"
#   }
# }
# ```
#
# Observation: AAPL 今日行情：
#   当前价格：$175.25
#   涨跌额：+$1.50
#   涨跌幅：+0.86%
# Thought:Action:
# ```
# {
#   "action": "stock_price_lookup",
#   "action_input": {
#     "symbol": "GOOGL",
#     "timeframe": "today"
#   }
# }
# ```
# Observation: GOOGL 今日行情：
#   当前价格：$138.42
#   涨跌额：$-0.32
#   涨跌幅：-0.23%
# Thought:Action:
# ```
# {
#   "action": "stock_price_lookup",
#   "action_input": {
#     "symbol": "TSLA",
#     "timeframe": "today"
#   }
# }
# ```
# Observation: TSLA 今日行情：
#   当前价格：$245.18
#   涨跌额：+$5.42
#   涨跌幅：+2.26%
# Thought:Action:
# ```
# {
#   "action": "portfolio_calculator",
#   "action_input": {
#     "investments": [
#       {
#         "symbol": "AAPL",
#         "shares": 100,
#         "price": 150
#       },
#       {
#         "symbol": "GOOGL",
#         "shares": 50,
#         "price": 120
#       },
#       {
#         "symbol": "TSLA",
#         "shares": 30,
#         "price": 200
#       }
#     ],
#     "current_prices": {
#       "AAPL": 175.25,
#       "GOOGL": 138.42,
#       "TSLA": 245.18
#     }
#   }
# }
# ```
# Observation: 📊 投资组合分析报告
# ========================================
# AAPL:
#   持有：100股
#   现价：$175.25
#   现值：$17525.00
#   收益：+$2525.00 (+16.83%)
#   ------------------------------
# GOOGL:
#   持有：50股
#   现价：$138.42
#   现值：$6921.00
#   收益：+$921.00 (+15.35%)
#   ------------------------------
# TSLA:
#   持有：30股
#   现价：$245.18
#   现值：$7355.40
#   收益：+$1355.40 (+22.59%)
#   ------------------------------
#
# 📈 总计：
#   总投资：$27000.00
#   总现值：$31801.40
#   总收益：+$4801.40 (+17.78%)
#
# Thought:Action:
# ```
# {
#   "action": "risk_assessment",
#   "action_input": {
#     "symbols": [
#       "AAPL",
#       "GOOGL",
#       "TSLA"
#     ],
#     "investment_amount": 31801.4
#   }
# }
# ```
#
#
# Observation: 📊 投资风险评估报告
# ========================================
# 投资组合：AAPL, GOOGL, TSLA
# 投资金额：$31,801.40
#
# 📈 风险分析：
#   总体风险等级：高风险
#   平均波动性：1.53
#   风险分布：低(0) 中(2) 高(1)
#
# 🏢 行业分布：
#   科技: 2只股票 (66.7%)
#   汽车: 1只股票 (33.3%)
#
# 💡 投资建议：
#   适合激进型投资者
#   • 考虑增加低风险资产配置
#   • 设置止损点
#   • 定期重新平衡投资组合
#
# Thought:Action:
# ```
# {
#   "action": "financial_news",
#   "action_input": {
#     "topic": "AAPL GOOGL TSLA stock news",
#     "limit": 3
#   }
# }
# ```
# Observation: 📰 关于 'AAPL GOOGL TSLA stock news' 的最新新闻（3条）：
# 1. 美联储维持利率不变
# 2. 科技股普遍上涨，纳斯达克创新高
# 3. 原油价格上涨影响全球市场
#
# Thought:```
# {
#   "action": "Final Answer",
#   "action_input": "📊 投资组合综合分析报告\n========================================\n\n📈 股票当前价格查询结果：\n- AAPL：$175.25（+0.86%）\n- GOOGL：$138.42（-0.23%）\n- TSLA：$245.18（+2.26%）\n\n💼 投资组合表现：\n- 总投资：$27,000.00\n- 当前总价值：$31,801.40\n- 总收益：+$4,801.40（+17.78%）\n\n🔍 各股票收益详情：\n• AAPL：收益 +$2,525.00（+16.83%）\n• GOOGL：收益 +$921.00（+15.35%）\n• TSLA：收益 +$1,355.40（+22.59%）\n\n⚠️ 风险评估：\n- 总体风险等级：高风险\n- 波动性：1.53（较高）\n- 行业集中度：科技股占66.7%\n- 建议：适合激进型投资者，建议分散配置、设置止损、定期再平衡。\n\n📰 相关市场新闻：\n1. 美联储维持利率不变\n2. 科技股普遍上涨，纳斯达克创新高\n3. 原油价格上涨影 响全球市场\n\n✅ 总结：投资组合表现良好，受益于科技股上涨，但存在行业集中和高波动风险，建议关注市场变化并适当调整持仓。"
# }
# ```
#
# > Finished chain.
#
# 最终答案：
# 📊 投资组合综合分析报告
# ========================================
#
# 📈 股票当前价格查询结果：
# - AAPL：$175.25（+0.86%）
# - GOOGL：$138.42（-0.23%）
# - TSLA：$245.18（+2.26%）
#
# 💼 投资组合表现：
# - 总投资：$27,000.00
# - 当前总价值：$31,801.40
# - 总收益：+$4,801.40（+17.78%）
#
# 🔍 各股票收益详情：
# • AAPL：收益 +$2,525.00（+16.83%）
# • GOOGL：收益 +$921.00（+15.35%）
# • TSLA：收益 +$1,355.40（+22.59%）
#
# ⚠️ 风险评估：
# - 总体风险等级：高风险
# - 波动性：1.53（较高）
# - 行业集中度：科技股占66.7%
# - 建议：适合激进型投资者，建议分散配置、设置止损、定期再平衡。
#
# 📰 相关市场新闻：
# 1. 美联储维持利率不变
# 2. 科技股普遍上涨，纳斯达克创新高
# 3. 原油价格上涨影响全球市场
#
# ✅ 总结：投资组合表现良好，受益于科技股上涨，但存在行业集中和高波动风险，建议关注市场变化并适当调整持仓。
#
#
# 🔬 执行步骤深度分析
# ============================================================
#
# 🔧 分析查询：我有100股AAPL，购买价格是$160，现在值多少钱？
# ==================================================
#
#
# > Entering new AgentExecutor chain...
# Action:
# ```
# {
#   "action": "stock_price_lookup",
#   "action_input": {
#     "symbol": "AAPL",
#     "timeframe": "today"
#   }
# }
# ```
#
# Observation: AAPL 今日行情：
#   当前价格：$175.25
#   涨跌额：+$1.50
#   涨跌幅：+0.86%
# Thought:```
# {
#   "action": "portfolio_calculator",
#   "action_input": {
#     "investments": [
#       {
#         "symbol": "AAPL",
#         "shares": 100,
#         "price": 160
#       }
#     ],
#     "current_prices": {
#       "AAPL": 175.25
#     }
#   }
# }
# ```
# Observation: 📊 投资组合分析报告
# ========================================
# AAPL:
#   持有：100股
#   现价：$175.25
#   现值：$17525.00
#   收益：+$1525.00 (+9.53%)
#   ------------------------------
#
# 📈 总计：
#   总投资：$16000.00
#   总现值：$17525.00
#   总收益：+$1525.00 (+9.53%)
#
# Thought:Action:
# ```
# {
#   "action": "Final Answer",
#   "action_input": "您持有的100股AAPL股票当前价值为$17,525.00，总收益为+$1,525.00，收益率为+9.53%。"
# }
# ```
#
# > Finished chain.
#
# 执行步骤分析：
#
# 步骤 1:
#   工具调用：stock_price_lookup
#   输入参数：{'symbol': 'AAPL', 'timeframe': 'today'}
#   工具输出：AAPL 今日行情：
#   当前价格：$175.25
#   涨跌额：+$1.50
#   涨跌幅：+0.86%...
#
# 步骤 2:
#   工具调用：portfolio_calculator
#   输入参数：{'investments': [{'symbol': 'AAPL', 'shares': 100, 'price': 160}], 'current_prices': {'AAPL': 175.25}}
#   工具输出：📊 投资组合分析报告
# ========================================
# AAPL:
#   持有：100股
#   现价：$175.25
#   现值：$17525.00
#   收益：+$1525.00 (+9.53%)
#   ------------------------------
#
# 📈 总计：
#   总投资：$16000.00
#   总现值：$17525.00
#   总收益：+$...
#
# 总工具调用次数：2
# 最终输出长度：56 字符
#
#
# 🔄 工具路由演示
# ============================================================
# 查询：'AAPL今天的股价是多少？' → 路由到：'stock_price_lookup'
# 查询：'将1000美元换成人民币' → 路由到：'currency_converter'
# 查询：'特斯拉有什么新闻？' → 路由到：'financial_news'
# 查询：'AAPL和GOOGL哪个风险更高？' → 路由到：'risk_assessment'
# 查询：'今天天气怎么样？' → 路由到：'none'
#
# ============================================================
# 演示完成！
#
# 💡 关键观察：
# 1. Agent能够理解复杂查询并分解为多个步骤
# 2. 工具之间可以传递数据和上下文
# 3. Agent根据中间结果动态调整下一步行动
# 4. 记忆机制使多轮对话成为可能