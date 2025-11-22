今日目标 学习 Prompt 模板化设计（PromptTemplate）

# 一、为什么要做 Prompt 模板化？

如果你只偶尔在 ChatGPT 里手打一个问题，那不需要模板；
但一旦你要做的是：“给一批数据都用同一类指令处理”，模板就变成刚需。典型场景：

1. 批量生成：


    1000 条商品文案

    大量日志/流量文本的自动标签

    成千上万条评论的情感分析 + 理由说明

2. 产品化：


    在一个系统里给用户提供“智能问答 / 文案助手 / 营销助手”等功能
    
    需要让 Prompt 变成“可维护的配置项”，而不是散落在代码里的长字符串

3. 实验调参：


    同一个任务，但你要不断尝试不同表达方式
    
    希望修改模板就能快速 A/B，避免动到一堆业务逻辑

一句话：模板化让 Prompt 具备了：可复用、可参数化、可版本化、可维护的工程属性。

---
# 二、PromptTemplate 的核心思想：把 Prompt 当函数

概念抽象：

    PromptTemplate ≈ 一个函数
    输入：若干参数（variables）
    输出：一个完整的 Prompt 字符串

形式上一般类似：

    模板内容：  
    你是一个{role}。  
    现在有一段文本：{text}  
    请将其分类为以下几类之一：{labels}。  
    最终只输出类别名称，不要解释。

 - 参数：role, text, labels


调用时：

    role   = "资深安全分析专家"
    text   = "来自 PLC 的 Modbus 写寄存器操作，频率突然升高。"
    labels = "正常业务流量, 可疑扫描行为, 高危入侵行为"

    template.format(role=role, text=text, labels=labels)


得到最终 Prompt：

    你是一个资深安全分析专家。
    现在有一段文本：来自 PLC 的 Modbus 写寄存器操作，频率突然升高。
    请将其分类为以下几类之一：正常业务流量, 可疑扫描行为, 高危入侵行为。
    最终只输出类别名称，不要解释。


注意几点关键要素：

- 固定部分：任务角色说明 + 输出格式要求

- 参数部分：动态插入的具体数据（如一条日志、一段对话、一组候选标签）

- 结构清晰：段落清楚地划分角色、输入、要求、输出格式

- 易于复用：只改参数即可重复使用同一逻辑
---
# 三、几种典型的 Prompt 模板结构
## 1. “Role + Task + Input + Output” 四段式

这是最常用、也最清晰的一种结构：

    [角色 / 背景 Role]
    你现在是一名{role}。
    
    [任务说明 Task]
    你的任务是：{task_description}
    
    [输入 Input]
    下面是需要处理的内容：
    {input}
    
    [输出要求 Output Format]
    请根据上述内容，输出：
    {output_requirements}


参数示例：

- role：资深工控安全专家 / 文案策划 / 教学设计专家

- task_description：对工控日志进行场景分类；编写推广文案；为学生讲解 Transformer

- input：日志内容 / 商品信息 / 学生问题

- output_requirements：输出 JSON；输出 markdown 表格；只输出类别名称等

## 2. “Few-shot 示例驱动”模板

在模板中内嵌几条示例（Example）：
    
    你是一名{role}，负责将文本划分到给定的场景类别中。
    
    可选类别：
    {labels}
    
    下面是一些示例：
    [示例1]
    文本：{example_text_1}
    类别：{example_label_1}
    
    [示例2]
    文本：{example_text_2}
    类别：{example_label_2}
    
    现在，请对下面的文本进行分类：
    文本：{input_text}
    
    只输出一个类别名称。
    

这里模板整体是固定的，参数包括：

- 角色说明 role

- 类别集合 labels

- 若干示例 example_text_x / example_label_x

- 当前输入 input_text

这种模板的优势：对模型的“意图对齐”更强，适合类别复杂或者容易混淆的任务。

---
## 3. “分步思考 + 结构化输出”模板

对于复杂任务，可以让模型“先思考，再总结”，但最后仍然要求结构化输出，方便程序解析：
    
    你是一名{role}。
    
    任务：分析以下内容，并完成三步：
    1. 用简短的自然语言总结它在说什么。
    2. 判断它属于以下哪一类：{labels}
    3. 给出 1~5 的风险评分。
    
    请严格按照下面 JSON 格式返回（不要添加其他内容）：
    {
      "summary": "...",
      "label": "...",
      "risk_score": ...
    }
    
    待分析内容：
    {text}


这里模板化的点在于：

- 把“思考步骤”写进 Prompt

- 同时强制输出合法 JSON，方便程序直接 json.loads() 解析

---
## 四、在 LangChain 中的 PromptTemplate（一个比较正规/工程化的例子）

用 Python + LangChain 写一个标准 PromptTemplate，大致如下：

    from langchain.prompts import PromptTemplate
    
    template_str = """
    你是一名资深工控安全分析专家。
    
    你的任务：
    - 根据给定的工业控制流量描述，对其业务场景进行分类。
    
    可选场景类别：
    {labels}
    
    请按照以下步骤思考：
    1. 简要复述该流量可能对应的业务操作。
    2. 判断它最可能属于哪个场景类别。
    
    最终只输出一个场景名称（必须是上述候选之一），不要输出其他文字。
    
    待分析内容：
    {text}
    """
    
    prompt = PromptTemplate(
        input_variables=["labels", "text"],
        template=template_str,
    )
    

