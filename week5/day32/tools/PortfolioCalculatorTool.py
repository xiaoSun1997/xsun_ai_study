from decimal import Decimal
from typing import List, Dict, Any, Optional, Type

from langchain_core.tools import BaseTool

from model.PortfolioInput import PortfolioInput


class PortfolioCalculatorTool(BaseTool):
    """计算投资组合表现"""
    name: str = "portfolio_calculator"
    description: str = """
    计算投资组合的当前价值、收益、收益率等指标。
    需要提供投资列表（股票代码、股数、购买价格）。
    """
    args_schema: Type[PortfolioInput] = PortfolioInput

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
                    f"  {'-' * 30}\n"
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