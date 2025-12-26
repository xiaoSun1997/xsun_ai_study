day39: 外部API封装（NewsAPI、Google Search）
# 外部API封装（NewsAPI、Google Search）
## 定义：
### 1. 概念

把外部 API 封装成你项目里的一个“标准能力模块”，通常要做到：

1. 统一接口（Interface）
```text
例如所有接口都实现：search(query, **kwargs) -> List[SearchItem]
```

2. 配置外置（Config）
```text
API_KEY / BASE_URL / 超时 / 重试 / 限流 / 代理 走环境变量或配置文件，不写死
```

3. 错误处理（Resilience）

- 超时、网络错误

- 401/403（key/权限）

- 429（限流）

  - 5xx（对端故障）
    - 做好：重试、退避、降级（fallback）

4. 结果标准化（Normalization）
```text
不同供应商字段不同：统一成你自己的 SearchResult(title, url, snippet, source, published_at) 结构
```

5. 可观测（Observability）
```text
打日志：请求耗时、命中数、失败原因、配额信息（若对端给 header）
```

6. 成本控制（Cost & Rate limit）
```text
1. 缓存（相同 query 一段时间内不重复请求）

2. 截断（限制返回条数）

3. 只在需要时调用（Router/Agent decision）
```

---

### 2. NewsAPI 与 Google Search 各适合做什么？
#### NewsAPI（新闻聚合/检索）
[官方文档](https://newsapi.org/docs/endpoints/everything?utm_source=chatgpt.com)

典型用法是用 /v2/everything 做关键词检索，支持 q、language、sortBy、from/to、分页等。

注意：NewsAPI 的 Developer 计划通常仅允许开发/测试环境使用，生产要换付费计划（条款要注意）。 

#### Google Search（网页搜索）
[官方文档](https://serper.dev/?utm_source=chatgpt.com)
官方路线一般是 Programmable Search Engine（原 CSE）+ Custom Search JSON API：你需要先创建 Search Engine，然后用 cx（search engine id）+ API key 调接口。 

工程上很多人也会用第三方 SERP API（如 Serper/SerpApi）来省去一些麻烦，但是否合规、成本与稳定性要你自己评估。 

---

### 3. Demo：封装两个外部 API → 变成 Agent 的 Tools

#### 3.1 安装依赖

    pip install -U httpx pydantic langgraph langchain-openai langchain-core

#### 3.2 配置环境变量（.env）
```python

# LLM
OPENAI_API_KEY=sk-xxx
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
OPENAI_MODEL=qwen-plus-latest

# NewsAPI
NEWSAPI_KEY=your_newsapi_key

# Google Custom Search JSON API
GOOGLE_API_KEY=your_google_api_key
GOOGLE_CSE_CX=your_cx

```

#### 3.3 代码：external_api_tools_demo.py
```python
import os
import time
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import httpx

from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent


# --------- 1) 统一数据结构（标准化输出）---------
class SearchItem(BaseModel):
    title: str
    url: str
    snippet: str = ""
    source: str = ""
    published_at: str = ""


# --------- 2) 通用 HTTP 客户端：超时 + 重试 + 退避 ---------
class ResilientHttp:
    def __init__(self, timeout_s: float = 15.0, max_retries: int = 3):
        self.timeout_s = timeout_s
        self.max_retries = max_retries
        self.client = httpx.Client(timeout=timeout_s)

    def get(self, url: str, params: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> httpx.Response:
        last_exc = None
        for i in range(self.max_retries):
            try:
                r = self.client.get(url, params=params, headers=headers)
                # 429/5xx 做退避重试
                if r.status_code in (429, 500, 502, 503, 504) and i < self.max_retries - 1:
                    time.sleep(0.8 * (2 ** i))
                    continue
                r.raise_for_status()
                return r
            except Exception as e:
                last_exc = e
                if i < self.max_retries - 1:
                    time.sleep(0.8 * (2 ** i))
                else:
                    raise last_exc


# --------- 3) NewsAPI 封装 ---------
class NewsAPIClient:
    def __init__(self, api_key: str, base_url: str = "https://newsapi.org"):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.http = ResilientHttp()

    def search_everything(self, q: str, language: str = "zh", page_size: int = 5, sort_by: str = "publishedAt") -> List[SearchItem]:
        url = f"{self.base_url}/v2/everything"
        params = {
            "q": q,
            "language": language,
            "pageSize": page_size,
            "sortBy": sort_by,
            "apiKey": self.api_key,
        }
        data = self.http.get(url, params=params).json()
        items = []
        for a in data.get("articles", [])[:page_size]:
            items.append(SearchItem(
                title=a.get("title", ""),
                url=a.get("url", ""),
                snippet=a.get("description", "") or "",
                source=(a.get("source") or {}).get("name", "") or "",
                published_at=a.get("publishedAt", "") or "",
            ))
        return items


# --------- 4) Google Custom Search JSON API 封装 ---------
class GoogleCSEClient:
    def __init__(self, api_key: str, cx: str, base_url: str = "https://www.googleapis.com/customsearch/v1"):
        self.api_key = api_key
        self.cx = cx
        self.base_url = base_url
        self.http = ResilientHttp()

    def search(self, q: str, num: int = 5, lr: Optional[str] = None) -> List[SearchItem]:
        params = {
            "key": self.api_key,
            "cx": self.cx,
            "q": q,
            "num": min(max(num, 1), 10),
        }
        if lr:
            params["lr"] = lr  # 例如 lr="lang_zh-CN"（按需）
        data = self.http.get(self.base_url, params=params).json()
        items = []
        for it in data.get("items", [])[: num]:
            items.append(SearchItem(
                title=it.get("title", ""),
                url=it.get("link", ""),
                snippet=it.get("snippet", "") or "",
                source="GoogleCSE",
                published_at="",
            ))
        return items


def format_items(items: List[SearchItem]) -> str:
    if not items:
        return "未找到结果。"
    lines = []
    for i, x in enumerate(items, 1):
        lines.append(f"{i}. {x.title}\n   - {x.url}\n   - {x.snippet}\n   - source={x.source} time={x.published_at}".strip())
    return "\n".join(lines)


# --------- 5) 把外部 API 变成 Agent Tools ---------
def main():
    # LLM（DashScope OpenAI compatible）
    llm = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "qwen-plus-latest"),
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL"),
        temperature=0.2,
    )

    news_key = os.getenv("NEWSAPI_KEY", "")
    google_key = os.getenv("GOOGLE_API_KEY", "")
    google_cx = os.getenv("GOOGLE_CSE_CX", "")

    news_client = NewsAPIClient(news_key) if news_key else None
    google_client = GoogleCSEClient(google_key, google_cx) if (google_key and google_cx) else None

    def news_search_tool(query: str) -> str:
        if not news_client:
            return "NEWSAPI_KEY 未配置。"
        items = news_client.search_everything(query, language="zh", page_size=5, sort_by="publishedAt")
        return format_items(items)

    def web_search_tool(query: str) -> str:
        if not google_client:
            return "GOOGLE_API_KEY / GOOGLE_CSE_CX 未配置。"
        items = google_client.search(query, num=5)
        return format_items(items)

    tools = [
        Tool(name="NewsSearch", func=news_search_tool, description="搜索新闻（NewsAPI）并返回标题/链接/摘要"),
        Tool(name="WebSearch", func=web_search_tool, description="搜索网页（Google Custom Search JSON API）并返回标题/链接/摘要"),
    ]

    agent = create_react_agent(llm, tools)

    question = "帮我找一下最近关于“AI Agent LangGraph GraphRAG”的新闻和网页资料，各给5条，并用中文总结要点。"
    result = agent.invoke({"messages": [("user", question)]})
    print(result["messages"][-1].content)


if __name__ == "__main__":
    main()
```