然后在实际调用时：

    labels = "正常生产控制, 设备调试, 远程维护, 疑似攻击流量"
    text = "PLC 在凌晨 3 点接受到来自非常用工程站的程序写入请求。"
    
    filled_prompt = prompt.format(labels=labels, text=text)
    print(filled_prompt)


如果再配合一个 LLM（如 OpenAI / 本地模型）：

    from langchain_openai import ChatOpenAI  # 示例
    from langchain.chains import LLMChain
    
    llm = ChatOpenAI(model="gpt-4o")
    
    chain = LLMChain(llm=llm, prompt=prompt)
    
    result = chain.run(labels=labels, text=text)
    print("模型输出场景：", result)


这里的要点是：

- PromptTemplate 专注于 Prompt 构造

- LLM 只负责“接收字符串 → 输出字符串”

- 你的业务逻辑调用的是“链（LLMChain）”，而不是混杂的字符串拼接

---
## 五、工程实践层面的 Prompt 模板化设计要点

我给你一套“审查/设计 Prompt 模板”的 checklist，可以直接套在你自己的任务上。

## 1. 明确“输入/输出边界”

- 模板里要清楚写明：给你的输入是什么？

- 也要写清楚：你必须输出成什么格式？

如果输出要被程序解析：

- 尽量要求：

    - JSON
    - CSV（少见）
    - Markdown 表格
    - 一行一个 label

示例：

    请严格按照如下 JSON 格式输出（不要添加注释、不要添加多余文字）：
    {
      "label": "从 {labels} 中选择一个",
      "confidence": "0~1 之间的小数"
    }

## 2. 尽量不要把“业务逻辑”写死在 Prompt 文本里

例如，不要写：

    候选场景：正常业务流量, 扫描行为, 入侵行为


而写成：

    候选场景：{labels}


这样，当你新增类别或改名，只需要改配置/数据库，而不用改代码里的长字符串。

## 3. 对多语言 / 多区域做抽象

你可以设计多语言模板，例如：
    
    你是一名{role_zh} / You are a {role_en}.
    ...
    
    当前语言：{lang}
    ...


然后在参数中传不同语言版本，很容易做国际化。

## 4. 把“风格/语气”也当作参数

例如：

    请用{tone}的语气撰写输出，目标读者是{audience}。


参数：

- tone：严谨学术 / 口语化 / 营销风 / 老师讲解

- audience：安全工程师 / 初学者 / 管理层

这样一个模板可以覆盖很多场景，而不需要复制粘贴多个类似 Prompt。

## 5. 给模板版本号（非常工程向的建议）

在复杂系统里，你可以直接在模板顶部加一行：

    # PROMPT_VERSION: v1.3


这样：

- 出现问题可以回溯：某次上线是不是换了 Prompt 版本？

- A/B 实验时也方便标记：模型输出可带上 Prompt 版本号用于分析

# 六、一个从 0 到 1 的完整小示例（不依赖 LangChain，只用 Python）

我们写一个最小可用的 PromptTemplate 类，自己感受一下原理：
    
    from dataclasses import dataclass
    from typing import List, Dict
    
    @dataclass
    class PromptTemplate:
        template: str
        input_variables: List[str]
    
        def format(self, **kwargs) -> str:
            # 简单校验：检查参数是否齐全
            missing = [v for v in self.input_variables if v not in kwargs]
            if missing:
                raise ValueError(f"Missing variables for template: {missing}")
            return self.template.format(**kwargs)
    
    
    # 定义模板
    template_str = """
    你是一名{role}。
    
    任务：
    - 阅读下面的文本，并从以下标签中选择一个最合适的类别：
    {labels}
    
    要求：
    1. 先在心里推理原因，但不要写出来。
       2. 最终只输出一个标签名称。
    
    文本内容：
    {text}
    """
    
    prompt = PromptTemplate(
        template=template_str,
        input_variables=["role", "labels", "text"],
    )
    
    # 使用模板
    filled = prompt.format(
        role="资深工控安全分析专家",
        labels="正常业务流量, 设备维护, 故障诊断, 可疑攻击行为",
        text="在非生产时间段出现大量来自外部 IP 的写寄存器指令。",
    )
    
    print(filled)


接下来你只需要把 filled 丢给任意一个 LLM API（OpenAI、Azure、本地模型）即可。

# 七、如何把这件事逐步用在你的项目里？

如果你已经在做：

- 日志/流量 → 场景分类

- 文本 → 标签/摘要/说明

- 用户输入 → 智能回复

你可以按下面顺序来落地 Prompt 模板化：

- 先把现在“写死在代码里的 Prompt”抽出来，变成一个带 {变量} 的大字符串

- 用类似 PromptTemplate 的类包一层，确保：

    - 参数列表清晰

    - 缺参数时会报错，而不是 silent fail

- 再做进一步升级：

    - 把模板放入配置文件 / 数据库

    - 加上版本号

    - 对不同任务 / 场景统一管理