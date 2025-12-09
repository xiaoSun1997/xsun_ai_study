# 嵌入模型
import logging

import numpy as np
from langchain_core.embeddings import Embeddings
from sentence_transformers import SentenceTransformer

from config import Config

logger = logging.getLogger(__name__)


class AdvancedEmbeddingModel(Embeddings):
    """高级嵌入模型，支持多种功能和优化"""

    def __init__(self, model_name: str = None,device: str = "cpu"):
        self.model_name = model_name or Config.EMBEDDING_MODEL
        self.device = device
        self.model = None
        self.dimension = None
        self._initialize_model()

    def _initialize_model(self):
        """初始化模型"""
        logger.info(f"正在加载嵌入模型: {self.model_name}")

        try:
            self.model = SentenceTransformer(
                self.model_name,
                device=self.device
            )

            # 测试维度
            test_embedding = self.model.encode("test")
            self.dimension = test_embedding.shape[0]
            logger.info(f"模型加载成功，维度: {self.dimension}")

        except Exception as e:
            logger.error(f"模型加载失败: {str(e)}")
            logger.error(f"模型名称: {self.model_name}, 设备: {self.device}")
            raise RuntimeError(f"无法加载嵌入模型 '{self.model_name}'，请检查模型名称和设备配置") from e

    def embed_query(self, text: str) -> list[float]:
        """嵌入查询文本"""
        if not text:
            logger.warning("接收到空文本输入")
            return []
            
        processed_text = self._preprocess_text(text)
        
        try:
            #生成嵌入
            embedding = self.model.encode(processed_text,
                                          convert_to_numpy=True,
                                          normalize_embeddings=True,
                                          show_progress_bar=False)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"嵌入查询文本时出错: {str(e)}")
            logger.error(f"输入文本: {processed_text[:100]}...")
            raise RuntimeError(f"无法对文本生成嵌入: {str(e)}") from e

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """嵌入文档列表"""
        if not texts:
            logger.warning("接收到空文档列表")
            return []
            
        processed_texts = [self._preprocess_text(text) for text in texts]
        
        try:
            #生成嵌入
            embeddings = self.model.encode(processed_texts,
                                           convert_to_numpy=True,
                                           batch_size=32,
                                           normalize_embeddings=True,
                                           show_progress_bar=False)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"嵌入文档列表时出错: {str(e)}")
            logger.error(f"文档数量: {len(processed_texts)}")
            raise RuntimeError(f"无法对文档列表生成嵌入: {str(e)}") from e

    def _preprocess_text(self, text: str) -> str:
        """文本预处理"""
        # 移除多余空白
        text = ' '.join(text.split())

        # 其他预处理逻辑
        # ...

        return text

    def compute_similarity(self, embedding1: list[float], embedding2: list[float]) -> float:
        """计算相似度"""
        try:
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)

            vec1 = vec1 / np.linalg.norm(vec1)
            vec2 = vec2 / np.linalg.norm(vec2)

            similarity = np.dot(vec1, vec2)
            return float(similarity)
        except Exception as e:
            logger.error(f"计算相似度时出错: {str(e)}")
            raise RuntimeError(f"无法计算相似度: {str(e)}") from e