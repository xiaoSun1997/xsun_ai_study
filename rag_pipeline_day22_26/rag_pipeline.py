# rag_pipeline_day22_26.py
import logging
from typing import Dict, List, Any, Optional
from document_processor import DocumentProcessor
from vector_store import VectorStore
from retriever import HybridRetriever
from generator import ResponseGenerator
from config import Config

logger = logging.getLogger(__name__)


class RAGPipeline:
    """完整的RAG管道"""

    def __init__(
            self,
            knowledge_base_path: str = "./knowledge_base",
            vector_store_path: str = None,
            use_existing_vector_store: bool = True
    ):
        self.knowledge_base_path = knowledge_base_path
        self.vector_store_path = vector_store_path or Config.VECTOR_STORE_PATH

        # 初始化组件
        logger.info("初始化RAG管道组件...")

        self.document_processor = DocumentProcessor()
        self.vector_store = VectorStore(persist_directory=self.vector_store_path)
        self.retriever = HybridRetriever(self.vector_store)
        self.generator = ResponseGenerator()

        # 构建知识库（如果需要）
        if not use_existing_vector_store or self.vector_store.get_stats()["document_count"] == 0:
            self.build_knowledge_base()

        logger.info("RAG管道初始化完成")

    def build_knowledge_base(self):
        """构建知识库"""
        logger.info(f"开始构建知识库: {self.knowledge_base_path}")

        # 处理文档
        documents = self.document_processor.process_directory(self.knowledge_base_path)

        if not documents:
            logger.warning("没有找到可处理的文档")
            return

        # 添加到向量库
        self.vector_store.add_documents(documents)

        stats = self.vector_store.get_stats()
        logger.info(f"知识库构建完成，包含 {stats['document_count']} 个文档块")

    def query(
            self,
            question: str,
            top_k: int = Config.RETRIEVAL_TOP_K,
            generate_response: bool = True,
            return_contexts: bool = True
    ) -> Dict[str, Any]:
        """执行完整RAG流程"""

        logger.info(f"处理查询: {question}")

        result = {
            "question": question,
            "retrieval": None,
            "generation": None,
            "metadata": {}
        }

        # 1. 检索阶段
        retrieval_result = self.retriever.retrieve_with_explanation(
            query=question,
            k=top_k
        )

        result["retrieval"] = retrieval_result
        result["metadata"]["retrieval_time"] = "..."  # 可以添加时间统计

        # 如果没有检索到结果
        if not retrieval_result["results"]:
            result["generation"] = {
                "response": "抱歉，没有找到相关信息来回答这个问题。",
                "contexts_used": 0,
                "citations": []
            }
            return result

        # 2. 生成阶段（如果需要）
        if generate_response:
            contexts = [r["content"] for r in retrieval_result["results"]]

            generation_result = self.generator.generate_with_context(
                query=question,
                contexts=contexts
            )

            result["generation"] = generation_result
            result["metadata"]["generation_time"] = "..."  # 可以添加时间统计

        # 3. 返回上下文（如果需要）
        if return_contexts:
            result["contexts"] = [
                {
                    "content": r["content"],
                    "score": r["score"],
                    "source": r["source"],
                    "metadata": r["metadata"]
                }
                for r in retrieval_result["results"]
            ]

        logger.info(f"查询处理完成，使用 {len(retrieval_result['results'])} 个上下文")
        return result

    def batch_query(self, questions: List[str], **kwargs) -> List[Dict[str, Any]]:
        """批量查询"""
        results = []
        for question in questions:
            result = self.query(question, **kwargs)
            results.append(result)
        return results

    def get_pipeline_info(self) -> Dict[str, Any]:
        """获取管道信息"""
        vector_stats = self.vector_store.get_stats()

        return {
            "pipeline_components": {
                "document_processor": "active",
                "vector_store": "active",
                "retriever": "active",
                "generator": "active"
            },
            "vector_store_stats": vector_stats,
            "config": {
                "embedding_model": Config.EMBEDDING_MODEL,
                "generation_model": Config.GENERATION_MODEL,
                "retrieval_top_k": Config.RETRIEVAL_TOP_K,
                "chunk_size": Config.CHUNK_SIZE
            }
        }

    def evaluate_retrieval(self, query: str, expected_keywords: List[str]) -> Dict[str, Any]:
        """评估检索效果"""
        retrieval_result = self.retriever.retrieve(query)

        # 计算召回率
        total_keywords = len(expected_keywords)
        found_keywords = 0

        for result in retrieval_result:
            content = result["content"].lower()
            for keyword in expected_keywords:
                if keyword.lower() in content:
                    found_keywords += 1
                    break  # 每个关键词只计算一次

        recall = found_keywords / total_keywords if total_keywords > 0 else 0

        return {
            "query": query,
            "total_results": len(retrieval_result),
            "recall_rate": recall,
            "expected_keywords": expected_keywords,
            "found_keywords": found_keywords
        }