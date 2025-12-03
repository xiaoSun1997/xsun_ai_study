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