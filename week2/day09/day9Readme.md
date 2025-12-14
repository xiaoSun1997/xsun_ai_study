今日目标  尝试 HuggingFace Transformers Pipeline

# 一、什么是 HuggingFace Transformers 的 pipeline？

一句话：pipeline 是一个高层封装，让你“几行代码用大模型干活”，而不用自己操心模型选择、tokenizer、前后处理等细节。

它做了几件事：
    
    1. 自动下载 & 加载模型和 tokenizer
    
        你只要写：pipeline("sentiment-analysis")
        
        它会去 Hugging Face Hub 找默认模型（例如 distilbert-base-uncased-finetuned-sst-2-english），自动下载并缓存。
        
    2. 统一调用方式
    
        无论是情感分析、文本生成、翻译还是问答，你基本都用：
        
        pipe = pipeline("task_name", model=..., tokenizer=...)
        pipe("some input")
    
    
    3. 自动前处理 & 后处理
    
        前处理：文本转 token、padding、truncation、转 tensor 等
        
        后处理：根据任务输出结构化结果，比如：
        
        [{'label': 'POSITIVE', 'score': 0.9998}]
        
        
    4. 屏蔽框架细节
    
        底层可以是 PyTorch / TensorFlow / JAX，但对你来说就是调用函数。

---
# 二、pipeline 常见任务类型（task）

常见 task 字符串（传给 pipeline("xxx") 的那个）：

## 文本相关
    
    "sentiment-analysis"：情感分析 / 二分类
    
    "text-classification"：通用文本分类（多分类、多标签）
    
    "text-generation"：文本生成（像 GPT 那样补全）
    
    "text2text-generation"：输入文本 → 输出文本（翻译、摘要、改写等）
    
    "translation" 或 "translation_xx_to_yy"：翻译
    
    "summarization"：文本摘要
    
    "question-answering"：阅读理解式问答（给上下文 + 问题）
    
    "fill-mask"：MLM 填空（[MASK]）

## 视觉相关
    
    "image-classification"：图像分类
    
    "object-detection"：目标检测
    
    "image-segmentation"：分割
    
    "image-to-text"：图像描述（caption）

## 多模态

    "zero-shot-classification"：零样本分类（给候选 label，直接判断）
    
    "zero-shot-image-classification"
    
    "visual-question-answering" 等


你可以先专注在文本类任务：sentiment-analysis, text-generation, question-answering，这些最容易上手。

---
# 三、pipeline 的关键参数

    from transformers import pipeline
    pipe = pipeline(
        task,                 # 任务名，例如 "sentiment-analysis"
        model=None,           # 可选，指定模型名或者本地路径
        tokenizer=None,       # 可选，指定 tokenizer
        device=None,          # GPU/CPU，如 0 表示用第一块 GPU，-1 表示 CPU
        batch_size=1,         # 批大小
        truncation=True,      # 是否截断过长输入
        max_length=None,      # 最大长度
        **task_specific_args  # 每种任务有自己特定的参数
    )
    

## 常用点：

### 选择模型

    pipe = pipeline("sentiment-analysis")  # 用默认
    pipe = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")


### 指定设备

    pipe = pipeline("sentiment-analysis", device=-1)  # CPU
    pipe = pipeline("sentiment-analysis", device=0)   # 第 0 块 GPU


### 批处理输入

    pipe(["I love this!", "This is bad..."])


### 任务特定参数（以 text-generation 为例）

    generator = pipeline("text-generation", model="gpt2")
    generator(
        "Once upon a time",
        max_length=50,
        num_return_sequences=3,
        do_sample=True,
        temperature=0.7
    )

---

# 四、相关的基础知识点（由浅到深）
## 1. 模型（Model）

通过名字加载，例如：

    bert-base-uncased
    
    distilbert-base-uncased-finetuned-sst-2-english
    
    gpt2

这些名字对应 Hugging Face Hub 上的仓库（repo）。

## 2. Tokenizer

负责把文本 → token id，再转回文本：
    
        分词 / 子词切分（BPE、WordPiece 等）
        
        加上特殊 token（[CLS], [SEP], <pad> 等）
    
pipeline 会根据模型自动选择默认 tokenizer，一般你不用自己管。

## 3. Config

模型结构和一些超参数：

    隐藏层大小、层数、head 数量等

一般只需要知道它存在： AutoConfig.from_pretrained(model_name)

## 4. Auto 类（很重要）

AutoModel, AutoModelForSequenceClassification, AutoTokenizer 等：

不用记每个模型类名，只用 Auto 类：

    from transformers import AutoModelForSequenceClassification, AutoTokenizer
    model = AutoModelForSequenceClassification.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")
    tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")

## 5. 与 pipeline 的关系

pipeline 内部就做了类似事情：

    根据 model 名自动加载模型和 tokenizer
    
    把你的输入转换为模型能理解的张量
    
    调用模型
    
    把输出转成易读的结构

