 AI Agent 工程师学习计划（20 周打卡版）

📅 阶段 1：LLM 与 LangChain 入门（第 1–4 周）
🎯 目标：掌握 Python 环境、LLM 调用、LangChain 基础、RAG 流程。

🧩 第1周：Python + FastAPI 基础

    [√] 周一：学习 Python 基础语法、列表、字典、函数
    [√] 周二：掌握虚拟环境（venv）与包管理（pip、requirements.txt）
    [√] 周三：学习 FastAPI 基础与路径参数
    [√] 周四：理解 async/await 异步机制
    [√] 周五：使用 requests 调用 HTTP 接口

🧩 第2周：LLM 调用与 Prompt 工程

    [√] 周一：调用 OpenAI ChatCompletion API
    [√] 周二：尝试 HuggingFace Transformers Pipeline
    [√] 周三：学习 Prompt 模板化设计（PromptTemplate）
    [√] 周四：Few-shot / Chain-of-Thought 提示技巧
    [√] 周五：封装 LLMClient 类，统一调用接口

🧩 第3周：LangChain 核心机制

    [√] 周一：理解 LangChain 基础结构（LLM、Prompt、Chain）
    [√] 周二：SequentialChain 实战  
        （fix 从 langchain v0.1.0 版本开始，SequentialChain 已被弃用，推荐使用 LangChain Expression Language (LCEL) 来构建链式调用。如果使用的是较新版本的 langchain，建议改用 RunnableSequence 或直接使用管道操作符 | 来连接组件。）
    [√] 周三：记忆机制（Memory）
    [√] 周四：学习 TextLoader / PDFLoader
    [√] 周五：Embedding 嵌入模型（SentenceTransformers）

🧩 第4周：RAG 构建与优化

    [√] 周一：向量数据库原理（相似度检索）
    [√] 周二：Chroma 基础与索引
    [√] 周三：实现 RAG Pipeline（Embedding + Retrieval + Generation）
    [√] 周四：优化 top-k 检索策略
    [ ] 周五：回答准确率测试
    [ ] 周末项目：✅ 文档问答Bot（RAG 系统）

📘 阶段 2：Agent 架构与 Java 整合（第 5–8 周）
🎯 目标：掌握 Agent 架构、多工具协作、LangChain4j 后端整合。

🧩 第5周：LangChain Agent 基础

    [ ] 周一：理解 Agent 结构（LLM + Tool + Executor）
    [ ] 周二：使用内置工具（PythonREPL、Search API）
    [ ] 周三：自定义 Tool 函数
    [ ] 周四：多工具组合执行链
    [ ] 周五：Agent 错误恢复与回退策略
    [ ] 周末项目：✅ 天气 + 搜索 + 计算 Agent

🧩 第6周：多 Agent 协作

    [ ] 周一：多Agent架构（Coordinator + Worker 模式）
    [ ] 周二：了解 LangGraph（流程化控制）
    [ ] 周三：组合多个工具链
    [ ] 周四：外部API封装（NewsAPI、Google Search）
    [ ] 周五：Agent 通信与上下文共享
    [ ] 周末项目：✅ 智能任务管家（多Agent协作系统）

🧩 第7周：LangChain4j 入门（Java）

    [ ] 周一：LangChain4j 安装与 Maven 配置
    [ ] 周二：Java 调用 OpenAI / Ollama API
    [ ] 周三：Prompt 模板与 Chain
    [ ] 周四：使用 Java SDK 集成 Chroma / Milvus
    [ ] 周五：封装 API 调用为 Tool
    [ ] 周末项目：✅ Java 知识库 Agent

🧩 第8周：Java + Python 协作架构

    [ ] 周一：学习 REST 架构与语言间协作方式
    [ ] 周二：FastAPI 提供服务，Java 端调用
    [ ] 周三：Spring Boot 调用 Python Agent 服务
    [ ] 周四：使用 Redis/Kafka 异步通信
    [ ] 周五：整合部署与测试
    [ ] 周末项目：✅ 企业智能问答系统（Java + LangChain）

🧠 阶段 3：模型微调与蒸馏（第 9–12 周）
🎯 目标：理解 Transformer、LoRA、蒸馏原理并能实际微调模型。

🧩 第9周：Transformer 理论理解

    [ ] 周一：Transformer Encoder/Decoder 机制
    [ ] 周二：Attention、QKV 计算原理
    [ ] 周三：Tokenizer 工作方式
    [ ] 周四：Embedding 训练与向量化
    [ ] 周五：模型评估指标（Perplexity）
    [ ] 周末项目：✅ 从Embedding到Transformer的完整数据流实验

🧠 第10周｜LoRA 与 PEFT 实战
🎯 目标：掌握参数高效微调（PEFT/LoRA），完成一个小模型微调。

