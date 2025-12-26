from langgraph.prebuilt import create_react_agent
from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="qwen-plus-latest",
                 api_key="sk-YOUR-key",
                 base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                 temperature=0.7)


def summarize_text(text: str) -> str:
    prompt = f"请用不超过5句话总结以下文本：\n{text}"

    return llm.invoke(prompt).content


summary_tool = Tool(
    name="SummarizeText",
    func=summarize_text,
    description="用于对长文本进行摘要。"
)


# 人物关系抽取
def extract_relations(text: str) -> str:
    prompt = f"""
请从以下文本中抽取人物关系，用列表输出：
格式：人物A - 关系 - 人物B
文本：
{text}
"""
    return llm.invoke(prompt).content


relation_tool = Tool(
    name="ExtractRelations",
    func=extract_relations,
    description="从文本中抽取人物关系"
)

# 关系分析
def analyze_relations(relations: str) -> str:
    prompt = f"""
根据以下人物关系，判断：
1. 谁是核心人物？
2. 是否存在悲剧冲突？
关系：
{relations}
"""
    return llm.invoke(prompt).content

analysis_tool = Tool(
    name="AnalyzeRelations",
    func=analyze_relations,
    description="分析人物关系并给出判断"
)

tools = [
    Tool(name="SummarizeText",func=summarize_text,description="用于对长文本进行摘要。"),
    Tool(name="ExtractRelations",func=extract_relations,description="从文本中抽取人物关系"),
    Tool(name="AnalyzeRelations",func=analyze_relations,description="分析人物关系并给出判断")
]

agent = create_react_agent(llm,tools)

def main():
    text = """
    张三深爱李四，但李四被迫嫁给王五。
    王五性格暴躁，经常伤害李四。
    最终张三为救李四而死。
    """

    # 将文本作为输入传递给代理
    result = agent.invoke(
        {"messages": [("user", f"请分析这段故事的人物关系，并判断悲剧核心人物是谁。故事内容：{text}")]}
    )

    print(result["messages"][-1].content)

if __name__ == "__main__":
    main()

# 根据分析，悲剧核心人物是**李四**。
#
# 理由如下：
# - 所有关键关系均以她为枢纽：张三的深爱与牺牲、王五的强迫婚姻与暴力伤害，皆围绕她展开；
# - 她身陷多重结构性压迫——情感自主权被剥夺（被迫嫁）、人身安全受威胁（被伤害）、成为他人牺牲的动因（张三为其而死），却无主动解局之力；
# - 张三之死虽具强烈悲壮感，但其行为逻辑完全由对李四的爱与拯救欲驱动；王五的暴行也以李四为直接对象。因此，李四是悲剧能量的汇聚点与承受体，是命运不可逆性的最深刻体现。
#
# ✅ 结论明确：**李四为本故事的悲剧核心人物。**