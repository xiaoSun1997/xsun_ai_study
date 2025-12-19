from pydantic import BaseModel, Field


class CurrencyInput(BaseModel):
    """货币转换输入参数"""
    amount: float = Field(..., description="金额")
    from_currency: str = Field(..., description="源货币代码，如：USD, EUR, CNY")
    to_currency: str = Field(..., description="目标货币代码")
