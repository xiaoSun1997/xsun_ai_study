import os

from dotenv import load_dotenv
from openai import OpenAI

# 读取 .env 文件里的 DASHSCOPE_API_KEY
load_dotenv()

client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

def main():
    completion = client.chat.completions.create(
        model="qwen-plus",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "你是谁？最强的能力是什么？"}
        ]
    )
    print("模型回复：")
    print(completion.choices[0].message.content)

if __name__ == "__main__":
    main()