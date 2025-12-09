# 配置文件
class Config:
    # 嵌入模型配置
    EMBEDDING_MODEL = "BAAI/bge-small-zh-v1.5"
    EMBEDDING_DIM = 512
    EMBEDDING_DEVICE = "cpu"

    # 文本分割配置
    CHUNK_SIZE = 500
    CHUNK_OVERLAP = 100
    SEPARATORS = ["\n\n", "\n", "。", "！", "？", "，", "；"]

    # 向量存储配置
    VECTOR_STORE_PATH = "./vector_store"
    COLLECTION_NAME = "knowledge_base"

    # 检索配置
    RETRIEVAL_TOP_K = 3
    RETRIEVAL_SCORE_THRESHOLD = 0.3  # 降低阈值以便检索到更多结果
    USE_MMR = True
    MMR_DIVERSITY = 0.5

    # 生成模型配置
    GENERATION_MODEL = "gpt2"
    MAX_NEW_TOKENS = 500
    TEMPERATURE = 0.7
    TOP_P = 0.9

    # RAG配置
    RAG_PROMPT_TEMPLATE = """
    基于以下上下文信息，请回答问题。如果你不知道答案，就说不知道，不要编造信息。

    上下文信息：
    {context}
    
    问题：{question}
    
    请基于上述上下文信息回答："""