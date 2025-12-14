day26 回答准确率测试


# 回答准确率测试

## 1️⃣ 定义（通俗版）

回答准确率测试，就是：

    给模型一批「有标准答案的问题」，看它给出的回答有多少是“对的”

本质是一个 评测（Evaluation）问题。

---

## 2️⃣ 数学定义（简单版）

假设你有：

- N 个问题

- 模型答对了 K 个

那么：

    Accuracy = K / N


例如：

- 100 个问题

- 答对 83 个
  
    - 👉 准确率 = 83%

---

## 3️⃣ 在 LLM 领域的特殊性

和传统分类不同，LLM 的回答是 自然语言：
    
    ❌ 不是 “A / B / C”
    ✅ 而是 “一段文本”

因此 “什么叫答对” 就成了核心难点。

---
# 二、回答准确率测试的关键概念（LLM 视角）
## 1️⃣ 三种常见“准确”的定义
### ✅ 1. Exact Match（严格匹配）
    模型回答 == 标准答案

✔ 简单
❌ 对 LLM 非常不友好

---

### ✅ 2. 语义等价（Semantic Match）
    含义一致即可


例如：

- 标准答案：


    “巴黎是法国的首都”

- 模型回答：

    
    “法国的首都是巴黎”

✔ 更符合人类判断
❌ 需要额外模型判断

---

### ✅ 3. LLM-as-a-Judge（主流方案）

用 另一个 LLM 来判断：

    “模型回答是否正确？”

这是目前工业界、论文里最常见的方法。

---

## 2️⃣ 回答准确率 ≠ 检索准确率

如果你用了 RAG（检索增强生成），要分清：

指标	| 衡量什么
--- | ---
检索准确率	|找到的文档对不对
回答准确率	|最终回答对不对

---

# 三、整体 Demo 架构
```

            ┌────────────┐
            │  Questions │
            └─────┬──────┘
                  │
        ┌─────────▼─────────┐
        │ Chroma 向量数据库 │  ← 知识库
        └─────────┬─────────┘
                  │
        ┌─────────▼─────────┐
        │     Qwen-Plus     │  ← 生成回答
        └─────────┬─────────┘
                  │
        ┌─────────▼─────────┐
        │   Accuracy Judge  │  ← 再用 Qwen-Plus
        └─────────┬─────────┘
                  │
               Accuracy

```
---
# 四、 Demo（可运行）
## Step 0：准备 requirements.txt
```text

openai>=1.0.0
chromadb>=0.4.22
tqdm
python-dotenv

```


安装：
```bash

pip install -r requirements.txt

```

## Step 1：配置 Qwen-Plus

⚠️ Qwen 使用 阿里云 DashScope（OpenAI 兼容接口）

```python

import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)


```

## Step 2：构建一个最小知识库（Chroma）
```python
import chromadb

chroma_client = chromadb.Client()
collection = chroma_client.create_collection(name="demo_kb")

docs = [
    "巴黎是法国的首都。",
    "东京是日本的首都。",
    "北京是中国的首都。"
]

collection.add(
    documents=docs,
    ids=[f"doc{i}" for i in range(len(docs))]
)
```

## Step 3：定义测试问题（带标准答案）
```python

eval_set = [
    {
        "question": "法国的首都是哪里？",
        "answer": "巴黎"
    },
    {
        "question": "日本的首都是哪里？",
        "answer": "东京"
    },
]
```


## Step 4：RAG + Qwen-Plus 生成回答
```python

def answer_question(question):
    # 1. 检索
    results = collection.query(
        query_texts=[question],
        n_results=1
    )
    context = results["documents"][0][0]

    # 2. 生成
    prompt = f"""
已知信息：
{context}

问题：
{question}

请给出简洁准确的回答。
"""

    resp = client.chat.completions.create(
        model="qwen-plus",
        messages=[{"role": "user", "content": prompt}]
    )
    return resp.choices[0].message.content.strip()

```

## Step 5：用 LLM 判断“是否正确”（核心）
```python
def judge_answer(question, gt_answer, model_answer):
    judge_prompt = f"""
你是一个严格的评测员。

问题：
{question}

标准答案：
{gt_answer}

模型回答：
{model_answer}

请判断模型回答是否正确。
只回答 YES 或 NO。
"""

    resp = client.chat.completions.create(
        model="qwen-plus",
        messages=[{"role": "user", "content": judge_prompt}]
    )

    return resp.choices[0].message.content.strip().upper() == "YES"
```
## Step 6：计算准确率
```python
correct = 0

for item in eval_set:
    model_ans = answer_question(item["question"])
    is_correct = judge_answer(
        item["question"],
        item["answer"],
        model_ans
    )
    print(item["question"], model_ans, is_correct)

    if is_correct:
        correct += 1

accuracy = correct / len(eval_set)
print(f"Accuracy: {accuracy:.2%}")
```