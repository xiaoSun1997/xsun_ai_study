import chromadb
from openai import OpenAI

client = OpenAI(
    api_key="YOUR_KEY",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

chroma_client = chromadb.Client()
collection = chroma_client.create_collection(name="vector_collection")

docs = [
    "巴黎是法国的首都。",
    "东京是日本的首都。",
    "北京是中国的首都。"
]

collection.add(
    documents=docs,
    ids=[f"doc{i}" for i in range(len(docs))]
)

eval_set = [
    {
        "question": "中国的首都是哪里？",
        "answer": "北京。"
    },
    {
        "question": "东京是哪个国家的首都？",
        "answer": "东京是日本的首都。"
    },
    {
        "question": "巴黎是哪个国家的首都？",
        "answer": "巴黎是法国的首都。"
    }
]

def answer_question(question):
    query_result = collection.query(
        query_texts=[question],
        n_results=1
    )
    context = query_result["documents"][0][0]

    prompt = f"""
    已知信息：
    {context}

    问题：
    {question}

    请给出简洁准确的回答。
    """

    response = client.chat.completions.create(
        model="qwen-plus",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    return response.choices[0].message.content.strip()

def judge_answer(question, gt_answer,model_answer):
    prompt = f"""
    问题：
    {question}

    标准答案：
    {gt_answer}

    模型回单：
    {model_answer}
    
    请判断模型回答是否正确。
    只回答 YES 或 NO。
    """

    response = client.chat.completions.create(
        model="qwen-plus",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    return response.choices[0].message.content.strip().upper() == "YES"

def main():
    correct = 0

    for item in eval_set:
        model_answer = answer_question(item["question"])
        is_correct = judge_answer(item["question"], item["answer"], model_answer)
        print(item["question"], ":", model_answer, ":", is_correct)
        if is_correct:
            correct += 1

    accuracy = correct / len(eval_set)
    print(f"Accuracy:, {accuracy:.2f}")

if __name__ == "__main__":
    main()


# (day26venv) PS E:\code\xsun_ai_study\week4\day26> python main.py
# 中国的首都是哪里？ : 中国的首都是北京。 : True
# 东京是哪个国家的首都？ : 东京是日本的首都。 : True
# 巴黎是哪个国家的首都？ : 巴黎是法国的首都。 : True
# Accuracy:, 1.00