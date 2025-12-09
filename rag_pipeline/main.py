# main.py
import os
import logging
import argparse
from rag_pipeline import RAGPipeline

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="RAG Pipeline 系统")
    parser.add_argument("--mode", choices=["build", "query", "interactive", "test"],
                        default="interactive", help="运行模式")
    parser.add_argument("--query", type=str, help="查询问题")
    parser.add_argument("--knowledge-base", type=str, default="./knowledge_base",
                        help="知识库目录路径")
    parser.add_argument("--vector-store", type=str, default="./vector_store",
                        help="向量存储路径")
    parser.add_argument("--top-k", type=int, default=3,
                        help="检索的文档数量")

    args = parser.parse_args()

    # 检查知识库目录
    if not os.path.exists(args.knowledge_base):
        logger.warning(f"知识库目录不存在: {args.knowledge_base}")
        os.makedirs(args.knowledge_base, exist_ok=True)
        logger.info(f"已创建知识库目录: {args.knowledge_base}")

    # 初始化RAG管道
    logger.info("初始化RAG管道...")
    rag_pipeline = RAGPipeline(
        knowledge_base_path=args.knowledge_base,
        vector_store_path=args.vector_store
    )

    # 获取管道信息
    pipeline_info = rag_pipeline.get_pipeline_info()
    logger.info(f"管道信息: {pipeline_info}")

    if args.mode == "build":
        logger.info("知识库构建模式")
        # 已经在初始化时构建了知识库
        return

    elif args.mode == "query" and args.query:
        logger.info(f"执行查询: {args.query}")
        result = rag_pipeline.query(args.query, top_k=args.top_k)

        # 打印结果
        print("\n" + "=" * 60)
        print(f"问题: {result['question']}")
        print("=" * 60)

        if result.get("generation"):
            print(f"\n回答: {result['generation']['response']}")
            print(f"\n基于 {result['generation']['contexts_used']} 个上下文生成")

            # 显示引用
            if result['generation']['citations']:
                print("\n引用来源:")
                for citation in result['generation']['citations']:
                    print(f"  - {citation['content_preview']}")

        # 显示检索结果
        if result.get("contexts"):
            print(f"\n检索到的上下文 ({len(result['contexts'])} 个):")
            for i, ctx in enumerate(result['contexts'], 1):
                print(f"\n{i}. [分数: {ctx['score']:.4f}] {ctx['source']}")
                print(f"   {ctx['content'][:200]}...")

    elif args.mode == "test":
        # 测试查询
        test_queries = [
            "什么是余弦相似度?",
            "向量是什么？",
            "ANN是什么？"
        ]

        for query in test_queries:
            print(f"\n{'=' * 60}")
            print(f"测试查询: {query}")
            result = rag_pipeline.query(query, top_k=args.top_k)

            if result.get("generation"):
                print(f"回答: {result['generation']['response'][:200]}...")

            print(f"检索到 {len(result.get('contexts', []))} 个上下文")

    else:  # interactive mode
        print("\n" + "=" * 60)
        print("RAG Pipeline 交互模式")
        print("输入 'quit' 或 'exit' 退出")
        print("=" * 60)

        while True:
            try:
                question = input("\n请输入问题: ").strip()

                if question.lower() in ['quit', 'exit', 'q']:
                    print("再见！")
                    break

                if not question:
                    continue

                # 执行查询
                result = rag_pipeline.query(question, top_k=args.top_k)

                # 显示结果
                print(f"\n回答: {result['generation']['response']}")

                # 显示来源
                if result.get("contexts"):
                    print(f"\n来源 ({len(result['contexts'])} 个):")
                    for i, ctx in enumerate(result['contexts'], 1):
                        print(f"\n{i}. 《{ctx['source']}》[相关度: {ctx['score']:.2%}]")
                        print(f"   {ctx['content'][:150]}...")

            except KeyboardInterrupt:
                print("\n程序被中断")
                break
            except Exception as e:
                logger.error(f"处理查询时出错: {e}")
                print(f"抱歉，处理问题时出错: {e}")


if __name__ == "__main__":
    main()

