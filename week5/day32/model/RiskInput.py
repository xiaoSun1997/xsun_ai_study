from typing import List, Optional

from pydantic import BaseModel, Field


class RiskInput(BaseModel):
    """风险评估输入参数"""
    symbols: List[str] = Field(..., description="股票代码列表")
    investment_amount: Optional[float] = Field(
        10000,
        description="投资金额（美元），默认10000"
    )