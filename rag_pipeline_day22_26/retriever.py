# retriever.py
from typing import List, Tuple, Dict, Any, Optional
import logging
from vector_store import VectorStore
from config import Config

logger = logging.getLogger(__name__)


class HybridRetriever:
    """混合检索器（支持多种检索策略）"""

    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store

    def retrieve(
            self,
            query: str,
            k: int = Config.RETRIEVAL_TOP_K,
            filters: Optional[Dict] = None,
            use_rerank: bool = True,
            score_threshold: float = Config.RETRIEVAL_SCORE_THRESHOLD
    ) -> List[Dict[str, Any]]:
        """检索相关文档"""

        logger.info(f"检索查询: {query}")

        # 1. 向量相似度检索
        vector_results = self.vector_store.search(
            query=query,
            k=k * 2,  # 获取更多结果用于重排序
            filter_condition=filters,
            use_mmr=Config.USE_MMR
        )

        logger.info(f"向量检索返回 {len(vector_results)} 个原始结果")
        
        # 记录所有检索结果的分数，便于调试
        for i, (_, score, _) in enumerate(vector_results):
            logger.debug(f"结果 {i+1} 分数: {score}")

        # 2. 应用分数阈值过滤
        filtered_results = [
            (doc, score, metadata)
            for doc, score, metadata in vector_results
            if score >= score_threshold
        ]
        
        logger.info(f"阈值过滤后剩余 {len(filtered_results)} 个结果 (阈值: {score_threshold})")

        # 3. 重排序（如果需要）
        if use_rerank and len(filtered_results) > 1:
            filtered_results = self._rerank_results(query, filtered_results)

        # 4. 返回Top K结果
        final_results = filtered_results[:k]

        # 格式化结果
        formatted_results = []
        for i, (content, score, metadata) in enumerate(final_results):
            formatted_results.append({
                "rank": i + 1,
                "content": content,
                "score": score,
                "metadata": metadata,
                "source": metadata.get("source", "unknown"),
                "page": metadata.get("page", "unknown")
            })

        logger.info(f"检索完成，返回 {len(formatted_results)} 个结果")
        return formatted_results

    def _rerank_results(self, query: str, results: List[Tuple]) -> List[Tuple]:
        """简单重排序策略"""

        # 这里可以实现更复杂的重排序逻辑
        # 例如：基于BM25、交叉编码器等

        # 当前实现：基于内容长度和分数的组合排序
        def ranking_score(item):
            content, score, metadata = item
            length_score = min(len(content) / 1000, 1.0)  # 长度在1000字以内最好
            return 0.7 * score + 0.3 * length_score

        sorted_results = sorted(results, key=ranking_score, reverse=True)
        return sorted_results

    def retrieve_with_explanation(
            self,
            query: str,
            k: int = Config.RETRIEVAL_TOP_K
    ) -> Dict[str, Any]:
        """检索并返回解释信息"""

        results = self.retrieve(query, k)

        # 分析检索结果
        if results:
            avg_score = sum(r["score"] for r in results) / len(results)
            max_score = max(r["score"] for r in results)
            min_score = min(r["score"] for r in results)

            sources = set(r["source"] for r in results)

            explanation = {
                "query": query,
                "total_results": len(results),
                "score_statistics": {
                    "average": avg_score,
                    "maximum": max_score,
                    "minimum": min_score
                },
                "sources": list(sources),
                "retrieval_strategy": "hybrid",
                "use_mmr": Config.USE_MMR,
                "score_threshold": Config.RETRIEVAL_SCORE_THRESHOLD
            }
        else:
            explanation = {
                "query": query,
                "total_results": 0,
                "message": "未找到相关文档"
            }

        return {
            "results": results,
            "explanation": explanation
        }