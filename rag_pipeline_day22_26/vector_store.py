import logging
from typing import Dict, List, Optional, Tuple, Any

import chromadb
from chromadb import Settings

from config import Config
from embedding_model import AdvancedEmbeddingModel

logger = logging.getLogger(__name__)

class VectorStore:
    """向量数据库"""

    def __init__(self, persist_directory: str = None):
        self.persist_directory = persist_directory or Config.VECTOR_STORE_PATH
        self.embedding_model = AdvancedEmbeddingModel()
        self.collection_name = Config.COLLECTION_NAME
        # 初始化chroma客户端
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        self.collection = self._get_or_create_collection()

    def _get_or_create_collection(self):
        """获取或创建集合"""
        try:
            # 尝试获取现有集合
            collection = self.client.get_collection(
                name=self.collection_name
            )
            logger.info(f"加载现有集合: {self.collection_name}")

        except Exception as e:
            # 创建新集合
            logger.info(f"创建新集合: {self.collection_name}")
            collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}  # 使用余弦相似度
            )

        return collection

    def add_documents(self, documents: List[Dict], ids: Optional[List[str]] = None):
        """添加文档到向量库"""
        if not documents:
            logger.warning("没有文档可添加")
            return

        # 提取内容和元数据
        contents = [doc.get("content", "") for doc in documents]
        metadatas = [doc.get("metadata", {}) for doc in documents]

        # 如果没有提供ID，自动生成
        if ids is None:
            ids = [f"doc_{i}_{hash(content)}" for i, content in enumerate(contents)]

        # 添加到集合
        self.collection.add(
            documents=contents,
            metadatas=metadatas,
            ids=ids
        )

        logger.info(f"成功添加 {len(documents)} 个文档")
        # 在新版本的 ChromaDB 中，数据会自动持久化，无需手动调用 persist()

    def search(
            self,
            query: str,
            k: int = Config.RETRIEVAL_TOP_K,
            filter_condition: Optional[Dict] = None,
            use_mmr: bool = Config.USE_MMR
    ) -> List[Tuple[str, float, Dict]]:
        """搜索相似文档"""

        # 执行查询
        if use_mmr:
            # MMR搜索（平衡相关性和多样性）
            results = self.collection.query(
                query_texts=[query],
                n_results=k * 2,  # 获取更多结果用于MMR
                where=filter_condition,
                include=["documents", "metadatas", "distances"]
            )

            # 应用MMR算法
            final_results = self._apply_mmr(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0],
                k=k,
                diversity=Config.MMR_DIVERSITY
            )
        else:
            # 普通相似度搜索
            results = self.collection.query(
                query_texts=[query],
                n_results=k,
                where=filter_condition,
                include=["documents", "metadatas", "distances"]
            )

            final_results = list(zip(
                results["documents"][0],
                results["distances"][0],
                results["metadatas"][0]
            ))

        return final_results

    def _apply_mmr(self, documents, metadatas, distances, k: int, diversity: float):
        """应用最大边际相关性算法"""
        # 将距离转换为相似度分数
        similarities = [1 - d for d in distances]

        selected_indices = []
        candidate_indices = list(range(len(documents)))

        # 第一步：选择最相关的文档
        if candidate_indices:
            best_idx = max(candidate_indices, key=lambda i: similarities[i])
            selected_indices.append(best_idx)
            candidate_indices.remove(best_idx)

        # 后续步骤：平衡相关性和多样性
        while len(selected_indices) < k and candidate_indices:
            scores = []

            for cand_idx in candidate_indices:
                # 相关性分数
                relevance_score = similarities[cand_idx]

                # 与已选文档的最大相似度（用于衡量多样性）
                max_similarity_to_selected = 0
                if selected_indices:
                    # 这里简化处理，实际应计算嵌入向量的相似度
                    max_similarity_to_selected = max(
                        similarities[cand_idx]
                        for sel_idx in selected_indices
                    )

                # MMR分数：λ * 相关性 - (1-λ) * 与已选文档的相似度
                mmr_score = diversity * relevance_score - (1 - diversity) * max_similarity_to_selected
                scores.append((cand_idx, mmr_score))

            # 选择MMR分数最高的文档
            best_cand_idx = max(scores, key=lambda x: x[1])[0]
            selected_indices.append(best_cand_idx)
            candidate_indices.remove(best_cand_idx)

        # 构建结果
        results = []
        for idx in selected_indices:
            results.append((
                documents[idx],
                1 - distances[idx],  # 返回相似度分数
                metadatas[idx]
            ))

        return results

    def get_stats(self) -> Dict[str, Any]:
        """获取向量库统计信息"""
        count = self.collection.count()

        return {
            "collection_name": self.collection_name,
            "document_count": count,
            "embedding_dimension": self.embedding_model.dimension,
            "persist_directory": self.persist_directory
        }

    def clear(self):
        """清空向量库"""
        try:
            self.client.delete_collection(self.collection_name)
            logger.info("向量库已清空")
        except Exception as e:
            logger.warning(f"删除集合时出错: {e}")