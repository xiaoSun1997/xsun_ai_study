# document_processor.py
import os
from typing import List, Dict, Any
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    CSVLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
import logging
from config import Config

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """文档处理器"""

    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            separators=Config.SEPARATORS,
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP,
            length_function=len,
            is_separator_regex=False
        )

    def load_documents(self, file_paths: List[str]) -> List[Dict]:
        """加载多种格式的文档"""
        all_docs = []

        for file_path in file_paths:
            if not os.path.exists(file_path):
                logger.warning(f"文件不存在: {file_path}")
                continue

            file_ext = os.path.splitext(file_path)[1].lower()

            try:
                if file_ext == '.pdf':
                    loader = PyPDFLoader(file_path)
                elif file_ext == '.txt':
                    loader = TextLoader(file_path, encoding='utf-8')
                elif file_ext == '.csv':
                    loader = CSVLoader(file_path)
                else:
                    logger.warning(f"不支持的文件格式: {file_ext}")
                    continue

                documents = loader.load()

                # 添加元数据
                for doc in documents:
                    doc.metadata.update({
                        "source": os.path.basename(file_path),
                        "file_path": file_path,
                        "file_type": file_ext
                    })

                all_docs.extend(documents)
                logger.info(f"已加载 {len(documents)} 个文档块: {file_path}")

            except Exception as e:
                logger.error(f"加载文件失败 {file_path}: {e}")

        return all_docs

    def split_documents(self, documents: List) -> List[Dict]:
        """分割文档为chunks"""
        split_docs = self.text_splitter.split_documents(documents)

        # 转换为字典格式
        processed_docs = []
        for i, doc in enumerate(split_docs):
            processed_docs.append({
                "content": doc.page_content,
                "metadata": {
                    **doc.metadata,
                    "chunk_id": i,
                    "chunk_length": len(doc.page_content)
                }
            })

        logger.info(f"文档分割完成: {len(documents)} -> {len(processed_docs)} chunks")
        return processed_docs

    def process_directory(self, directory_path: str) -> List[Dict]:
        """处理整个目录的文档"""
        if not os.path.isdir(directory_path):
            logger.error(f"目录不存在: {directory_path}")
            return []

        # 收集所有支持的文件
        supported_extensions = ['.pdf', '.txt', '.docx', '.csv']
        file_paths = []

        for root, dirs, files in os.walk(directory_path):
            for file in files:
                if any(file.endswith(ext) for ext in supported_extensions):
                    file_paths.append(os.path.join(root, file))

        logger.info(f"发现 {len(file_paths)} 个文档文件")

        # 加载并处理所有文档
        documents = self.load_documents(file_paths)
        processed_docs = self.split_documents(documents)

        return processed_docs