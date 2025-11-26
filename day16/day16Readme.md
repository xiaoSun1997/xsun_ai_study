了解 LCEL 和 RunnableSequence的相关知识点

SequentialChain 
(从 langchain v0.1.0 版本开始，SequentialChain 已被弃用)

# LCEL 和 RunnableSequence

一、LCEL 是什么？
1. 基本概念

LCEL（LangChain Expression Language） 是 LangChain 从 v0.1.0 开始引入的声明式编程范式，用于构建 AI 应用链。

核心思想：
```python
# 传统写法（命令式）
result = function3(function2(function1(input)))

```
```python
# LCEL 写法（声明式）
chain = function1 | function2 | function3
result = chain.invoke(input)

```


类比：

- Unix 管道：cat file.txt | grep "error" | wc -l

- LCEL 管道：prompt | llm | output_parser

2. LCEL 的核心优势

优势	| 说明	                 | 示例                       
--------|---------------------|--------------------------
可读性强	| 链式调用，一眼看懂数据流        | 	prompt \| llm \| parser 
可组合	| 组件可以像积木一样自由组合       |	小链 → 大链
自动异步	| 支持 async/await、流式输出 |	.astream()
可观测	|内置追踪、调试、日志|	LangSmith 集成
标准接口	|所有组件都实现 Runnable 协议|	.invoke() .batch()

# 二、Runnable 协议
1. 什么是 Runnable？

Runnable 是 LangChain 中所有可执行组件的基础接口（类似 Python 的 __call__）。

核心方法：

方法	|功能	|使用场景
----|--------|---------
.invoke(input)	|单次同步调用|普通问答
.batch([inputs])|	批量调用|多个问题一起处理
.stream(input)	|流式输出|	打字机效果
.ainvoke(input)	|异步调用|	高并发场景
.astream(input)	|异步流式|	实时对话

实现 Runnable 的组件：

- PromptTemplate

- LLM / ChatModel

- OutputParser

- Retriever

- 自定义函数（用 @chain 装饰）

---

# 三、RunnableSequence 是什么？
1. 基本概念

RunnableSequence 是用 | 操作符连接多个 Runnable 后自动生成的对象。
    
    from langchain_core.runnables import RunnableSequence

    # 这两种写法等价

    chain = prompt | llm | parser
    chain = RunnableSequence(first=prompt, middle=[llm], last=parser)
    

特点：

- 自动处理数据在各组件间的传递

- 支持中间结果查看

- 可以进一步组合成更大的链

2. 执行流程

       输入 (dict/str)
           ↓
       [Component 1] prompt.invoke(input)
           ↓
       [Component 2] llm.invoke(prompt_output)
           ↓
       [Component 3] parser.invoke(llm_output)
           ↓
       最终输出

# 四、完整 Demo：从基础到进阶
## Demo 1：最简单的 LCEL 链
```python

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 1. 定义组件
prompt = ChatPromptTemplate.from_template("给我讲个关于 {topic} 的笑话")
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.9)
parser = StrOutputParser()

# 2. 用 LCEL 连接（自动生成 RunnableSequence）
chain = prompt | llm | parser

# 3. 调用
result = chain.invoke({"topic": "程序员"})
print(result)

# 查看 chain 的类型
print(type(chain))  # <class 'langchain_core.runnables.base.RunnableSequence'>

```


执行流程解析：
    
    {"topic": "程序员"}
        ↓
    prompt.invoke() → "给我讲个关于程序员的笑话"
        ↓
    llm.invoke() → "为什么程序员喜欢黑暗？因为 bug 喜欢藏在光线里..."
        ↓
    parser.invoke() → 纯字符串（去掉 LLM 的包装）

## Demo 2：查看中间结果
```python

# 只执行到某一步
prompt_result = prompt.invoke({"topic": "程序员"})
print("Prompt 输出:", prompt_result)

llm_result = llm.invoke(prompt_result)
print("LLM 输出:", llm_result)

final_result = parser.invoke(llm_result)
print("最终结果:", final_result)

```
##  3：流式输出（打字机效果）
```python

# 流式输出每个 token
for chunk in chain.stream({"topic": "AI"}):
    print(chunk, end="", flush=True)


```
## Demo 4：批量处理
```python

# 一次性处理多个问题
topics = ["Python", "JavaScript", "Go"]
inputs = [{"topic": t} for t in topics]

results = chain.batch(inputs)
for topic, joke in zip(topics, results):
    print(f"\n【{topic}】\n{joke}")


```
## Demo 5：自定义 Runnable（进阶）
```python

from langchain_core.runnables import RunnableLambda

# 方式 1：用 Lambda 包装函数
def add_emoji(text: str) -> str:
    return f"😄 {text} 😄"

emoji_runnable = RunnableLambda(add_emoji)

# 方式 2：用 @chain 装饰器（更优雅）
from langchain_core.runnables import chain

@chain
def add_emoji_v2(text: str) -> str:
    return f"🎉 {text} 🎉"

# 加入链中
chain_with_emoji = prompt | llm | parser | emoji_runnable
result = chain_with_emoji.invoke({"topic": "数据科学"})
print(result)


```
# 五、LCEL 的高级特性
```python

1. RunnableParallel（并行执行）
from langchain_core.runnables import RunnableParallel

# 同时执行多个链
parallel_chain = RunnableParallel(
    joke=prompt | llm | parser,
    question=ChatPromptTemplate.from_template("关于 {topic} 的问题是？") | llm | parser
)

result = parallel_chain.invoke({"topic": "机器学习"})
print(result)
# 输出: {"joke": "...", "question": "..."}


```
2. RunnableBranch（条件分支）
```python

from langchain_core.runnables import RunnableBranch

def is_math_question(input: dict) -> bool:
    return "计算" in input["question"] or "数学" in input["question"]

branch = RunnableBranch(
    (is_math_question, math_chain),  # 如果是数学问题，走 math_chain
    default_chain  # 否则走默认链
)


```
## 3. RunnablePassthrough（透传数据）
```python
from langchain_core.runnables import RunnablePassthrough

# 保留原始输入 + 添加新字段
chain = (
    RunnablePassthrough.assign(
        llm_output=prompt | llm | parser
    )
)

# 输出: {"topic": "Python", "llm_output": "..."}
result = chain.invoke({"topic": "Python"})
print(result)
```


六、LCEL vs 传统 LLMChain
对比表
特性	| 传统 LLMChain                   | 	LCEL                    
----|-------------------------------|--------------------------
写法	| LLMChain(prompt=..., llm=...) | 	prompt \| llm \| parser 
可读性| 	较差（嵌套多层）                     |	优秀（管道式）
流式输出| 	需要额外配置                       |	原生支持 .stream()
异步	| 需要手动处理	                       |原生支持 .ainvoke()
组合性	| 困难	                           |简单（链可以嵌套）
官方推荐	|❌ 已弃用|	✅ 推荐使用

