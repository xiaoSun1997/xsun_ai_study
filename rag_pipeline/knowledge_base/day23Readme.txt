day23: Chroma 基础与索引

# Chroma 基础概念
Chroma 本质上是一个 轻量级向量数据库 / 向量存储（Vector Store），特点是：

- 💾 内嵌持久化（不用单独启动服务器）

- 🧱 按 Collection 管理数据（类似“表”）

- 📌 支持 metadata / documents / embeddings 三类数据

- 🔍 内置 ANN 索引（如 HNSW），用于高效相似度搜索

---
## Chroma 的核心结构
可以把 Chroma 想象成：

- Client：数据库客户端入口

- Collection：一个集合，相当于一张表，用于存文档的向量 + 原文 + 元信息

- Record（一条数据）包含：

    - id: 唯一标识

    - embedding: 向量（list[float]）

    - document: 文本内容

    - metadata: 任意辅助信息（如来源文件名、页码等）
  
在 Chroma 原生 API 中，通常用法为：
```python
import chromadb

client = chromadb.Client()
collection = client.create_collection("my_collection")

collection.add(
    ids=["1"],
    documents=["这是一个示例文档"],
    metadatas=[{"source": "demo.txt"}],
    embeddings=[[0.1, 0.2, 0.3]]  # 一般由 embedding 模型生成
)

```
不过在实际“做知识库”时，大家一般用 LangChain 封装好的 Chroma 向量库，更方便跟 Loader / LLM 结合.

---
## Chroma 的持久化模式（Persistence）

Chroma 有两种典型用法：

1. 内存模式（默认）：

   - 使用 chromadb.Client()

   - 程序结束 / 进程退出，数据就没了

   - 适合快速实验 / demo

2. 持久化模式（推荐做知识库）：

   - 使用 chromadb.PersistentClient(path="chroma_db")

   - 所有数据会存到 chroma_db 目录

   - 下次重新运行代码，通过同一 path 可以继续使用原来的向量库

在 LangChain 中，通过 Chroma(persist_directory="chroma_db", ...) 来指定本地持久化路径。

---
## Chroma 的索引与相似度度量

Chroma 内部使用高效的 ANN 索引（默认 HNSW），你可以理解为：

    - 数据插入时，Chroma 会在后台维护一个 向量索引结构

    - 查询时，Chroma 不会暴力比对所有向量，而是用索引快速找到最相似的几个

相似度空间（distance metric） 常见几种：

    - cosine：余弦相似度（最常见，用于文本 embedding）
    
    - l2：欧氏距离
    
    - ip：Inner Product（点积）

在原生 Chroma 中可以通过 metadata 设置：
```python

collection = client.create_collection(
    name="my_collection",
    metadata={"hnsw:space": "cosine"}
)

```

在 LangChain 的 Chroma 封装里，一般默认用 cosine（由底层与 embedding 配合）。

---
结合 TextLoader / PDFLoader (day18) 做“文档→知识库”
# DEMO

