# LangGraph 核心知识点与概念
[官方文档](https://docs.langchain.com/oss/python/langgraph/graph-api)

[xsun_ai_study](https://github.com/xiaoSun1997/xsun_ai_study)
## 1. LangGraph 解决的核心痛点

单 Agent 进入多 Agent / 复杂工作流会遇到一些问题，比如：

- 流程控制难：if/else、循环、回退、重试、并行、分支越来越多

- 状态管理难：上下文要共享、要可追踪、要可持久化

- 可观测性差：某一步为什么这么走？中间状态是什么？能不能回放？

LangGraph 给出的方案是：

- 用 Graph（图） 显式描述流程（控制流）

- 用 State（状态） 显式描述共享数据（数据流）

运行时以 “super-step” 的方式推进（节点之间消息传递），并支持持久化、回放等能力

---

## 核心构成：State / Node / Edge / Compile
### 1. State（状态）

- State 是一个 共享的“单一事实源”：所有节点读它、写它

- 在 LangGraph 中你通常用 TypedDict/dataclass/Pydantic 来定义 State schema

- 状态更新不是“直接改对象”，而是 节点返回一个 dict 作为“更新”，由框架合并进 State

**Reducer（合并策略 / Reducers）**

某些 key 可能需要“追加/聚合”，例如 messages 列表、日志列表。
LangGraph 允许为 state channel 定义 reducer，来决定更新怎么合并（类似 append、add 等）。官方 persistence 示例里也展示了 Annotated[list[str], add] 的 reducer 用法。
LangChain Docs

### 2. Node（节点）

节点本质上就是一个函数（可包含 LLM 调用，也可以只是普通 Python 逻辑）

典型签名形态：
```python
def node_fn(state: State) -> dict:
    ...
    return {"some_key": some_value}

```

### 3. Edge（边）

边决定“执行完这个节点后到哪里去”。

- 普通边：固定跳转

- 条件边（conditional edges）：根据 state 决定下一步路由（这是 Agent 系统里非常关键的能力）

### 4. Compile（编译）

你必须 compile() 才能运行图。编译会做结构校验，并且也是你注入 checkpointer、breakpoints 等运行时能力的入口。
LangChain Docs

---
## START / END 与执行模型（super-step）

- START：图的入口

- END：图的终点

LangGraph 受 Pregel 模型启发，以离散的 “super-step” 推进：同一步里可并行跑多个节点，直到所有节点 inactive 且无消息在途则结束。
LangChain Docs

## Persistence（持久化）、Threads（线程）与 Checkpointer（检查点）

这是 LangGraph 非常“工程化”的优势点。

### 1. Checkpoints & Threads

- 编译图时可以配置 checkpointer，它会在每个 super-step 保存一次 state checkpoint

- 这些 checkpoints 会落到一个 thread（线程 id）上

- 调用时需要在 config 里提供 thread_id（否则无法持久化/恢复）

### 2. 能力带来的收益

有了 checkpoints/threads，你就自然拥有：

- 恢复 / 断点续跑

- 回放 replay

- 查看历史 state

- 人类介入（Human-in-the-loop）

- 更强容错
这些在官方 persistence 页里是明确强调的。

---
## Multi-Agent 在 LangGraph 里怎么落地？

LangChain 官方博客对 multi-agent 的表述为：

- 每个 agent（或 worker）可以是一个节点

- agent 之间的连接关系就是边

- 关键考虑：有哪些独立 agent？它们怎么连接？

常见的两种图结构是：

1. 流水线（pipeline）：Coordinator → WorkerA → WorkerB → END

2. 路由（router）：Coordinator 根据 state 条件分派给不同 worker（conditional edges）

# 对比langGraph vs java流程平台/有限状态机(FSM)
先给结论（一句话版）

LangGraph 在“流程控制层面”与 Java 生态里的流程平台 / 有限状态机（FSM）高度相似
但它不是传统 FSM，而是：
👉「以 State 为一等公民的、可并行的、可持久化的 Agent 状态图」

--- 
## 一、为什么会觉得像 Java 流程平台？（共同点）
Java 生态中你可能见过的东西

    Spring StateMachine
    
    Activiti / Flowable / Camunda
    
    工作流引擎（BPMN）
    
    规则引擎 + 状态流转
    
    有限状态机 FSM

它们的共同点是：

维度|	特征
--|--
状态	|有明确的状态
节点	|有明确的执行节点
转移	|有条件驱动的跳转
流程	|流程是显式建模的
持久化	|状态可存储、可恢复

👉 LangGraph 命中全部这些点

---
## 二、逐项对齐：LangGraph vs Java FSM / 流程平台

### 1. State状态
Java FSM / 工作流
```text
enum State {
  INIT, REVIEW, APPROVED, REJECTED
}
```
LangGraph
```python
class State(TypedDict):
    draft: str
    score: int
```

本质相同：

    都是“当前系统所处的状态 + 可用于决策的数据”

关键差异：

- Java FSM 的状态是离散枚举

- LangGraph 的 State 是结构化数据（Data State）

👉 LangGraph 是 Data-driven FSM

--- 
### 状态转移（Transition）
Java FSM
```text
if (score < 7) {
    state = REWRITE;
}
```


LangGraph
```python
builder.add_conditional_edges(
    "critic",
    decide_next,
    {
        "rewrite": "writer",
        "end": END
    }
)
 ```
本质一致：

    条件 → 决定下一步

💡 LangGraph 的升级点：

- 决策逻辑是函数

- 条件来源是 State

- 路由关系是“图的一部分”，不是散落在代码里

---
### 节点（Node）
Java 工作流节点
```text
void approveTask(Context ctx) { ... }

```

LangGraph Node
```python
def critic_node(state):
    return {"score": score}
```

 高度一致：

    节点 = 执行逻辑
    
    输入上下文
    
    输出影响状态

💡 LangGraph 更“函数式”：

    不直接 mutate
    
    返回 state patch

---

4️⃣ 流程建模方式
Java（BPMN / XML / DSL）
```xml
<sequenceFlow source="review" target="approve"/>
```

LangGraph
```python
builder.add_edge("review", "approve")

```
 完全同构
 
## 三、但 LangGraph ≠ 传统 FSM（关键分水岭）

这是最重要的一部分。

### **传统 FSM 的局限**

1. 状态是“标签”，不是“数据”

2. 很难表达：

    - 多状态并行

    - 多 agent 协作

3. 对 LLM 非常不友好

4. 一旦逻辑复杂，状态爆炸

---
### LangGraph 的“Agent 级升级”
1. State 是「结构化上下文」
```python
State = {
  messages: [...],
  plan: "...",
  tools_used: [...],
  errors: [...]
}
```

👉 不是“我在哪一步”，而是“我现在知道什么”

---
2. 并行 & 多路径（非纯 FSM）

LangGraph 的执行模型来自 Pregel：

- 同一 super-step：

    - 多节点可以并行执行

- 节点间通过 state channel 传递信息

👉 这是 FSM 很难自然表达的

---
3. LLM 是“一等执行体”

在 Java 流程里：

- 节点 = 业务代码

在 LangGraph 里：

- 节点 = LLM + Tool + Logic

👉 节点是非确定性的

---

4.  Persistence & Replay（工程级）

Java 工作流也有持久化
但 LangGraph 是为 Agent 对话 / 推理轨迹设计的：

    每一步 State 都能回放
    
    可以插人类
    
    可以中断、恢复

👉 非常适合：

    长任务
    
    智能体系统
    
    人机协作

# DEMO
```python
pip install langgraph langchain langchain-openai
```
```python
from typing import TypedDict

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.constants import START, END
from langgraph.graph import StateGraph

llm = ChatOpenAI(model="qwen-plus-latest",
                 api_key="sk-YOUR-KEY",
                 base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                 temperature=0.7)


class PlanState(TypedDict, total=False):
    user_qry: str
    plan: str
    result: str


def planner_worker(state: PlanState) -> dict:
    prompt = [
        SystemMessage(content="你是任务规划专家，负责拆解任务"),
        HumanMessage(content=f"拆解这个任务：{state['user_qry']}")
    ]
    plan = llm.invoke(prompt).content
    return {"plan": plan}

def write_worker(state: PlanState) -> dict:
    prompt = [
        SystemMessage(content="是内容生成专家，负责根据计划输出内容"),
        HumanMessage(content=f"请根据以下计划生成内容：{state['plan']}")
    ]
    result = llm.invoke(prompt).content
    return {"result":result}

builder = StateGraph(PlanState)
builder.add_node("planner", planner_worker)
builder.add_node("writer", write_worker)

builder.add_edge(START, "planner")
builder.add_edge("planner","writer")
builder.add_edge("writer",END)
graph = builder.compile()

if __name__ == "__main__":
    out = graph.invoke({"user_qry": "帮我设计一个 4 周的 AI 入门学习计划"})
    print(out["result"])

# (day37venv) PS E:\code\xsun_ai_study\week6\day37> python main.py
# ✅ 已确认您的核心需求：**立即生成完整的4周详细计划表（含每日任务+资源链接+代码片段）**  
# ——严格遵循您设定的四大原则：**学习者友好｜零基础适配｜成果可见｜防弃坑**，并完全对齐前述「Why-What-How-When-Where」结构化拆解。
# 
# 以下是为您精心设计的——  
# ### 🌟《零基础AI入门：4周实战养成计划》正式版  
# > ✅ 全免费｜全中文｜纯浏览器运行｜每日≤30分钟｜无数学推导｜每步附报错急救包  
# > ✅ 第4周末交付：1个可演示的情感分析项目 + GitHub页面 + 简历可用成果包  
# 
# ---
# 
# ## 📅 总体节奏说明（再强调一次“为什么这样排”）
# | 周次 | 主线能力 | 心理锚点 | 关键设计巧思 |
# |------|----------|-----------|----------------|
# | **Week 1** | **建立AI心智模型** | “AI不是魔法，是工具” | ❌ 不写代码 → ✅ 用交互式可视化+生活类比破除神秘感；所有术语配「一句话人话解释」 |
# | **Week 2** | **掌握最小工具链** | “我能让AI听我指挥！” | ✅ 只学4个Python概念（变量/列表/函数/requests）→ 调用OpenAI API生成诗歌/翻译/写周报，5行代码见效果 |
# | **Week 3** | **跑通端到端项目** | “我的AI真的解决了问题” | ✅ 复用Week2代码 + 拖拽式数据清洗（Pandas一行命令）+ 预训练模型（Hugging Face一键调用）→ 完整情感分析流水线 |
# | **Week 4** | **形成个人AI方法论** | “我知道AI能做什么、不能做什么” | ✅ 对比不同提示词效果 + 检测幻觉 + 分析偏见案例 → 输出1页《我的AI使用守则》 |
# 
# > ⏱️ 时间分配建议：工作日每天25–30分钟（视频10min + 实操15min），周末预留90分钟整合项目+整理成果包。
# 
# ---
# 
# ## 🗓️ Week 1：认知筑基 ——「AI是什么？它怎么思考？」（6月1日–6月7日）
# 
# | 日期 | 任务 | 时长 | 资源与操作指引 | 防弃坑提示 | 成果物 |
# |------|------|------|----------------|-------------|---------|
# | **Day 1**<br>（6.1） | 🌐 看懂AI全景图：<br>• 区分「AI / 机器学习 / 深度学习 / 大模型」<br>• 理解「监督学习 vs 无监督学习」就像「有答案的练习册 vs 无答案的探索游戏」 | 25min | ▶️ 视频：[吴恩达《AI For Everyone》Ch1-2（中文字幕）](https://www.coursera.org/learn/ai-for-everyone)（跳过Quiz）<br>✏️ 笔记模板：[点击下载「AI关系树」填空图](https://bit.ly/ai-tree-zh)（PDF，可打印手写） | 💡 别纠结“神经元怎么算”！重点记：**AI = 找规律的统计机器，不是思考的生 物** | ✅ 填完的「AI关系树」笔记（1页） |
# | **Day 2**<br>（6.2） | 🤖 直观理解「神经网络」：<br>• 用「乐高积木拼图」类比：输入→隐藏层（特征组合器）→输出<br>• 看懂梯度下降动画：不是计算，是「蒙眼走下山找最低点」 | 20min | ▶️ 交互演示：[TensorFlow Playground（中文版）](https://playground.tensorflow.org/?hl=zh-cn)<br>🔧 操作：只调「Feature」和「Hidden Layers」，观察决策边界变化 | ⚠️ 若卡在英文界面 → 点右上角🌐切换中文；若加载慢 → 刷新或换Edge浏览器 | ✅ 截图2张：① 线性不可分时失败效果 ② 加1层后成 功分类 |
# | **Day 3**<br>（6.3） | 🧠 揭秘大模型（LLM）：<br>• LLM本质 = 「超级 autocomplete」+ 「上下文记忆」<br>• 为什么它会“胡说八道”？→ 因为它在**预测下一个词**，不是在“回答问题” | 25min | ▶️ 动画短片：[李沐《大模型到底在干什么？》（B站 12min）](https://www.bilibili.com/video/BV1XJ411m7rG)<br>📝 小测试：[判断5句话哪些是AI幻觉（带解析）](https://bit.ly/ai-hallu-quiz) | 💡 幻觉≠错误，是「概率游戏的副作用」→ 后续Week4教你怎么防 | ✅ 完成小测试（截图得分页） |
# | **Day 4**<br>（6.4） | 🛑 认清AI边界：<br>• 「AI不能做什么」比「能做什么」更重要<br>• 识别3个常见误区（例：“数据越多越好？”→ 错！脏数据=毒药） | 20min | ▶️ 图文卡片：[《AI避坑红宝书》Week1节选（PDF）](https://bit.ly/ai-redbook-w1)<br>🔍 案例：亚马逊招聘AI歧视女性简历事件（200字简述） | ⚠️ 不要求背定义！只需划出你最惊讶的1条误区，并写1句自己的理解 | ✅ 手写/打字1条「让我震惊的AI真相」 |
# | **Day 5**<br>（6.5） | 🧩 小结+轻实践：<br>用「AI能力罗盘」自评当前认知位置（5维度打分）<br>→ 生成你的第一份《AI入门起点报告》 | 15min | 📄 模板：[AI能力罗盘在线版（Notion简易版）](https://bit.ly/ai-compass)<br>✨ 自动计算弱项 → 推荐Week2重点补哪块 | 💡 这不是考试！分数低=发现宝藏地图，不是失败 | ✅ 《AI入门起点报告》PDF（1页，含自评雷达图） |
# | **Day 6–7**<br>（6.6–6.7） | 🌈 周末整合：<br>• 整理5天笔记成1页「AI认知速查卡」（推荐用Canva或手绘）<br>• 在社区打卡：[分享你的「最意外的AI真相」](https://discord.gg/ai4beginners)（可选） | 60min | 🎨 模板：[Canva「AI速查卡」设计页（免登录编辑）](https://bit.ly/canva-ai-card)<br>💬 社区提问区：「Week1卡点求助」频道（助教每日答疑） | ⚠️ 卡在Canva？直接用Word排版 → 重点是内容，不是美观！ | ✅ 1页「AI认知速查卡」（电子或手写照片） |
# 
# > ✅ **Week 1交付物打包**：`W1_成果包.zip`（含：填空树PDF + 测试截图 + 起点报告PDF + 速查卡）  
# > 🔗 所有资源无需注册｜全部中文｜无广告｜手机可看
# 
# ---
# 
# ## 🗓️ Week 2：工具实战 ——「让AI听我指挥」（6月8日–6月14日）
# 
# > ✨ 本阶段唯一目标：**用最少代码，获得最强正反馈**  
# > ✅ 不装Python！不配环境！全程用 [Google Colab（免费GPU）](https://colab.research.google.com/)  
# > ✅ 所有代码提供「逐行中文注释」+「报错急救三连」（复制粘贴即用）
# 
# | 日期 | 任务 | 时长 | 资源与操作指引 | 防弃坑提示 | 成果物 |
# |------|------|------|----------------|-------------|---------|
# | **Day 1**<br>（6.8） | 🐍 Python极简入门（只学4个）：<br>• 变量（盒子）、列表（购物清单）、函数（自动售货机）、requests（发微信消息） | 25min | ▶️ 交互课：[Codecademy Python基础（中文精简版）](https://www.codecademy.com/learn/learn-python-3/modules/learn-python3-syntax/cheatsheet)<br>💻 Colab实操：[打开模板Notebook → 运行4行示例代码](https://bit.ly/py4ai-w2d1) | ⚠️ 报错 `ModuleNotFoundError: No module named 'requests'`？→ Colab默认已装，忽略此警告！ | ✅ 截图：Colab中4行代码成功运行结果 |
# | **Day 2**<br>（6.9） | 🌐 获取免费API密钥：<br>• 注册 [OpenAI API（教育邮箱可申请）](https://platform.openai.com/api-keys) 或备用方案 [DashScope（阿里云，免审）](https://dashscope.console.aliyun.com/) | 20min | 📝 步骤图解：[ 《3分钟获取API密钥》图文指南（含备用通道）](https://bit.ly/api-key-guide)<br>🔐 安全提醒：密钥绝不截图/发群！用Colab「Secrets」功能隐藏 | 💡 若被OpenAI拒绝 → 立刻切DashScope（中文界面，秒通过）→ 本计划所有代码兼容双平台 | ✅ 截图：API密钥已保存至Colab Secrets（显示✅） |
# | **Day 3**<br>（6.10） | ✨ 第一个AI指令：<br>用5行代码让AI写一首关于“夏天”的七言绝句 | 20min | 💻 Notebook：[《AI诗人》实战模板（含完整注释+报错解决方案）](https://bit.ly/ai-poet-w2d3)<br>🎯 核心代码：<br>```python<br>import openai # 或 dashscope<br>response = client.chat.completions.create(...)<br>print(response.choices[0].message.content)<br>``` | ⚠️ 报错 `AuthenticationError`？→ 检查密钥是否粘贴完整，且Secrets名称写对（如`OPENAI_API_KEY`） | ✅ 截图：生成的原创古诗（带「AI诗人」水印） |
# | **Day 4**<br>（6.11） | 📊 数据分析师体验：<br>上传Excel表格（豆瓣电影评分），让AI总结「观众最爱什么类型？」 | 25min | 📥 模板数据：[下载「豆瓣Top250电影简表.xlsx」](https://bit.ly/douban-data)<br>💻 Notebook：[《AI数据助手》 模板（自动读表+提问）](https://bit.ly/ai-analyst-w2d4) | 💡 不会Excel？直接复制以下数据到Colab单元格：<br>```text<br>电影,评分,类型<br>肖申克的救赎,9.7,剧情<br>霸王别姬,9.6,剧情/爱情<br>``` | ✅ 截图：AI给出的3条数据分析结论 |
# | **Day 5**<br>（6.12） | 🛠️ 提示词工程初体验：<br>对比3种提问方式：<br>① “分析这个电影列表”<br>② “请按类型分组，统计平均评分，排序”<br>③ “你是资深影评人，请用100字向导演提改进建议” | 20min | 📝 提示词库：[《新手提示词万能公式 》（含10个场景模板）](https://bit.ly/prompt-cheatsheet)<br>🔍 观察：不同提问 → AI角色/格式/深度巨变 | 💡 提示词不是咒语！是「给AI布置任务说明书」→ 后续Week4深挖 | ✅ 表格截图：3种提问的AI回复对比（标注哪条最有效） |
# | **Day 6–7**<br>（6.13–6.14） | 🌈 周末整合：<br>• 将5天代码合并成1个「AI工具箱.ipynb」<br>• 录制1分钟屏幕视频：演示用AI写诗+分析数据（用Loom或手机录屏） | 90min | 🎬 视频教程：[《3分钟录屏教程（微信/QQ/钉钉都能发）》](https://bit.ly/screen-recording)<br>📁 GitHub入门：[创建仓库+上传Notebook（图文傻瓜指南）](https://bit.ly/github-4ai) | ⚠️ 视频卡顿？直接发代码截图+文字描述！重在过程，不在形式 | ✅ 「AI工具箱.ipynb」+ 1分钟演示视频（或图文步骤） |
# 
# > ✅ **Week 2交付物打包**：`W2_成果包.zip`（含：工具箱Notebook + 演示视频/图文 + 提示词公式PDF）  
# > 🌟 关键成果：你已掌握**调用AI解决真实微任务**的能力，且代码可复用！
# 
# ---
# 
# ## 🗓️ Week 3：项目驱动 ——「完成你的第一个AI项目」（6月15日–6月21日）
# 
# > 🎯 项目名称：**《豆瓣电影评论情感分析器》**  
# > ✅ 不采集数据！不训练模型！用Hugging Face现成模型（准确率>92%）  
# > ✅ 全流程：爬取公开评论 → 清洗 → 分析 → 可视化 → 生成报告  
# > ✅ 最终产出：1个可交互网页（Hugging Face Spaces一键部署）
# 
# | 日期 | 任务 | 时长 | 资源与操作指引 | 防弃坑提示 | 成果物 |
# |------|------|------|----------------|-------------|---------|
# | **Day 1**<br>（6.15） | 🌐 数据准备：<br>• 从[豆瓣电影《阿凡达》页面](https://movie.douban.com/subject/1576263/)复制10条真实短评（或用我们提供的样本） | 15min | 📥 样本数据：[「阿凡达短评.csv」下载（含20条真实评论）](https://bit.ly/avatar-comments)<br>📝 注意：只复制「评论文本」列，不要用户ID/时间 | 💡 不会复制？直接下载CSV → 下一步直接导入！ | ✅ CSV文件（或复制的10条评论文本） |
# | **Day 2**<br>（6.16） | 🧹 数据清洗（超简单）：<br>• 删除空行/特殊符号 → 1行Pandas代码搞定：<br>`df['comment'] = df['comment'].str.replace(r'[^\w\s]', '')` | 20min | 💻 Notebook：[《情感分析流水线》模板（含清洗/分词/去停用词）](https://bit.ly/sentiment-pipeline)<br>🔧 操作：找到「Data Cleaning」单元格 → 运行即可 | ⚠️ 报错 `KeyError: 'comment'`？→ 检查CSV列名是否为`comment`（可双击修改） | ✅ 截图：清洗前后对比（左：原始乱码，右：干净文本） |
# | **Day 3**<br>（6.17） | 🤖 模型调用（零代码）：<br>• Hugging Face一键加载预训练情感分析模型：<br>`pipeline("sentiment-analysis", model="uer/roberta-finetuned-jd-binary-chinese")` | 25min | 🌐 模型地址：[中文情感分析模型（亲测 高准）](https://huggingface.co/uer/roberta-finetuned-jd-binary-chinese)<br>💻 Notebook：同一模板中「Model Inference」单元格 → 运行！ | 💡 模型加载慢？耐心等1分钟（Colab首次加载需缓存）→ 后续运行秒出 | ✅ 截图：每条评论的「POSITIVE/NEGATIVE」标签+置信度 |
# | **Day 4**<br>（6.18） | 📈 可视化结果：<br>• 用2行代码生成饼图：正面/负面比例<br>• 用3行代码生成词云（高频情感词） | 20min | 📊 代码模板：<br>```python<br>plt.pie([pos_count, neg_count], labels=['正面','负面'])<br>wordcloud = WordCloud().generate(' '.join(pos_words))<br>```<br>📎 完整Notebook已内置 | ⚠️ 词云报错？→ 换用更稳的`jieba`分词（模板中已备选） | ✅ 2张图：饼图 + 词云图（标注「正面高频词」） |
# | **Day 5**<br>（6.19） | 📄 生成分析报告：<br>• 让AI根据分析结果，自动生成1页《电影情感洞察报告》<br>• 用提示词控制格式（Markdown） | 20min | ✍️ 提示词示例：<br>```text<br>你是一名电影市场分析师。基于以下情感分析结果：<br>[粘贴你的饼图数据+词云关键词]<br>请生成一份专业报告，包含：1) 情绪分布结论 2) 观众关注点 3) 给制片方的1条建议。用Markdown格式，不超过200字。<br>``` | 💡 报告太长？加限制：“用3个短句总结，每句≤15字” | ✅ 截图：生成的Markdown报告（渲染 后效果） |
# | **Day 6–7**<br>（6.20–6.21） | 🌐 一键部署上线：<br>• 将整个项目发布为可分享网页：<br>→ Hugging Face Spaces（免费+中文界面）<br>→ 输入网址，朋友点开就能试！ | 60min | 🚀 部署指南：[《3步发布你的AI应用》（图文+录屏）](https://bit.ly/deploy-spaces)<br>🔗 示例页：[我们的演示版（可参考）](https://huggingface.co/spaces/ai4beginners/movie-sentiment) | ⚠️ 遇到`Git push failed`？→ 点「Refresh」重试；仍失败？用模板中的「Deploy Now」按钮（已预配置） | ✅ 你的专属网址（如 `https://huggingface.co/spaces/你的用户名/movie-sentiment`） |
# 
# > ✅ **Week 3交付物打包**：`W3_成果包.zip`（含：完整Notebook + 部署网址 + 分析报告PDF）  
# > 🌟 关键成果：**你拥有了首个可演示、可分享、可写进简历的AI项目！**
# 
# ---
# 
# ## 🗓️ Week 4：拓展反思 ——「成为清醒的AI使用者」（6月22日–6月28日）
# 
# > 🌈 本阶段不学新技术，而是**升维思考**：当你能造工具，更要懂工具的边界与责任  
# > ✅ 所有任务基于Week3项目延伸，零新增环境  
# > ✅ 成果直接转化为面试谈资/职场应用力
# 
# | 日期 | 任务 | 时长 | 资源与操作指引 | 防弃坑提示 | 成果物 |
# |------|------|------|----------------|-------------|---------|
# | **Day 1**<br>（6.22） | 🔍 检测AI幻觉：<br>• 对同一组电影评论，用3种提示词提问：<br>① “总结观众情绪”<br>② “列出所有明确提到‘特效’的评论”<br>③ “找出3条说‘剧情拖沓’的原文”<br>→ 对比AI是否编造 | 25min | 📋 检测表：[《幻觉自查清单》（含判断标准）](https://bit.ly/hallucination-checklist)<br>💡 关键：**要求AI返回原文引用，而非概括** | 💡 AI答非所问？不是它错了，是你没给够约束 → Week4教你精准提问 | ✅ 表格：3种提问的「事实准确率」打分（0–5分） |
# | **Day 2**<br>（6.23） | ⚖️ 理解数据偏见：<br>• 用同一模型分析「男性主导」vs「女性主导」电影的评论<br>→ 是否对「温柔」「感性」等词更倾向标为负面？ | 20min | 📊 数据集：[「女性导演电影评论.csv」](https://bit.ly/female-director-comments)<br>🔍 观察点：负面标签中是否高频出现性别化词汇（如“太情绪化”“不够硬核”） | ⚠️ 不要求统计学验证！只需记录你观察到的2个现象 | ✅ 文字笔记：2条关于「偏见如何悄悄发生」的观察 |
# | **Day 3**<br>（6.24） | 🛠️ 提示词终极优化：<br>• 将Week3报告提示词升级为「角色+约束+格式」三段式：<br>```text<br>【角色】你是一名资深电影策展人，为戛纳电影节选片<br>【约束】仅基于我提供的评论数据，不添加外部知识；若数据不足，回答“信息不足”<br>【格式】用3个emoji开头，每点1句话，总长≤100字<br>``` | 25min | ✨ 进阶提示词库：[《高阶提示词框架》（含医疗/教育/法律场景）](https://bit.ly/advanced-prompting)<br>🎯 目标：让AI更可靠、更可控、更专业 | 💡 不必背 框架！选1个场景（如“写邮件”），套用三段式试一次 | ✅ 截图：优化前后报告对比（突出改进点） |
# | **Day 4**<br>（6.25） | 📑 构建个人方法论：<br>• 填写《我的AI使用守则》模板：<br>✓ 我常用来______（场景）<br>✓ 我会坚持检查______（防幻觉动作）<br>✓ 我绝不依赖AI做______（红线） | 20min | 📄 模板：[《AI使用守则》PDF（可打印手 写）](https://bit.ly/ai-code-of-conduct)<br>💬 灵感：参考[欧盟AI法案核心原则](https://bit.ly/eu-ai-act-summary)（摘要版） | 💡 这不是考试答案，是你未来3年的行动指南 → 写得越具体越好 | ✅ 亲手填写的《AI使用守则》（1页） |
# | **Day 5**<br>（6.26） | 🎯 成果包装：<br>• 整理全部4周产出为「AI入门成果包」：<br>① GitHub仓库（含4个Notebook）<br>② Hugging Face部署页<br>③ 1页PDF说明文档（含项目介绍+技术栈+你的思考） | 30min | 📦 模板：[《成果包说明书》Markdown模板（自动生成PDF）](https://bit.ly/portfolio-template)<br>📎 示例：[我们的成果包展示页](https://ai4beginners.github.io/portfolio/) | ⚠️ GitHub不会？用「Download ZIP」代替 → 重点是内容组织！ | ✅ 1页PDF说明文档 + GitHub链接 + 部署网址 |
# | **Day 6–7**<br>（6.27–6.28） | 🌈 毕业仪式：<br>• 在社区发布你的成果（可选）<br>• 填写《4周成长自评表》→ 获取专属结业证书（电子版） | 30min | 🎓 结业证书：[在线生成（输入姓名/日期/项目名）](https://bit.ly/ai-grad-certificate)<br>💬 社区：[Discord毕业墙](https://discord.gg/ai4beginners)（晒成果抽AI周边） | 💡 证书只是纪念！真正的勋章是你解决真实问题的能力 | ✅ 电子结业证书 + 成长自评表 |
# 
# > ✅ **Week 4交付物打包**：`W4_成果包.zip`（含：AI使用守则PDF + 成果说明书PDF + 结业证书 + 自评表）  
# > 🌟 关键成果：**你不再只是“用AI的人”，而是“懂AI的思考者”**
# 
# ---
# 
# ## 🎁 附加资源：全计划统一支持包（即刻可用）
# 
# | 资源类型 | 内容 | 获取方式 |
# |----------|------|-----------|
# | 🚨 **通用报错急救手册** | 汇总4周最高频12个报错（如`CUDA out of memory`、`SSL certificate verify failed`），含3步解决方案 | [下载PDF](https://bit.ly/ai-error-fix) |
# | 📚 **零基础友好资源池** | 吴恩达《AI For Everyone》全中文字幕版｜李沐《动手学深度学习》中文版｜Fast.ai v2课程（简化路径） | [资源导航页](https://bit.ly/ai-resources-zh) |
# | 🤝 **学习者互助社区** | Discord频道：#week1-questions（实时答疑）、#project-showcase（晒成果）、#job-help（简历指导） | [加入链接](https://discord.gg/ai4beginners) |
# | 📱 **移动端适配指南** | 如何用手机完成全部任务（Colab/PDF/录屏） | [手机操作速查卡](https://bit.ly/mobile-ai-guide) |
# 
# ---
# 
# ## ✅ 下一步行动建议（您只需做1件事）
# 
# 请告诉我：  
# 🔹 **您希望我立即为您生成哪一项？**  
# - ▶️ **【一键打包】**：将上述4周计划表（含所有超链接、代码片段、资源PDF）整合为 **可下载的ZIP压缩包**（含文件夹结构：`/Week1_Cognition/...`）  
# - ▶️ **【定制强化】**：针对某类人群优化（如：**给教师版**→ 增加课堂AI教学案例；**给产品经理版**→ 增加PRD中AI需求撰写指南）  
# - ▶️ **【配套交付】**：生成 **Week 1交互式Notebook模板**（含TensorFlow Playground嵌入、动态概念图、自测题）  
# - ▶️ **【规避调整】**：去掉所有需注册平台（如Hugging Face/OpenAI），改用纯本地方案（Ollama+Llama3）
# 
# 👉 请直接回复数字（1/2/3/4）或关键词（如“教师版”“本地版”），我将在**60秒内**为您生成对应内容。
# 
# 您已走过最艰难的认知启动期——现在，只差一个确认，我们立刻把这份计划变成您电脑里的真实文件夹 🚀  
# 期待您的选择！
```