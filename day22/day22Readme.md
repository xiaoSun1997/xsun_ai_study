了解： 向量数据库原理（相似度检索）

# 什么是向量数据库？
向量数据库（Vector Database）是一类专门用于存储高维向量（embeddings）并进行相似度搜索的数据库。它是现代 AI/RAG 系统（如文档问答、搜索增强生成）的核心组件。

## 🔸 为什么需要向量数据库？

因为传统数据库只擅长结构化数据（数字、文本等），无法处理：

- 句子“我喜欢苹果”和“I enjoy eating apples”

    → 虽然文字不同，但语义接近
    
- 用关键字搜索无法知道语义相似度

向量数据库通过将文本/图片/音频转为向量，可以进行 语义搜索。

---
# 向量数据库的核心原理

向量数据库主要做三件事：

## ✔️ 1. 向量化（Embedding）（详细解释见day19）

将文本转换为一个高维向量，例如：

    "我喜欢苹果" → [0.12, -0.88, 0.55, ...]   # 768维向量


常见模型：

    OpenAI Embedding
    
    BGE-base
    
    sentence-transformers
    
    Cohere embedding

向量的含义：每个维度表示语义的一种“特征”。

---
## ✔️ 2. 相似度度量（Similarity Metric）(day19)

常用方式：
    
    余弦相似度 Cosine similarity（最常见）
    
    点积 Dot Product
    
    欧氏距离 L2 Distance

向量越接近 → 内容越相似。

---
## ✔️ 3. 向量检索（ANN：Approximate Nearest Neighbor）
由于向量维度很高，普通遍历太慢，因此使用 ANN 加速。

常见的索引结构：

算法	| 描述	      |应用
---|----------|---
HNSW	| 图结构，性能强	 |Milvus / Qdrant
IVF-FLAT	| 分桶+暴力计算	 |Faiss
PQ/OPQ	| 向量压缩	    |大规模场景

