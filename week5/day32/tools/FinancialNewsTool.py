from langchain_core.tools import BaseTool
from typing import Type
from model.NewsInput import NewsInput


class FinancialNewsTool(BaseTool):
    """获取金融新闻（模拟）"""
    name: str = "financial_news"
    description: str = """
    获取最新的金融新闻和市场动态。
    可以按主题（如股票代码、公司名称、市场事件）搜索。
    """
    args_schema: Type[NewsInput] = NewsInput

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