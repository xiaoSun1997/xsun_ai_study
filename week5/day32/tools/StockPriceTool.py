from langchain_core.tools import BaseTool

from model.StockPriceInput import StockPriceInput


class StockPriceTool(BaseTool):
    """
    获取股票价格信息（模拟数据）
    """
    name = "stock_price_lookup"
    description = """ 查询股票价格信息。输入股票代码和时间范围。
    可以获取当前价格、涨跌幅等信息。"""
    args_schema = StockPriceInput

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
                f"  波动范围：${stock['price'] * 0.95:.2f} - ${stock['price'] * 1.05:.2f}"
            )
        elif timeframe == "month":
            # 模拟一月数据
            monthly_change = stock["change_percent"] * 22
            return (
                f"{symbol} 本月表现：\n"
                f"  当前价格：${stock['price']:.2f}\n"
                f"  月涨跌幅：{monthly_change:.2f}%\n"
                f"  30日平均：${stock['price'] * 0.98:.2f}"
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