```commandline
# 用于加速pip下载
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
//进入虚拟环境之后：
pip install "langchain>=0.2.0" chromadb sentence-transformers pypdf
```
```python
from typing import List

from langchain_core.embeddings import Embeddings
from sentence_transformers import SentenceTransformer


class SentenceTransformerEmbeddings(Embeddings):
    # 比较适用于中文的模型 bge-small-zh-v1.5
    def __init__(self, model_name: str = "BAAI/bge-small-zh-v1.5"):
        self.model = SentenceTransformer(model_name)

    def embed_query(self, text: str) -> List[float]:
        return self.model.encode(text,show_progress_bar=True,normalize_embeddings=True).tolist()

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self.model.encode(texts,normalize_embeddings=True).tolist()

```
```python
import os
import shutil

from langchain_community.document_loaders import PyPDFLoader
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

from SentenceTransformerEmbeddings import SentenceTransformerEmbeddings


def loadPdfFile():
    print(">>>>>>>>>>>>> loading pdf file Start<<<<<<<<<<<<<<<<<<")
    docs = []
    pdf_loader = PyPDFLoader("health.pdf")
    pdf_docs = pdf_loader.load()
    docs.extend(pdf_docs)
    print(f"已经加载{len(pdf_docs)}页pdf文件")
    print(">>>>>>>>>>>>> loading pdf file End<<<<<<<<<<<<<<<<<<")
    return docs

def split_docs(docs):
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", "。", "！", "？", "，", "；", "、", "："],
        chunk_size=800,  # 中文平均每个字2字节，500太小
        chunk_overlap=150,
        length_function=len,  # 确保这是按字符计数
        is_separator_regex=False
    )
    split_docs =text_splitter.split_documents(docs)
    print(f"已经分词{len(split_docs)}个段落")
    return split_docs

def build_or_load_vector_store(docs,persist_directory="./chroma_db"):
    embeddings = SentenceTransformerEmbeddings()

    if os.path.exists(persist_directory) and len(os.listdir(persist_directory)) > 0:
        print("---------------------- Found existing index, loading ----------------------")
        # print(f"⚠️ 删除旧的向量数据库: {persist_directory},并重新创建")
        # shutil.rmtree(persist_directory)
        # vector_store = Chroma.from_documents(docs,
        #                                      embeddings,
        #                                      persist_directory=persist_directory)
        # print(f"Created {vector_store._collection.count()} documents")
        vector_store = Chroma(persist_directory=persist_directory,
                              embedding_function=embeddings)
        print(f"Found {vector_store._collection.count()} existing documents")
        print("---------------------- Found existing index, loading END----------------------")

    else:
        print("======================= Creating new index =======================")
        vector_store = Chroma.from_documents(docs,
                                             embeddings,
                                             persist_directory=persist_directory)
        print(f"Created {vector_store._collection.count()} documents")
        print("======================= Creating new index ,END =======================")

    return vector_store


def query_vector_store(vector_store,query,k: int = 1):
    print(">>>>>>>>>>>>>>>>>>>>>>> Querying vector store Start<<<<<<<<<<<<<<<<<<<<<<<<")
    # 方法1: 带分数的相似度搜索
    print("\n=== 方法1: 标准相似度搜索 ===")
    results = vector_store.similarity_search_with_score(query,k=k)
    for i, (doc, score) in enumerate(results, start=1):
        print(f"\n--- 结果 {i} (相似度: {score:.4f}) ---")
        print(f"Similarity Score: {score:.4f}")
        print(f"来源: {doc.metadata.get('source', '未知')}")
        print(f"页码: {doc.metadata.get('page', '未知')}")
        print(f"内容预览:\n{doc.page_content[:300]}...")




if __name__ == "__main__":
    docs = loadPdfFile()
    split_docs = split_docs(docs)
    vector_store = build_or_load_vector_store(split_docs)
    while True:
        query = input("\n请输入查询 (输入 'q' 退出): ").strip()
        if query.lower() in ["q"]:
            print("程序已退出")
            break
        query_vector_store(vector_store, query, k=3)
        
# === 方法1: 标准相似度搜索 ===
# Batches: 100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 122.31it/s]
# 
# --- 结果 1 (相似度: 0.4841) ---
# Similarity Score: 0.4841
# 来源: health.pdf
# 页码: 0
# 内容预览:
# 养生冷知识："逆腹式呼吸法" - 被遗忘的古法呼吸术
# 核心知识点：
# 普通腹式呼吸是吸气时腹部鼓起，呼气时腹部收缩。而逆腹式呼吸正好相反：
# 吸气时：腹部自然内收，横膈膜上升
# 呼气时：腹部放松外鼓，横膈膜下降
# 冷门数据点：
# 1.
# 历史渊源（适合时间维度向量）：
# 源自道家"丹田呼吸法"，记载于《云笈七签》
# 明清武术家用于内功修炼（形意拳、八卦掌秘传）
# 现代被 NASA 研究用于宇航员抗G 力训练
# 2.
# 生理机制对比（适合数值向量）：
# 普通腹式呼吸：
# - 潮气量：500-700ml
# - 呼吸频率：12-20 次/分钟
# - 副交感神经激活度：中等
# 逆腹式呼吸：
# - 潮气量：800-1000ml（增加 4...
# 
# --- 结果 2 (相似度: 0.5579) ---
# Similarity Score: 0.5579
# 来源: health.pdf
# 页码: 1
# 内容预览:
# 2019 年《呼吸医学》期刊研究：逆腹式呼吸组 vs 普通呼吸组
# 血压下降：12.4/8.2 mmHg vs 5.3/3.1 mmHg
# 皮质醇降低：28% vs 11%                                                                                                                                                                                                              
# 肠道蠕动频率：增加 45% vs 15%                                                                                                                                                                                                       
# 日本研究：激活"第二大脑"（肠神经系统）                                                                                                                                                                                              
# 产生血清素量：提高 30%（通过迷走神经通路）                                                                                                                                                                                          
# 4.                                                                                                                                                                                                                                  
# 4.                                                                                                                                                                                                                                  
# 现代应用场景（适合分类向量）：                                                                                                                                                                                                      
# 运动员：提升核心稳定性（比普拉提训练效率高 20%）                                                                                                                                                                                    
# 程序员：缓解"屏幕呼吸暂停症"                                                                                                                                                                                                        
# 音乐家：增加肺活量同时稳定发声（声乐教师秘传）                                                                                                                                                                                      
# 孕妇禁忌：孕中期后禁用（可能引起宫缩）                                                                                                                                                                                              
# 5.                                                                                                                                                                                                                                  
# 科学冷门机制：                                                                                                                                                                                                                      
# 激活"横膈膜-盆底肌联合泵"：促进淋巴回流                                                                                                                                                                                             
# 产生"肝源性 IGF...                                                                                                                                                                                                                  
#                                                                                                                                                                                                                                     
# --- 结果 3 (相似度: 1.2962) ---                                                                                                                                                                                                     
# Similarity Score: 1.2962                                                                                                                                                                                                            
# 来源: health.pdf                                                                                                                                                                                                                    
# 页码: 2                                                                                                                                                                                                                             
# 内容预览:                                                                                                                                                                                                                           
# 西医："Diaphragmatic Paradoxical Breathing"...                                                                                                                                                                                      
# 请输入查询 (输入 'q' 退出): q                                                                                                                                                                                                       
# 程序已退出           
```
## TIPS:
运行中出现：

        chromadb.errors.InvalidArgumentError: Collection expecting embedding with dimension of 384, got 512

这个错误是因为向量维度不匹配！你的新模型输出512维向量，但已存在的Chroma数据库是384维的（应该是之前用all-MiniLM-L6-v2创建的）。 需要删除旧的向量数据库，换成新的。

```python
import shutil

def build_or_load_vector_store(docs, persist_directory="./chroma_db"):
    embeddings = SentenceTransformerEmbeddings()
    
    # 如果维度可能不匹配，强制删除旧数据库
    if os.path.exists(persist_directory):
        print(f"⚠️ 删除旧的向量数据库: {persist_directory}")
        shutil.rmtree(persist_directory)
    
    print("======================= 创建新索引 =======================")
    vector_store = Chroma.from_documents(
        docs,
        embeddings,
        persist_directory=persist_directory
    )
    print(f"创建了 {vector_store._collection.count()} 个文档")
    return vector_store
```
