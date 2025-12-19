from typing import Optional

from pydantic import BaseModel, Field


class NewsInput(BaseModel):
    """新闻查询输入参数"""
    topic: str = Field(..., description="新闻主题或关键词")
    limit: Optional[int] = Field(3, description="返回的新闻数量，默认3条")