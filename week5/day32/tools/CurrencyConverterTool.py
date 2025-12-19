from langchain_core.tools import BaseTool
from typing import Type
from model.CurrencyInput import CurrencyInput


class CurrencyConverterTool(BaseTool):
    """货币转换工具（模拟汇率）"""
    name: str = "currency_converter"
    description: str = """
    在不同货币之间进行转换。
    支持主要货币：USD, EUR, GBP, JPY, CNY等。
    """
    args_schema: Type[CurrencyInput] = CurrencyInput

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