# 五、从 0 开始写一个完整 demo（含安装）

下面我一步一步写，你只要按顺序执行即可。我们做三件事：

    情感分析（sentiment analysis）
    
    文本生成（text generation）
    
    问答（question answering）

0. 环境准备

建议用虚拟环境（可选，但推荐）：

    # 创建并激活虚拟环境（以 venv 为例，Windows / Linux 都类似）
    python -m venv hf_env
    # Windows:
    hf_env\Scripts\activate
    # Linux / macOS:
    source hf_env/bin/activate
    

安装依赖：

    pip install --upgrade pip
    pip install "transformers[torch]"  # transformers + PyTorch
    # 如果你已有 torch，可以只安装 transformers
    # pip install transformers


如果下载模型慢，可以后面再问我国内加速方法。

1. 情感分析 demo

保存为 sentiment_demo.py：
    
    from transformers import pipeline
    
    def main():
        # 1. 创建情感分析 pipeline
        sentiment_pipe = pipeline("sentiment-analysis")
    
        # 2. 分析单句
        result_single = sentiment_pipe("I love Hugging Face transformers!")
        print("Single sentence result:")
        print(result_single)
        # 输出示例: [{'label': 'POSITIVE', 'score': 0.9998}]
    
        # 3. 分析多句（批处理）
        texts = [
            "I love Hugging Face transformers!",
            "This is the worst movie I have ever seen."
        ]
        result_batch = sentiment_pipe(texts)
        print("\nBatch result:")
        for text, res in zip(texts, result_batch):
            print(f"Text: {text}")
            print(f"  → label: {res['label']}, score: {res['score']:.4f}")
    
    if __name__ == "__main__":
        main()
    

运行：

    python sentiment_demo.py


首次运行会自动下载模型，之后走缓存。

2. 文本生成 demo（像小型 GPT）

保存为 text_generation_demo.py：
    
    from transformers import pipeline
    
    def main():
        # 1. 创建文本生成 pipeline
        # 默认会加载 gpt2
        generator = pipeline("text-generation", model="gpt2")
    
        prompt = "In the future, artificial intelligence will"
    
        # 2. 生成三段不同的续写
        outputs = generator(
            prompt,
            max_length=50,         # 最长 token 数
            num_return_sequences=3,
            do_sample=True,        # 采样，更有随机性
            temperature=0.7        # 温度，越高越随机
        )
    
        for i, out in enumerate(outputs):
            print(f"\n=== Generated #{i+1} ===")
            print(out["generated_text"])
    
    if __name__ == "__main__":
        main()

3. 问答 demo（阅读理解式）

我们给一段上下文 + 问题，从中抽取答案。

保存为 qa_demo.py：
    
    from transformers import pipeline
    
    def main():
        # 1. 创建问答 pipeline
        qa = pipeline("question-answering")
    
        # 2. 准备 context（文章）和 question（问题）
        context = """
        Hugging Face is a company that develops tools for building applications
        using machine learning. The Transformers library provides thousands
        of pretrained models to perform tasks on different kinds of data such as
        text, images, and audio.
        """
    
        question = "What does the Transformers library provide?"
    
        # 3. 调用 pipeline
        result = qa(question=question, context=context)
    
        print("Question:", question)
        print("Answer:", result["answer"])
        print("Score:", result["score"])
    
    if __name__ == "__main__":
        main()

六、如果你想“不要 pipeline，只用模型”的对比示例

为了理解 pipeline 帮你做了什么，这里放一个不用 pipeline 的情感分析版本（对比用，不用背）：
    
    import torch
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    
    model_name = "distilbert-base-uncased-finetuned-sst-2-english"
    
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    
    text = "I love Hugging Face transformers!"

# 1. 手动前处理
    inputs = tokenizer(text, return_tensors="pt")

# 2. 前向计算
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits

# 3. 手动后处理
    probs = torch.softmax(logits, dim=-1)
    pred = torch.argmax(probs, dim=-1).item()
    labels = ["NEGATIVE", "POSITIVE"]
    print(labels[pred], probs[0, pred].item())


对比一下你就知道：pipeline 把这些步骤都封装起来了。

七、下一步你可以怎么玩？

几个可以继续尝试的方向：

中文情感分析

    from transformers import pipeline
    pipe = pipeline("sentiment-analysis", model="uer/roberta-base-finetuned-jd-binary-chinese")
    print(pipe("这个产品真的很好用！"))


中文摘要

    summarizer = pipeline("summarization", model="IDEA-CCNL/Randeng-Pegasus-238M-Summary-Chinese")


零样本分类（零样本业务场景分类可用）
    
    classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
    classifier(
        "This is a message from a SCADA control system.",
        candidate_labels=["SCADA traffic", "web browsing", "email"]