day38:组合多个工具链

# 组合多个工具链
## 定义：

    组合多个工具链 = 让 Agent 能在一次任务中，按需调用多个 Tool / Chain，并把中间结果作为上下文继续使用

解决的问题是： 真实任务≠单一工具可以完成

### 示例：

- 用户问：「根据这篇小说，总结人物关系，并判断谁是悲剧核心人物」

- 实际需要：

    - 文本解析 / 检索（RAG / GraphRAG）

    - 人物关系分析（图谱/规则）

    - 推理判断（LLM）

    - 结构化输出

这就必须 多工具协作。

---
## 核心概念拆解
### Tool ≠ Chain ≠ Agent（你必须分清）
概念 |	本质|	举例
--|--|---
Tool	|一个能力函数	|搜索、计算、查天气
Chain	|固定流程的工具组合	|Prompt → LLM → Parser
Agent	|动态决策调用工具	|先搜再算 or 先算再搜

组合多个工具链：Agent 在执行过程中，调用多个 Chain / Tool，并把结果串起来

---
### 工具链组合的 3 种典型模式
1. 串行（Sequential）
```text
输入 → Tool A → Tool B → Tool C → 输出
```
示例：

- 文本 → 实体抽取 → 关系整理 → 总结

特点：

- 简单

- 可预测

- 适合确定流程

---
2. 条件分支（Router）
```text
           → Tool A
输入 → 判断
           → Tool B

```
示例：

    如果是「数学问题」→ Calculator
    
    如果是「事实问题」→ Search
    
    如果是「总结」→ RAG

3. Agent 动态组合
```text
Agent
  ├─ decide → Tool A
  ├─ decide → Tool B
  ├─ decide → Tool C
  └─ synthesize answer
```
特点：

- 非固定顺序

- 可多轮调用

- 可失败重试

---
## Demo
