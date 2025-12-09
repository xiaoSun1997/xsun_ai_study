import chromadb
from sentence_transformers import SentenceTransformer




def get_embedding(texts):
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    # 确保texts始终是一个列表
    if isinstance(texts, str):
        texts = [texts]
    embeddings = model.encode(texts)
    return embeddings

def main():
    client = chromadb.Client()
    collection = client.create_collection(name="my_collection", metadata={"hnsw:space": "cosine"})
    documents = [
        "苹果是一种非常美味的水果，营养丰富。",
        "香蕉富含钾元素，对人体健康有益。",
        "今天的天气非常好，适合户外活动。",
        "股市近期的波动较大，有一定的投资风险。",
        "我喜欢吃草莓和蓝莓，尤其是在夏天。"
    ]
    # 修复：正确获取文档嵌入
    embeddings = get_embedding(documents)

    collection.add(
        ids=[str(i) for i in range(len(documents))],
        documents=documents, 
        embeddings=embeddings.tolist()  # 转换为列表格式
    )

    while True:
        query = input("请输入查询：")
        if query.lower() in ["q"]:
            break
        _query(query, collection, k=3)

def _query(query, collection, k=3):
    # 修复：正确获取和传递查询嵌入
    query_embedding = get_embedding([query])[0].tolist()  # 获取第一个（也是唯一一个）嵌入并向量转换为列表
    results = collection.query(
        query_embeddings=[query_embedding], 
        n_results=k
    )
    print(f"Query: {query}")
    # 修复：正确访问结果
    for i, (doc, score) in enumerate(zip(results['documents'][0], results['distances'][0])):
        print(f"Top {i+1}: {doc} (距离: {score:.4f})")

if __name__ == "__main__":
    main()
# 请输入查询：我喜欢吃水果
# Query: 我喜欢吃水果
# Top 1: 苹果是一种非常美味的水果，营养丰富。 (距离: 0.2655)
# Top 2: 我喜欢吃草莓和蓝莓，尤其是在夏天。 (距离: 0.3894)
# Top 3: 股市近期的波动较大，有一定的投资风险。 (距离: 0.4565)