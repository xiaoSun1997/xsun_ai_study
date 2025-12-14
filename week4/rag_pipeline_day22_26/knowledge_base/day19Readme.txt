day19 今日目标 理解 Embedding 嵌入模型（SentenceTransformers）

# 数学知识
## 向量
1. 向量：可以想象成“有方向和大小的箭头”


    - 在二维平面里，一个点 (x, y) 可以看成一个向量
    
    - 在三维里是 (x, y, z)
    
    - 在机器学习里，向量可以是很多维，比如 384 维、768 维，就是 (v₁, v₂, v₃, ..., v₇₆₈)

直观理解：
向量 = 一串有顺序的数字，用来“表示某个东西”。

在 Embedding 里：一句话/一个单词/一个文档 → 被表示成一个向量。

---
## 向量的基本运算
假设有两个二维向量：

    a = (a₁, a₂)
    
    b = (b₁, b₂)
高维的时候也是一样，只是多了维度。
1. 向量加法


    a+b=(a1​+b1​,a2​+b2​)
就是对应位置相加。

    举例：
    a = (1, 2)，b = (3, 4)
    a + b = (1+3, 2+4) = (4, 6)
2. 数乘（标量乘法）

数字 k 乘向量 a：

    ka = (ka₁, ka₂)
就是把每一维都乘以 k，相当于把箭头拉长/缩短。

    举例：
    2 * (1, 2) = (2, 4)

---
## 向量的长度（范数 / norm）
二维就是勾股定理

            
    |a| = √(a₁² + a₂² + a₃²)

三维：

    |a| = √(a₁² + a₂² + a₃²)

高维同理：所有维度平方加起来，再开根号。

    举例：
    a = (3, 4)
    |a| = √(3² + 4²) = √(9+16) = √25 = 5

---
## 单位向量（unit vector）

单位向量：长度为 1 的向量。

求法：
给一个向量 a，先算出它的长度，然后每一维都除以长度。

    a^ = a / |a|

    举例：
    a = (3, 4)，|a| = 5
    单位向量：Â = (3/5, 4/5)
    你可以检验一下：
    |Â| = √[(3/5)² + (4/5)²] = √(9/25 + 16/25) = √(25/25) = 1 

只保留“方向”，长度固定为 1。
在 Embedding 里，我们常常把向量归一化成单位向量，再算相似度。

---
## 向量点积（dot product / inner product）

两个向量 a = (a₁,…, aₙ)、b = (b₁,…, bₙ) 的点积定义为：
    
    a·b = a₁b₁ + a₂b₂ + a₃b₃ + ... + aₙbₙ


举例：

    a = (1, 2, 3)
    b = (4, 5, 6)
    a · b = 1×4 + 2×5 + 3×6 = 4 + 10 + 18 = 32

点积同时有一个“几何意义”：

        a⋅b=|a||b|cosθ

        cosθ= a⋅b /  |a||b|    -->  cosθ = a/|a| * b/|b| 

- θ 是 a 和 b 的夹角（0°~180°）

  - cosθ 是三角函数里的余弦值（你只需要知道：

      - 夹角小 → cosθ 大（接近 1）
    
      - 夹角 90° → cosθ = 0
    
      - 夹角 >90° → cosθ 变成负的）
    
这个公式是后面余弦相似度的核心。

---

## 余弦相似度：衡量两个向量“方向是否相似”
    
1. 定义

余弦相似度（cosine similarity）：
 
    cos_sim(a,b) = a⋅b /  |a||b|  = a/|a| * b/|b| 

根据刚才的几何意义，其实这就是cos θ，θ 是两个向量的夹角。

- 取值范围：[-1, 1]

    - 1：完全同方向，非常相似

    - 0：正交（垂直），没啥关系

    - -1：完全反方向，非常不相似（对立）

在文本 Embedding 里，一般不会出现特别负的情况，常见的是 0~1 之间。

---

2. 手算一个小例子（直观一点）

设：

a = (1, 0)

b = (1, 1)

1）求各自的单位向量：
    
    a^ = a / |a| = (1, 0)
    b^ = b / |b| = (1/√2, 1/√2)



2）代入公式：

    cos_sim(a,b) = a^·b^ = (1, 0)·(1/√2, 1/√2) = 1/√2

1/√2 > 0，说明它们方向比较接近（实际就是 45° 的夹角）。

直观想象：

a = (1, 0)：指向正右方

b = (1, 1)：指向右上方
方向挺接近的，所以相似度也不低。

---

## Embedding（嵌入）
1. 核心想法：用向量表示“含义”

自然语言（中文、英文）对计算机来说太抽象，
所以我们想找一种“数字化的表示方式”，让“语义相近的句子”对应到“相近的向量”。

- “我今天很开心” → 向量 v1

- “我感觉非常高兴” → 向量 v2

- 希望：v1 和 v2 的余弦相似度很高（接近 1）

这整个把文本映射成向量的过程，就叫做 Embedding（嵌入）。

得到的向量就叫 嵌入向量 / embedding 向量。

---
2. Embedding 的用途

有了“文本 → 向量”的能力，就可以做很多事情：

1. 语义搜索（semantic search）


    用户输入一个问题 → 变成向量 q
    
    数据库里有很多文本 → 预先变成向量 d1, d2, ...
    
    计算 q 和每个 d 的余弦相似度，找相似度最高的几个，返回。

2. 文本聚类 / 分类


    相似的文本在向量空间里会“聚在一起”
    
    可以用聚类算法（K-means 等）在向量空间里分组
    
    或者直接用 embedding 作为特征喂给分类器。

