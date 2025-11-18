今日目标：调用 OpenAI ChatCompletion API
✅ 一、创建空文件夹并初始化项目结构

假设你在某个路径下创建一个新文件夹，例如：

    qwen_demo/


进入文件夹后，创建如下结构：

    qwen_demo/
    ├── main.py
    ├── .env
    └── requirements.txt

✅ 二、准备虚拟环境（可选，但推荐）

在项目目录下执行：

    python3 -m venv venv
    source venv/bin/activate     # macOS / Linux
    # 或 Windows:
    # venv\Scripts\activate

✅ 三、requirements.txt 内容

    openai>=1.3.0
    python-dotenv


安装依赖：

    pip install -r requirements.txt

✅ 四、创建 .env 文件存放你的 DASHSCOPE_API_KEY
    
    DASHSCOPE_API_KEY=你的API密钥


（密钥从 dashscope 控制台获取。）

✅ 五、main.py 完整 Demo（可直接运行）

    import os
    from openai import OpenAI
    from dotenv import load_dotenv

    # 读取 .env 文件里的 DASHSCOPE_API_KEY
    load_dotenv()

    # 初始化客户端
    client = OpenAI(
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )

    def main():
        # 调用 Qwen Chat Completion
        completion = client.chat.completions.create(
            model="qwen-plus",  # 可换成其它模型
            messages=[
                {'role': 'system', 'content': 'You are a helpful assistant.'},
                {'role': 'user', 'content': '你是谁？最强的能力是什么？'}
            ]
        )
    
        # 输出结果
        print("模型回复：")
        print(completion.choices[0].message.content)
    
    if __name__ == "__main__":
        main()

✅ 六、运行程序

确保你在项目根目录：

    python main.py


输出示例：

    模型回复：
    我是通义千问（Qwen），是阿里巴巴集团研发的超大规模语言模型。我的设计目标是成为一款能够理解人类语言、支持多轮对话，并能在不同场景下提供帮助的AI助手。
    
    我最强的能力体现在以下几个方面：
    
    1. **语言理解与生成**：我可以准确理解复杂的语义，包括上下文、隐含意图和多语言内容，并生成自然流畅的回答。
       2.  **知识广度**：基于海量文本训练，我具备广泛的知识，涵盖科技、文化、生活等多个领域，能回答各种问题。
       3.  **逻辑推理与编程能力**：我能进行逻辑推理、数学计算和代码编写，支持多种编程语言。
       4.  **多模态处理**：除了文字，我还支持图像、语音等多模态信息的理解和生成（具体功能取决于部署版本）。
       5.  **个性化服务**：可以根据用户需求调整语气风格，提供定制化建议和服务。
    
    但最重要的是——**我始终在学习和进步**！如果你有任何问题或需要帮助，我会尽力为你提供支持 😊
    
    你想了解哪方面的具体内容呢？