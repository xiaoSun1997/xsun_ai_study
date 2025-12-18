from typing import Optional

from pydantic import BaseModel, Field


class StockPriceInput(BaseModel):
    """股票查询输入参数"""
    symbol: str = Field(..., description="股票代码,例如AAPL,GOOGL.TSLA等")
    timeframe: Optional[str] = Field("today",
                                     description="时间范围，：'today'（今天）, 'week'（本周）, 'month'（本月）")