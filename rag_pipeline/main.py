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