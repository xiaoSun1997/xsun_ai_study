from typing import Dict, List, Any, Optional

from pydantic import BaseModel, Field


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