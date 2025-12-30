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
