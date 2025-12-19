from typing import List, Type

from langchain_core.tools import BaseTool

from model.RiskInput import RiskInput


class RiskAssessmentTool(BaseTool):
    """投资风险评估工具"""
    name: str = "risk_assessment"
    description: str = """
    评估投资组合的风险水平，提供风险评分和建议。
    需要提供股票代码列表和可选的投资金额。
    """
    args_schema: Type[RiskInput] = RiskInput

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