# (venv) PS E:\code\xsun_ai_study\rag_pipeline> python main.py --mode test
# 2025-12-09 19:36:21,472 - __main__ - INFO - 初始化RAG管道...
# 2025-12-09 19:36:21,472 - rag_pipeline - INFO - 初始化RAG管道组件...
# 2025-12-09 19:36:21,473 - embedding_model - INFO - 正在加载嵌入模型: BAAI/bge-small-zh-v1.5
# 2025-12-09 19:36:21,477 - sentence_transformers.SentenceTransformer - INFO - Load pretrained SentenceTransformer: BAAI/bge-small-zh-v1.5
# Batches: 100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 36.32it/s]
# 2025-12-09 19:36:26,255 - embedding_model - INFO - 模型加载成功，维度: 512
# 2025-12-09 19:36:26,458 - vector_store - INFO - 加载现有集合: knowledge_base
# 2025-12-09 19:36:26,458 - generator - INFO - 加载生成模型: gpt2 (设备: cpu)
# `torch_dtype` is deprecated! Use `dtype` instead!
# 2025-12-09 19:36:28,918 - generator - INFO - 生成模型加载完成
# 2025-12-09 19:36:28,969 - rag_pipeline - INFO - RAG管道初始化完成
# 2025-12-09 19:36:28,970 - __main__ - INFO - 管道信息: {'pipeline_components': {'document_processor': 'active', 'vector_store': 'active', 'retriever': 'active', 'generator': 'active'}, 'vector_store_stats': {'collection_name': 'knowledge_base', 'document_count': 50, 'embedding_dimension': 512, 'persist_directory': './vector_store'}, 'config': {'embedding_model': 'BAAI/bge-small-zh-v1.5', 'generation_model': 'gpt2', 'retrieval_top_k': 3, 'chunk_size': 500}}
#
# ============================================================
# 测试查询: 什么是余弦相似度?
# 2025-12-09 19:36:28,970 - rag_pipeline - INFO - 处理查询: 什么是余弦相似度?
# 2025-12-09 19:36:28,970 - retriever - INFO - 检索查询: 什么是余弦相似度?
# 2025-12-09 19:36:29,383 - retriever - INFO - 向量检索返回 6 个原始结果
# 2025-12-09 19:36:29,384 - retriever - INFO - 阈值过滤后剩余 6 个结果 (阈值: 0.3)
# 2025-12-09 19:36:29,384 - retriever - INFO - 检索完成，返回 3 个结果
# 2025-12-09 19:36:29,384 - generator - INFO - 生成提示词长度: 1096 字符
# 2025-12-09 19:36:29,385 - generator - INFO - 生成提示词:
#     基于以下上下文信息，请回答问题。如果你不知道答案，就说不知道，不要编造信息。
#
#     上下文信息：
#     [上下文 1]: #
# # --- 结果 3 (相似度: 1.2962) ---
#
# [上下文 2]: ---
#
# ## 余弦相似度：衡量两个向量“方向是否相似”
#
# 1. 定义
#
# 余弦相似度（cosine similarity）：
#
#     cos_sim(a,b) = a⋅b /  |a||b|  = a/|a| * b/|b|
#
# 根据刚才的几何意义，其实这就是cos θ，θ 是两个向量的夹角。
#
# - 取值范围：[-1, 1]
#
#     - 1：完全同方向，非常相似
#
#     - 0：正交（垂直），没啥关系
#
#     - -1：完全反方向，非常不相似（对立）
#
# 在文本 Embedding 里，一般不会出现特别负的情况，常见的是 0~1 之间。
#
# ---
#
# 2. 手算一个小例子（直观一点）
#
# 设：
#
# a = (1, 0)
#
# b = (1, 1)
#
# 1）求各自的单位向量：
#
#     a^ = a / |a| = (1, 0)
#     b^ = b / |b| = (1/√2, 1/√2)
#
#
#
# 2）代入公式：
#
#     cos_sim(a,b) = a^·b^ = (1, 0)·(1/√2, 1/√2) = 1/√2
#
# [上下文 3]: # 音乐家：增加肺活量同时稳定发声（声乐教师秘传）
# # 孕妇禁忌：孕中期后禁用（可能引起宫缩）
#
#     问题：什么是余弦相似度?
#
#     请基于上述上下文信息回答：
# 2025-12-09 19:36:56,379 - rag_pipeline - INFO - 查询处理完成，使用 3 个上下文
# 回答: x = x / x
#
# [上下文 3]: # 音乐家：增加肺活量同时稳定发声（声乐教师秘传）          x = x / x
#
# [上下文 3]: # 音乐家：增加肺活量同时稳定发声（声乐教师秘传）          x = x / x
#
# [上下文 3]: # 音乐家：增加肺活量同时稳定发声（声乐教师秘传）         x = x / x
#
# [上下文 3]: # 音乐家：增加肺活量同时稳定发...
# 检索到 3 个上下文
#
# ============================================================
# 测试查询: 向量是什么？
# 2025-12-09 19:36:56,380 - rag_pipeline - INFO - 处理查询: 向量是什么？
# 2025-12-09 19:36:56,380 - retriever - INFO - 检索查询: 向量是什么？
# 2025-12-09 19:36:56,649 - retriever - INFO - 向量检索返回 6 个原始结果
# 2025-12-09 19:36:56,649 - retriever - INFO - 阈值过滤后剩余 6 个结果 (阈值: 0.3)
# 2025-12-09 19:36:56,649 - retriever - INFO - 检索完成，返回 3 个结果
# 2025-12-09 19:36:56,650 - generator - INFO - 生成提示词长度: 824 字符
# 2025-12-09 19:36:56,650 - generator - INFO - 生成提示词:
#     基于以下上下文信息，请回答问题。如果你不知道答案，就说不知道，不要编造信息。
#
#     上下文信息：
#     [上下文 1]: # 运动员：提升核心稳定性（比普拉提训练效率高 20%）
# # 程序员：缓解"屏幕呼吸暂停症"
#
# [上下文 2]: # 页码: 2
# # 内容预览:
#
# [上下文 3]: # 音乐家：增加肺活量同时稳定发声（声乐教师秘传）
# # 孕妇禁忌：孕中期后禁用（可能引起宫缩）
#
#     问题：向量是什么？
#
#     请基于上述上下文信息回答：
# 2025-12-09 19:37:19,872 - rag_pipeline - INFO - 查询处理完成，使用 3 个上下文
# 回答: 向量的多转和
#
# [上下文 3]: # 心朋达池记＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝...
# 检索到 3 个上下文
#
# ============================================================
# 测试查询: ANN是什么？
# 2025-12-09 19:37:19,872 - rag_pipeline - INFO - 处理查询: ANN是什么？
# 2025-12-09 19:37:19,872 - retriever - INFO - 检索查询: ANN是什么？
# 2025-12-09 19:37:20,243 - retriever - INFO - 向量检索返回 6 个原始结果
# 2025-12-09 19:37:20,244 - retriever - INFO - 阈值过滤后剩余 6 个结果 (阈值: 0.3)
# 2025-12-09 19:37:20,244 - retriever - INFO - 检索完成，返回 3 个结果
# 2025-12-09 19:37:20,244 - generator - INFO - 生成提示词长度: 839 字符
# 2025-12-09 19:37:20,244 - generator - INFO - 生成提示词:
#     基于以下上下文信息，请回答问题。如果你不知道答案，就说不知道，不要编造信息。
#
#     上下文信息：
#     [上下文 1]: # 5.
# # 科学冷门机制：
#
# [上下文 2]: # 音乐家：增加肺活量同时稳定发声（声乐教师秘传）
# # 孕妇禁忌：孕中期后禁用（可能引起宫缩）
#
# [上下文 3]: # 页码: 2
# # 内容预览:
#
#     问题：ANN是什么？
#
#     请基于上述上下文信息回答：
# 2025-12-09 19:37:46,357 - rag_pipeline - INFO - 查询处理完成，使用 3 个上下文
# 回答: [上下文 3]: # 页码: 3...
# 检索到 3 个上下文