🗓️ 周一｜理解 LoRA 原理

    ● 阅读论文或总结笔记：LoRA（Low-Rank Adaptation）核心思想
    ● 了解为什么只调整部分权重可以加快训练
    ● 手写一个 LoRA 原理示例图
    📘 推荐阅读：
    ● HuggingFace LoRA 官方文档
    ● 博客：《从零理解 LoRA 微调原理》

🗓️ 周二｜PEFT 框架上手

    ● 安装 peft 库 (pip install peft transformers accelerate)
    ● 熟悉 LoraConfig, get_peft_model 的使用方式
    ● 在 HuggingFace 上尝试给一个小模型（如 distilbert-base-uncased）添加 LoRA 层
    🧩 小练习：
    from peft import LoraConfig, get_peft_model

🗓️ 周三｜准备训练数据

    ● 了解监督微调（SFT）的数据格式（instruction + input + output）
    ● 使用 datasets 或自制 JSONL 数据
    ● 准备一个小领域数据集（如技术问答、公司知识文档）
    🧰 输出：data/train.jsonl + data/val.jsonl

🗓️ 周四｜运行微调训练
    
    ● 使用 Trainer 或 SFTTrainer 启动 LoRA 训练
    ● 学会设置超参数（learning_rate, epochs, batch_size）
    ● 观察 GPU 占用变化（对比 LoRA vs 全量训练）
    🧩 参考命令：
    python train_lora.py --model_name mistralai/Mistral-7B-Instruct

🗓️ 周五｜保存与测试微调模型
    
    ● 保存 Adapter 权重并单独加载
    ● 对比微调前后模型输出差异
    ● 记录日志（loss, accuracy, qualitative examples）
    ✅ 输出：
    models/
     ├── base_model/
     └── lora_adapter/

🗓️ 周末项目实战 10️⃣｜微调 Mistral 模型
    
    ● 准备 200–500 条领域数据（如 Java 技术问答）
    ● 使用 PEFT + LoRA 微调 Mistral 模型
    ● 保存 adapter 并在 FastAPI 中部署推理
    ● 写总结：《LoRA 微调从入门到部署》
    📈 成果：
    ✅ lora_model 可回答你自定义领域问题
    ✅ 输出到日志文件 / 本地API接口

⚙️ 第11周｜模型蒸馏与推理优化
🎯 目标：掌握蒸馏思想、模型量化（QLoRA）、推理部署（vLLM / Ollama）

🗓️ 周一｜模型蒸馏原理
    
    ● 学习 Teacher–Student 框架
    ● 理解知识蒸馏的目标函数（KL散度）
    ● 画出“Teacher→Student”架构图
    📘 推荐资料：
    ● 论文笔记：《Distilling the Knowledge in a Neural Network》

🗓️ 周二｜蒸馏实战
    
    ● 使用 distilbert 为例，实现简单蒸馏训练
    ● Teacher 模型为 BERT-base，Student 模型为 DistilBERT
    ● 比较蒸馏前后模型精度与速度
    🧩 小实验：
    teacher = AutoModelForSequenceClassification.from_pretrained("bert-base-uncased")
    student = AutoModelForSequenceClassification.from_pretrained("distilbert-base-uncased")

🗓️ 周三｜QLoRA 与模型量化
    
    ● 理解 QLoRA：量化 + LoRA 微调
    ● 使用 4bit 量化 (bitsandbytes)
    ● 比较 VRAM 占用差异
    🧩 命令：
    bnb.nn.Linear4bit()

🗓️ 周四｜推理部署（vLLM / Ollama）
    
    ● 安装并运行 vLLM 或 Ollama
    ● 了解 KV cache 与分布式推理原理
    ● 部署你的 LoRA 模型到本地
    ✅ 输出：
    localhost:8000/v1/completions

🗓️ 周五｜性能测试与日志记录
    
    ● 对比不同模型延迟、吞吐量
    ● 记录 prompt → 输出时间
    ● 优化 batch size 与 top_k
    🧠 可使用：
    ● timeit 测试脚本
    ● ab / wrk 性能压测

🗓️ 周末项目实战 11️⃣｜知识问答模型蒸馏
    
    ● 选择一个大模型 (Teacher)：Mistral / Llama3
    ● Student 模型：Phi-3-mini 或 Qwen-1.8B
    ● 用领域问答数据进行蒸馏训练
    ● 部署 Student 模型 + FastAPI 接口
    ● 编写 README & 结果对比表
    📈 成果：
    ✅ 自定义轻量模型（推理快、知识准）
    ✅ 可直接本地运行

🧩 第12周｜RAG 优化与向量数据库调优
🎯 目标：深入理解 Milvus / Weaviate，掌握索引优化、混合搜索与性能调优。

🗓️ 周一｜Milvus 基础
    
    ● 安装 pymilvus
    ● 创建集合、插入向量、执行搜索
    ● 理解 Schema、Index、Partition
    🧩 示例：
    from pymilvus import connections, Collection

🗓️ 周二｜索引类型对比
    
    ● 学习 IVF_FLAT, IVF_SQ8, HNSW 的差异
    ● 实测不同索引的查询性能
    ● 记录 top_k 与召回率对比
    🧠 输出：
    小表格：index_type vs recall vs latency

