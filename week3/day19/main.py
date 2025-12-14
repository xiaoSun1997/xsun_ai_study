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

# (day19venv) PS E:\code\xsun_ai_study\day19> python main.py
# Embedding dim:
# 384
# Corpus embeddings shape: (7, 384)
# 请输入查询：我今天很开心
#
# 查询: 我今天很开心
# 最相似的句子:
#   [0.8880] 我今天心情很好，因为拿到了工作机会。
#   [0.8802] 今天面试通过了，我觉得非常开心和兴奋。
#   [0.7838] 我打算周末去爬山放松一下心情。
# 请输入查询：