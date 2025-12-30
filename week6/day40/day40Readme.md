day40:了解agent通信与上下文共享
# Agent 通信与上下文共享

## 一、什么是 Agent 通信与上下文共享？
定义：
```text
Agent 通信 = 多个 Agent 之间交换信息
上下文共享 = 多个 Agent 基于同一份“状态 / 记忆”协作完成任务
```
用于解决多个agent之间分工协作汇总的问题

---
## 二、为什么一定需要 Agent 通信？

### ️1. 任务天然可拆分

例如：

    搜索新闻
    
    分析关系
    
    生成总结

每个 Agent 职责不同，但结果要合并。

---

### 2. Agent 需要“知道别人做了什么

例如：

    Writer Agent 不应该再去搜索
    
    Analyzer Agent 需要知道 Search Agent 找到了什么

必须通信 / 共享上下文

---

### 3. 工程可控性

    限制某个 Agent 的权限（只搜索、不生成结论）
    
    避免工具重复调用（省钱）

---

## 三、Agent 通信与上下文共享的典型方式 ⭐
### 方式 1：直接消息传递（Message Passing）
```text
Agent A → message → Agent B
```
特点：

    简单
    
    强耦合
    
    - 不适合复杂系统

适合：demo / 原型

---
### 方式 2：共享状态（Shared State）⭐⭐⭐
```text
Shared State
  ├─ search_results
  ├─ analysis
  └─ final_answer
```
特点：

    解耦
    
    易扩展
    
    ⭐LangGraph 原生支持

---
### 方式 3：黑板模式（Blackboard）
```text
Agents ⇄ Blackboard ⇄ Agents
```
特点：

    所有 Agent 只读写“公共黑板”
    
    常见于复杂多 Agent 系统

LangGraph 的 state 就是轻量黑板

---
### 方式 4：基于记忆（Memory / DB）⭐⭐⭐
特点：

    Redis / DB / VectorStore / GraphDB
    
    用于跨会话通信

适合长期 Agent（智能助理 / 任务管家）

---
## 回顾： LangGraph 中的核心概念(day37⭐⭐⭐)
### 1. State = 上下文共享的核心
```python
from typing import TypedDict, List

class AgentState(TypedDict):
    topic: str
    search_results: List[str]
    analysis: str
    final_answer: str
```
***所有 Agent 节点：***

    输入：State
    
    输出：State 的一部分

### 2. Node = 一个 Agent / 一个角色


    SearchAgent → 写 search_results
    
    AnalyzerAgent → 读 search_results，写 analysis
    
    WriterAgent → 读所有，写 final_answer
    
### 3.Edge = 通信顺序（谁先谁后）
```text
Search → Analyze → Write
```



## DEMO
```text
#requirements.txt

langchain>=0.1.0
langchain_openai
langgraph
langchain-core
```
pip install -r requirements.txt
```python
from typing import TypedDict

from langchain_openai import ChatOpenAI
from langgraph.constants import END
from langgraph.graph import StateGraph


class StoryState(TypedDict):
    text:str
    relations:str
    analysis:str
    answer:str

llm = ChatOpenAI(
    model="qwen-plus-latest",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    api_key="sk-YourKey"
)

def extractAgent(state:StoryState) -> StoryState:
    prompt =f"""
    请从以下故事中抽取人物关系：
格式：人物A - 关系 - 人物B
故事：
{state["text"]}
    """
    relations = llm.invoke(prompt).content
    return {"relations":relations}

def analyzeAgent(state:StoryState) -> StoryState:
    prompt = f"""
    根据以下人物关系，判断：
    1. 谁是核心人物？
    2. 是否存在悲剧冲突？
    关系：
    {state["relations"]}
    """
    analysis = llm.invoke(prompt).content
    return {"analysis":analysis}

def answerAgent(state:StoryState) -> StoryState:
    prompt = f"""
    根据以下分析，给出最终结论：
    {state["analysis"]}
    """
    answer = llm.invoke(prompt).content
    return {"answer":answer}

graph = StateGraph(StoryState)

graph.add_node("extractAgent", extractAgent)
graph.add_node("analyzeAgent", analyzeAgent)
graph.add_node("answerAgent", answerAgent)

graph.set_entry_point("extractAgent")
graph.add_edge("extractAgent", "analyzeAgent")
graph.add_edge("analyzeAgent", "answerAgent")
graph.add_edge("answerAgent", END)

app = graph.compile()

if __name__ == "__main__":
    result = app.invoke({
        "text": """
    张三深爱李四，但李四被迫嫁给王五。
    王五性格暴躁，经常伤害李四。
    最终张三为救李四而死。
    """
    })
    print("最终回答：", result["answer"])
# (day40venv) (base) PS D:\code\ai\week6\day40> python main.py
# 最终回答： **最终结论：**
# 
# 这是一个以**李四为核心枢纽、以结构性父权暴力为根本动因、以无解牺牲为悲剧落点的现代性社会悲剧**。
# 
# 其本质并非个人命运的偶然不幸，而是**爱情自由、个体尊严与制度性压迫（强制婚姻、家暴合法化/纵容、女性主体性消音）之间不可调和的激烈冲撞**。李四作为被争夺、被规训、被伤害却始终未被赋权言说的中心，其存在本身即是对“沉默多数”的深刻指涉；张三之死不是英 雄主义的胜利，而是善良在系统性暴力面前的悲怆溃败；王五亦非扁平恶人，而是父权制度具身化的执行者——其暴力得以持续，正因它嵌套于被默认的亲属权力结构与社会失语之中。
# 
# 因此，该关系链所呈现的，是一个**微型但尖锐的悲剧切片**：
# > **当爱成为罪证，反抗失去出口，牺牲无法撼动结构——那么最深的悲剧，不在于死亡，而在于活着的人仍困在未被拆解的牢笼里。**
# 
# ✅ 这一分析不仅确认了李四的叙事核心地位与冲突的悲剧本质，更揭示出其超越个体故事的批判力量：它叩问的，是婚姻自主权如何落实、家暴为何难以终结、以及当法律缺位、伦理失语、社会共谋时，“救一个人”为何竟成了最绝望的壮举。
# 
# ——悲剧已发生；而真正的救赎，始于拒绝将它讲述为“命运”，并敢于直视那制造悲剧的、可被改变的现实结构。

```








