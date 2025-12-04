# 项目结构
```text
rag_pipeline/
├── config.py              # 配置文件
├── embedding_model.py     # 嵌入模型
├── vector_store.py       # 向量存储
├── retriever.py          # 检索器
├── generator.py          # 生成器
├── rag_pipeline.py       # 完整RAG管道
├── knowledge_base/       # 知识库文档
|── document_processor.py       # 文档处理器
├── requirements.txt
└── main.py              # 主程序
```
添加依赖