🗓️ 周三｜混合搜索与权重策略
    
    ● 结合 keyword + embedding 检索（hybrid search）
    ● 使用 BM25 + 向量加权融合
    ● 比较结果相关性
    🧩 工具：langchain.retrievers.MultiQueryRetriever

🗓️ 周四｜RAG 优化实践
    
    ● 融合 LoRA 模型 + Milvus 检索结果
    ● 封装优化版 RAG pipeline
    ● 增加多轮对话记忆
    ✅ 输出：RAG 优化版 Agent

🗓️ 周五｜性能监控与评估
    
    ● 统计查询延迟、embedding生成时间
    ● 使用 prometheus + grafana 简易监控
    ● 输出评估报告
    📊 输出：
    latency_report.md

🗓️ 周末项目实战 12️⃣｜高性能 RAG 问答系统
    
    ● 使用 Milvus + LoRA 模型 + LangChain 构建知识库问答
    ● 调整索引参数提升响应速度
    ● 部署至 FastAPI 接口
    ● 输出详细报告《RAG 优化实践总结》
    📈 成果：
    ✅ 问答速度提升 30%+
    ✅ 支持多轮上下文
    ✅ 已具备企业级性能

⚙️ 第13周｜多 Agent 后端整合
🎯 目标：实现 Java + Python Agent 多服务协作。
    
    ● 周一：Spring Boot 调用 Python 模型服务
    ● 周二：定义多 Agent 调度管理器
    ● 周三：引入 Redis 实现会话持久化
    ● 周四：异步任务与日志监控
    ● 周五：封装统一 REST API
    ● 周末项目⑬：构建“多 Agent 后端平台”

🌐 第14周｜React 前端与对话交互
🎯 目标：实现一个 Chat UI，与后端 Agent 实时交互。
    
    ● 周一：React 基础复习（Hooks、组件）
    ● 周二：与后端接口通信（Axios / Fetch）
    ● 周三：设计聊天窗口与滚动交互
    ● 周四：管理上下文状态（Redux / Context）
    ● 周五：增加动画（Framer Motion）
    ● 周末项目⑭：实现“智能对话前端界面”

🧱 第15周｜系统整合与容器部署
🎯 目标：Docker 化各模块并自动化部署。
    
    ● 周一：编写 Java、Python、React 各自 Dockerfile
    ● 周二：使用 Docker Compose 整合服务
    ● 周三：容器化部署 LLM 模型服务（vLLM / Ollama）
    ● 周四：使用 .env 管理配置
    ● 周五：GitHub Actions CI/CD 自动部署
    ● 周末项目⑮：构建“一键部署 AI 平台”

🚀 第16周｜系统联调与上线
🎯 目标：整合全栈系统并上线展示。
    
    ● 周一：联调前后端
    ● 周二：日志与监控（Prometheus + Grafana）
    ● 周三：用户系统与权限认证
    ● 周四：UI 优化与打包
    ● 周五：部署到公网（Render / VPS）
    ● 周末项目⑯：发布“企业 AI 助手平台”

⚡ 第17周｜Go 并发与性能优化（选修）
🎯 目标：用 Go 实现高并发 Agent 服务。
    
    ● 周一：Go 环境准备与基础语法
    ● 周二：使用 go-openai 实现 LLM 调用
    ● 周三：Milvus Go SDK 集成
    ● 周四：并发多 Agent 调度（goroutine + channel）
    ● 周五：性能测试与优化
    ● 周末项目⑰：Go 版高并发 Agent 平台

🤖 第18周｜LangGraph 与 CrewAI 多 Agent 协作
🎯 目标：构建多 Agent 流程图与协作系统。
    
    ● 周一：LangGraph 框架学习
    ● 周二：CrewAI 基础与任务配置
    ● 周三：自定义 Agent 角色
    ● 周四：Agent 记忆与上下文共享
    ● 周五：自动任务流实现
    ● 周末项目⑱：可视化多 Agent 工作流系统

📊 第19周｜模型评估与监控体系
🎯 目标：建立模型与 Agent 的评估系统。
    
    ● 周一：Prompt 评估指标（BLEU, ROUGE, GPTScore）
    ● 周二：自动生成测试数据集
    ● 周三：记录日志与分析调用效果
    ● 周四：构建可视化仪表盘
    ● 周五：实验记录自动化（DVC / MLflow）
    ● 周末项目⑲：构建“Agent 性能评估系统”

🏁 第20周｜最终综合实战与发布
🎯 目标：发布第一个完整 AI 产品。
    
    ● 周一：系统架构设计与模块划分
    ● 周二：模型选型与性能权衡
    ● 周三：部署优化与性能测试
    ● 周四：撰写用户文档与 README
    ● 周五：录制 Demo 视频与 GitHub 发布
    ● 周末项目⑳：发布“个人 AI 助手产品” ✅