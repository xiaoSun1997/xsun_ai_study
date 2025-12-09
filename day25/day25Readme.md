day25: 优化 top-k 检索策略
# Top-k 检索策略

在向量数据库中，Top-k 检索 是根据输入的查询向量 找到与之最相似的 K 个向量。具体而言，输入一个查询向量，系统会计算查询与库中向量的相似度（通常是余弦相似度、欧氏距离或点积），然后返回最相似的 K 个结果。

## 常见的相似度度量方法：

    余弦相似度（Cosine Similarity）：衡量两个向量方向的相似性。
    
    欧氏距离（Euclidean Distance）：衡量两个向量的直线距离。
    
    点积（Dot Product）：衡量两个向量的内积，通常在文本相似性任务中用于计算句子的相似度。

优化 Top-k 检索策略的关键是减少计算量和提高相似度计算的效率，同时保证返回的结果质量高。

---
# 优化 Top-k 检索策略的思路
## 1. 向量降维

1. PCA（主成分分析） 或 t-SNE 等方法用于减少向量的维度。通过降低向量维度，可以加速计算，并减少计算资源的消耗。

2. Huggingface Transformers 生成的 embeddings 往往维度较高，通常可以采用降维算法降低计算复杂度。

## 2. 使用高效的 ANN 索引算法

1. HNSW（Hierarchical Navigable Small World）：一种高效的图结构，用于处理高维数据的最近邻检索。

2. IVF（Inverted File）：将向量分成多个簇进行检索，适用于大规模向量数据。

3. Product Quantization（PQ）：通过量化向量来减少存储需求，提高检索速度。

这些索引方法会在检索前为向量库建立一个 索引结构，使得在查询时可以更快找到相似向量。

## 3. 合理设置 k 值

1. k 值的选择是一个平衡 计算成本 和 结果质量 的问题。k 太大可能导致计算开销过大，太小可能会丢失潜在的相关信息。

2. 可以使用 多阶段检索：首先进行粗检索，找出较多候选向量，然后再在候选向量中精细计算出最相似的 k 个向量。

## 4. 优化相似度计算方式

根据具体场景调整相似度计算方式，比如：

1. 对于文本相似度，余弦相似度是常用的计算方式，但如果模型的向量已经经过标准化处理（如归一化），使用点积会更有效。

2. 混合距离度量：有时结合多种相似度度量（例如先使用欧氏距离进行粗检索，再使用余弦相似度精细计算）可以得到更准确的结果。

---
# 实现 Demo：优化 Top-k 检索

我们将通过一个简单的 Chroma + Sentence-Transformer 示例，演示如何优化 Top-k 检索策略。

环境准备

安装所需依赖：

    pip install chromadb sentence-transformers

1. 导入必要的库
```python
import chromadb
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
import numpy as np

```

2. 设置 Embedding 模型

我们使用 SentenceTransformer 来生成向量表示。

```python
# 加载 Sentence Transformer 模型
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# 定义 Embedding 函数
def get_embedding(texts):
    return model.encode(texts).tolist()
```


3. 创建一个 Chroma 客户端并添加文档

我们将使用 Chroma 来存储文档并为每个文档生成一个向量。
```python

# 初始化 Chroma 客户端
client = chromadb.Client()

# 创建一个集合
collection = client.create_collection("optimized_search_collection")

# 假设我们有一些文档
documents = [
    "苹果是一种非常美味的水果，营养丰富。",
    "香蕉富含钾元素，对人体健康有益。",
    "今天的天气非常好，适合户外活动。",
    "股市近期的波动较大，有一定的投资风险。",
    "我喜欢吃草莓和蓝莓，尤其是在夏天。"
]

# 获取每个文档的 embedding 向量
embeddings = get_embedding(documents)

# 将文档及其向量添加到 Chroma 中
collection.add(
    ids=[f"id_{i}" for i in range(len(documents))],
    documents=documents,
    embeddings=embeddings
)
```
4. 实现优化的 Top-k 检索

在进行检索时，我们可以通过以下方式优化 Top-k 策略：
    
4.1. 使用 HNSW 索引：提高检索效率。

4.2. 使用不同的距离度量：例如余弦相似度。

4.3. 多阶段检索：首先粗略检索，再精细计算。

4.4. 执行查询并返回 Top-k 相似度结果
```python

def optimized_top_k_search(query, k=3):
    # 获取查询的向量表示
    query_embedding = get_embedding([query])[0]

    # 在 Chroma 中进行相似度检索
    results = collection.query(
        query_embeddings=[query_embedding],  # 查询向量
        n_results=k  # 返回前 k 个结果
    )

    # 输出最相似的文档
    print(f"Query: {query}")
    for i, result in enumerate(results['documents'][0]):
        print(f"Top {i+1}: {result}")
```
5. 执行查询并展示结果

假设我们要查询“我喜欢吃水果”，并返回最相似的 3 个文档。
```python
query = "我喜欢吃水果"
optimized_top_k_search(query, k=3)


```


输出示例：

    Query: 我喜欢吃水果
    Top 1: 苹果是一种非常美味的水果，营养丰富。
    Top 2: 我喜欢吃草莓和蓝莓，尤其是在夏天。
    Top 3: 香蕉富含钾元素，对人体健康有益。

6. 进一步优化：调整 k 值与距离度量

1. 调节 k 值：你可以通过调整 k 值，控制返回的相似文档数量，进一步影响计算效率和结果质量。

2. 使用不同的距离度量：你可以在 Chroma 创建时指定其他距离度量方式，如 l2 或 ip，并调整相似度计算方法。

例如，使用余弦相似度：
```python
collection = client.create_collection("optimized_search_collection", metadata={"hnsw:space": "cosine"})

```

---
# 总结：如何优化 Top-k 检索策略

    向量降维：减少高维向量计算量，加速检索。
    
    高效索引算法：使用 HNSW 等高效索引提高检索速度。
    
    合理选择 k 值：通过调节 k 值平衡计算成本与结果质量。
    
    多阶段检索：先进行粗检索，找到候选向量，再进行精细匹配。
    
    调整距离度量方式：根据实际应用场景选择合适的相似度计算方式。