3. 推荐系统


    用户行为 / 用户兴趣也可以编码成向量
    
    项目/商品也编码成向量
    
    用向量相似度来推荐“你可能喜欢的东西”。

4. 多语言语义对齐
    

    不同语言的句子映射到同一个向量空间
    
    比如 “I love you” 和 “我爱你”，向量会很接近
    
    支持跨语言检索。

---
## SentenceTransformers

### Transformer 简要介绍
Transformer 是一种非常强大的神经网络结构，
它的关键能力是：自注意力（self-attention），可以在一句话中，让每个词“看到”其他所有词，理解上下文。

    比如句子：
    “我把苹果放在桌子上，然后它滚下去了。”
    “它” 到底指代谁？需要结合前后文。
    Transformer 就擅长搞这种 “上下文关联”。

pip常见的预训练 Transformer 模型：
1. BERT

2. RoBERTa

3. DistilBERT

4. XLM-RoBERTa

5. ......

---
### SentenceTransformers：把 Transformer 变成“句子向量生成器”
SentenceTransformers 是一个 Python 库（基于 PyTorch），核心目标就是：

    简单地从句子 / 段落中得到“好用的语义向量（sentence embeddings）”

它做了几件事：
1. 封装了各种预训练模型

    - 比如 all-MiniLM-L6-v2、multi-qa-MiniLM、paraphrase-MiniLM 等

2. 提供统一的接口

    - model.encode(["句子1", "句子2"]) 直接得到 embedding

3. 对 Transformer 做了特殊训练（Siamese / Triplet / 对比学习）

    - 让模型学会：相似句子 → 向量接近，不相似 → 拉得远。

---
### SentenceTransformers 的基本使用流程（概念上）
1. 载入模型
```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
```
2. 编码句子：文本 → 向量
```python
sentences = ["我今天很开心", "我感觉非常高兴"]
embeddings = model.encode(sentences)
```
3. 计算相似度

- 把两个 embedding 拿出来，用余弦相似度公式

- 库里一般也会帮你算好。

---
### SentenceTransformers简略原理
对一个句子：
    
    “I love machine learning.”

大致经过这些步骤：

1. 分词 / tokenization

    - 句子 → 子词（tokens），比如 ["I", "love", "machine", "learning", "."]

    - 变成 token id（整数序列）喂给模型。

2. Transformer 编码

    - 每个 token 得到一个向量表示，比如维度 768

    - 整个句子变成一个矩阵 (序列长度, 隐层维度)，比如 (10, 768)

3. Pooling（池化）得到一个“句子级别”的向量
常见方式：

    - CLS pooling：取 [CLS] 位置的输出

    - Mean pooling：对所有 token 向量求平均 → 得到一个长度为 768 的句子向量

4. （有时）再做 L2 归一化

    - 把句子向量变成单位向量  a^ = a / |a|
    - 这样直接用点积就等价于余弦相似度。

5. 训练方式：让“相似句子更近，不相似句子更远”

典型做法：Siamese / 对比学习（contrastive learning）

- 训练数据里有句子对：

    - 正样本（相似）：“你好吗？” vs “最近怎么样？”

    - 负样本（不相似）：“今天天气不错” vs “我把电脑落在公司了”

- 目标：

    - 正样本的 embedding 余弦相似度高

    - 负样本的余弦相似度低

- 损失函数会鼓励这种行为，模型训练久了，就学会把语义相近的句子拉得更近。

## DEMO
```python

import numpy as np
from sentence_transformers import SentenceTransformer


def main():
    corpus = [
        "我今天心情很好，因为拿到了工作机会。",
        "今天天气不错，阳光明媚，适合出去玩。",
        "我昨天加班到很晚，有点累。",
        "最近在学深度学习和自然语言处理，感觉很有趣。",
        "今天面试通过了，我觉得非常开心和兴奋。",
        "股票市场今天大跌，很多人都很紧张。",
        "我打算周末去爬山放松一下心情。",
    ]
    # 加载模型
    model = SentenceTransformer('all-MiniLM-L6-V2')

    # 查看向量维度
    print("Embedding dim:")
    print(model.get_sentence_embedding_dimension())

    corpus_embeddings = model.encode(corpus,
                                     convert_to_numpy=True,
                                     normalize_embeddings=True)

    print("Corpus embeddings shape:",corpus_embeddings.shape)

    while True:
        query = input("请输入查询：")
        if query.lower() in ["q"]:
            print("程序已退出")
            break
        semantic_search(query,corpus,corpus_embeddings,top_k=3)


def semantic_search(query,corpus,corpus_embeddings,top_k):

    model = SentenceTransformer('all-MiniLM-L6-V2')

    query_embedding = model.encode(query, convert_to_numpy=True,normalize_embeddings=True)

    scores = np.dot(query_embedding, corpus_embeddings.T)

    if np.isscalar(scores):
        scores = np.array([scores])
    elif scores.ndim == 0:
        scores = np.array([scores.item()])

    top_k = min(top_k, len(corpus))
    top_k_indices = np.argsort(-scores)[:top_k]

    results =[(idx,float(scores[idx])) for idx in top_k_indices]
    # 打印搜索结果
    print(f"\n查询: {query}")
    print("最相似的句子:")
    for idx, score in results:
        print(f"  [{score:.4f}] {corpus[idx]}")

    return results

if __name__ == "__main__":
    main()
```
        
        