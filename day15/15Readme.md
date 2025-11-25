理解 LangChain 基础结构（LLM、Prompt、Chain）

# 一、LangChain 的三个核心概念

## 1. LLM（大语言模型）

在 LangChain 里，LLM 就是“负责生成文字的模型对象”，比如：

- OpenAI（如 gpt-4, gpt-4o）

- Ollama 本地模型（如 llama3）

- 其他厂商模型（通过相应包接入）

你可以把 LLM 看成一个 llm(...) 函数：

- 输入：文本（一般是已经拼好的 Prompt）

- 输出：模型生成的文本

在代码层面，LangChain 会把模型封装成一个类，比如（新版本推荐写法）：

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key="你的_API_KEY"
)
```

之后你可以像调用函数一样用它。

## 2. Prompt（提示词 / 提示模板）见day10、day11

Prompt 就是你给模型的“指令 + 上下文 + 格式要求”。

为了更容易复用和填变量，LangChain 提供了 PromptTemplate：

- 可以写固定结构，比如：

    
    你是一个 Python 助教，请用简单示例解释：{topic}

运行时动态传入 topic="什么是for循环"，就得到完整的字符串。

这和“写一个带占位符的模板字符串”类似。

3. Chain（链）

Chain 的本质：把 “Prompt 构建 + 调 LLM + 解析输出” 这一串步骤，组合成一个可复用的流程。

在 LangChain 里，你可以把多个组件（Prompt, LLM, 输出解析器等等）用 | 串起来：
```
chain = prompt | llm
```

甚至可以：
```
chain = input_schema | prompt | llm | output_parser
```

然后统一：
```
result = chain.invoke({"topic": "LangChain 是什么？"})
```

可以简单理解为：Chain = 可复用的“流水线”。

# 二、 Demo
0. 环境准备
1）安装依赖
```
pip install "langchain>=0.3.0" langchain-openai
```

如果你在国内，需要自行配置代理或使用国内镜像。

2）准备 OpenAI 兼容的 API Key

官方 OpenAI：去官网申请 API Key，然后在环境变量里配置：

```
export OPENAI_API_KEY="你的key"
```

如果你使用的是其它兼容 OpenAI 协议的服务（如 Moonshot、DeepSeek 等），通常也是类似用法，只是 base_url 和 model 名不同；这里先用 OpenAI 举例，逻辑是一样的。

1. 最简版 Demo：直接调用 LLM

目标：写一个脚本，让模型帮你总结一段文本。
```
# file: demo_llm_basic.py

from langchain_openai import ChatOpenAI

def main():
    # 1. 初始化 LLM
    llm = ChatOpenAI(
        model="gpt-4o-mini",     # 你也可以换成别的模型名
        temperature=0.7,         # 创造力程度（0~1）
        # api_key 会默认从环境变量 OPENAI_API_KEY 读取
    )

    # 2. 直接调用（简易用法）
    question = "用 3 点简要说明什么是大语言模型（LLM），用中文回答。"
    response = llm.invoke(question)

    # 3. 打印结果
    print("=== 问题 ===")
    print(question)
    print("\n=== 模型回答 ===")
    print(response.content)  # ChatOpenAI 返回的是一个 Message 对象

if __name__ == "__main__":
    main()

```
运行：

    python demo_llm_basic.py

2. 引入 PromptTemplate：LLM + Prompt

目标：把“问题模板”变成一个可以复用的 Prompt 模板。
```
# file: demo_prompt_chain.py

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

def main():
    # 1. 初始化 LLM
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.5,
    )

    # 2. 定义 Prompt 模板
    #    - {topic} 是变量，运行时传入
    prompt = ChatPromptTemplate.from_template(
        """
你是一个资深 Python 教练，请用新手也能听懂的方式解释下面的主题。

要求：
1. 用中文说明
2. 给至少一个简单示例代码
3. 结构清晰，有小标题

主题：{topic}
"""
    )

    # 3. 将 Prompt 和 LLM 串成一个 Chain
    chain = prompt | llm

    # 4. 调用 Chain
    topic = "Python 中的列表(list)是什么？"
    result = chain.invoke({"topic": topic})

    # 5. 打印
    print("=== 主题 ===")
    print(topic)
    print("\n=== 讲解 ===")
    print(result.content)

if __name__ == "__main__":
    main()
```
3. 再进阶一点：增加输出解析（把结果转成纯字符串）

有时我们希望 Chain 的输出直接是 str 而不是 Message 对象，可以用 StrOutputParser。
```
# file: demo_chain_with_parser.py

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

def main():
    # 1. LLM
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.3,
    )

    # 2. Prompt 模板
    prompt = ChatPromptTemplate.from_template(
        """
你现在是一个面试官，需要根据候选人的职位生成 5 个技术面试问题。

职位：{job_title}

要求：
- 只输出问题列表，不要额外解释
- 用中文
"""
    )

    # 3. 输出解析器：把 ChatMessage -> str
    parser = StrOutputParser()

    # 4. 组合成完整 Chain：输入 -> Prompt -> LLM -> 解析
    chain = prompt | llm | parser

    # 5. 调用
    job_title = "Python 数据分析工程师"
    questions = chain.invoke({"job_title": job_title})

    print("=== 职位 ===")
    print(job_title)
    print("\n=== 生成的问题 ===")
    print(questions)

if __name__ == "__main__":
    main()
```
# 三、回顾

1. LLM

    用 ChatOpenAI 等类初始化模型实例。
    
    控制模型：model、temperature 等参数。
    
    可单独调用：llm.invoke("问题")。

2. Prompt / PromptTemplate

    把“指令 + 占位符变量”封装起来。
    
    用 ChatPromptTemplate.from_template(...) 来创建。
    
    调用时传入字典：prompt.invoke({"topic": "xxx"}) 或在 Chain 中使用。

3. Chain
    
    用 | 操作符把组件连接成流水线。
    
    常见结构：prompt | llm | output_parser。
    
    调用：chain.invoke({输入字典})。

# 四、一个综合性小 Demo：问答机器人（Q&A）

这个例子：用户输入问题，Chain 返回答案（循环交互）。
```
# file: demo_qa_console.py

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

def build_chain():
    # 1. LLM
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.2,
    )

    # 2. Prompt 模板：统一风格
    prompt = ChatPromptTemplate.from_template(
        """
你是一个耐心的中文 AI 助手，回答下面用户的问题。

要求：
- 尽量用简洁、准确的中文回答
- 如果问题不清楚，可友好地请求澄清
- 如果涉及代码，给出简短示例

用户问题：{question}
"""
    )

    # 3. 输出解析器
    parser = StrOutputParser()

    # 4. 组合
    chain = prompt | llm | parser
    return chain

def main():
    chain = build_chain()
    print("简单 Q&A 机器人，输入 'exit' 退出。")

    while True:
        user_q = input("\n你：")
        if user_q.lower() in ["exit", "quit", "q"]:
            print("再见～")
            break

        answer = chain.invoke({"question": user_q})
        print("\nAI：", answer)

if __name__ == "__main__":
    main()
```