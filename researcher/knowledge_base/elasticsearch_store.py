"""
Elasticsearch 知识库实现
"""
import json
from datetime import datetime
from typing import List, Optional, Sequence

import requests
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError
# from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_text_splitters import RecursiveCharacterTextSplitter


from researcher.config.settings import Settings, get_settings
from researcher.utils.logger import get_logger


class EmbeddingServiceError(Exception):
    """Embedding 服务调用异常"""


class EmbeddingService:
    """
    调用外部 Embedding 服务（OpenAI 兼容接口）
    """

    def __init__(
        self,
        base_url: str,
        api_key: str,
        model_name: str,
        timeout: int = 60,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model_name = model_name
        self.timeout = timeout
        self.logger = get_logger("embedding_service")

        self._session = requests.Session()
        self._session.headers.update(
            {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
        )

    def embed_text(self, text: str) -> List[float]:
        """
        为单段文本生成向量
        """
        return self.embed_batch([text])[0]

    def embed_batch(self, texts: Sequence[str]) -> List[List[float]]:
        """
        为多段文本生成向量
        """
        if not texts:
            return []

        endpoint = f"{self.base_url}/embeddings"
        payload = {
            "input": list(texts),
            "model": self.model_name,
        }

        try:
            response = self._session.post(endpoint, json=payload, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as exc:
            self.logger.error("调用 Embedding 服务失败: %s", exc)
            raise EmbeddingServiceError(str(exc)) from exc

        if "data" not in data:
            self.logger.error("Embedding 服务响应格式错误: %s", data)
            raise EmbeddingServiceError("Invalid response from embedding service")

        embeddings = []
        for item in data["data"]:
            embedding = item.get("embedding")
            if embedding is None:
                raise EmbeddingServiceError("Missing embedding in response item")
            embeddings.append(embedding)

        return embeddings


class ElasticsearchKnowledgeBase:
    """
    使用 Elasticsearch 存储论文知识库
    """

    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or get_settings()
        self.logger = get_logger("es_knowledge_base")

        self._validate_config()

        hosts = [
            {
                "host": self.settings.es_host,
                "port": self.settings.es_port,
                "scheme": self.settings.es_scheme,
            }
        ]

        es_url = f"{self.settings.es_scheme}://{self.settings.es_host}:{self.settings.es_port}"
        es_kwargs = {
            "hosts": [es_url],
            "compatibility_mode": True,
        }

        if self.settings.es_username and self.settings.es_password:
            es_kwargs["basic_auth"] = (self.settings.es_username, self.settings.es_password)

        if self.settings.es_scheme == "https":
            if self.settings.es_ca_cert_path:
                es_kwargs["ca_certs"] = self.settings.es_ca_cert_path
                es_kwargs["verify_certs"] = True
            else:
                es_kwargs["verify_certs"] = False

        self.client = Elasticsearch(**es_kwargs)

        self.index = self.settings.es_index
        self.embedding_service = EmbeddingService(
            base_url=self.settings.embedding_service_base_url,
            api_key=self.settings.embedding_service_api_key,
            model_name=self.settings.embedding_service_model_name,
        )

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=150,
            separators=["\n\n", "\n", "。", "！", "？", " ", ""],
        )

        # 确保索引存在
        self._ensure_index()

    def _validate_config(self) -> None:
        """
        校验配置
        """
        missing = []
        if not self.settings.embedding_service_base_url:
            missing.append("embedding_service_base_url")
        if not self.settings.embedding_service_api_key:
            missing.append("embedding_service_api_key")
        if not self.settings.embedding_service_model_name:
            missing.append("embedding_service_model_name")

        if missing:
            raise ValueError(f"缺少 Embedding 服务配置: {', '.join(missing)}")

    def _ensure_index(self) -> None:
        """
        确保索引存在，如果不存在则创建
        """
        try:
            exists = self.client.indices.exists(index=self.index)
        except Exception as exc:
            self.logger.error("检查索引失败: %s", exc)
            raise

        if exists:
            return

        self.logger.info("索引不存在，准备创建: %s", self.index)

        # 先获取 Embedding 维度
        sample_vector = self.embedding_service.embed_text("sample text")
        dims = len(sample_vector)

        mapping = {
            "mappings": {
                "properties": {
                    "paper_id": {"type": "keyword"},
                    "chunk_id": {"type": "keyword"},
                    "paper_title": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                    "paper_url": {"type": "keyword"},
                    "content": {"type": "text"},
                    "saved_at": {"type": "date"},
                    "embedding": {
                        "type": "dense_vector",
                        "dims": dims,
                        "index": True,
                        "similarity": "cosine",
                    },
                    "metadata": {"type": "object"},
                }
            }
        }

        try:
            self.client.indices.create(index=self.index, mappings=mapping["mappings"])
            self.logger.info("索引创建成功: %s", self.index)
        except Exception as exc:
            self.logger.error("创建索引失败: %s", exc)
            raise

    def ingest_document(
        self,
        paper_id: str,
        paper_title: str,
        paper_url: str,
        paper_text: str,
    ) -> None:
        """
        将论文内容写入 Elasticsearch 知识库
        """
        if not paper_text.strip():
            self.logger.warning("论文内容为空，跳过写入知识库: %s", paper_title)
            return

        chunks = self.text_splitter.split_text(paper_text)
        if not chunks:
            self.logger.warning("未生成内容片段，跳过写入: %s", paper_title)
            return

        self.logger.info("论文 [%s] 拆分为 %d 个片段，开始向量化...", paper_title, len(chunks))
        embeddings = self.embedding_service.embed_batch(chunks)

        timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

        for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings), start=1):
            doc_id = f"{paper_id}-{idx:04d}"
            document = {
                "paper_id": paper_id,
                "chunk_id": idx,
                "paper_title": paper_title,
                "paper_url": paper_url,
                "content": chunk,
                "saved_at": timestamp,
                "embedding": embedding,
                "metadata": {
                    "length": len(chunk),
                    "word_count": len(chunk.split()),
                },
            }

            try:
                self.client.index(index=self.index, id=doc_id, document=document)
            except Exception as exc:
                self.logger.error("写入文档失败 doc_id=%s: %s", doc_id, exc)
                raise

        self.logger.info("论文 [%s] 已写入知识库，共 %d 个片段", paper_title, len(chunks))

    def ingest_chunks(
        self,
        paper_id: str,
        paper_title: str,
        paper_url: str,
        chunks: list[str],
    ) -> None:
        """
        将已经切分好的片段写入 Elasticsearch（跳过内部再次切分）
        """
        if not chunks:
            self.logger.warning("空片段集合，跳过写入: %s", paper_title)
            return
        self.logger.info("接收外部片段 %d 个，开始向量化...", len(chunks))
        embeddings = self.embedding_service.embed_batch(chunks)
        timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings), start=1):
            doc_id = f"{paper_id}-{idx:04d}"
            document = {
                "paper_id": paper_id,
                "chunk_id": idx,
                "paper_title": paper_title,
                "paper_url": paper_url,
                "content": chunk,
                "saved_at": timestamp,
                "embedding": embedding,
                "metadata": {
                    "length": len(chunk),
                    "word_count": len(chunk.split()),
                },
            }
            try:
                self.client.index(index=self.index, id=doc_id, document=document)
            except Exception as exc:
                self.logger.error("写入文档失败 doc_id=%s: %s", doc_id, exc)
                raise
        self.logger.info("论文 [%s] 外部片段已写入知识库，共 %d 个片段", paper_title, len(chunks))

    def delete_paper(self, paper_id: str) -> None:
        """
        删除指定论文的所有文档
        """
        query = {"query": {"term": {"paper_id": paper_id}}}
        try:
            self.client.delete_by_query(index=self.index, body=query)
            self.logger.info("知识库中已删除论文: %s", paper_id)
        except NotFoundError:
            self.logger.warning("删除论文失败，索引不存在: %s", self.index)
        except Exception as exc:
            self.logger.error("删除论文失败: %s", exc)
            raise

    def search(
        self,
        query: str,
        top_k: int = 5,
        min_score: float = 0.0,
    ) -> List[dict]:
        """
        基于向量检索知识库内容
        """
        if not query.strip():
            return []

        query_vector = self.embedding_service.embed_text(query)
        knn = {
            "field": "embedding",
            "query_vector": query_vector,
            "k": top_k,
            "num_candidates": max(10, top_k * 4),
        }

        search_body = {
            "knn": knn,
            "size": top_k,
            "_source": {
                "includes": [
                    "paper_id",
                    "paper_title",
                    "paper_url",
                    "content",
                    "saved_at",
                    "metadata",
                ]
            },
        }

        try:
            response = self.client.search(index=self.index, body=search_body)
        except TypeError:
            # 兼容旧版 python 客户端需要 request body 名为 `body`
            response = self.client.search(index=self.index, body=search_body)
        except Exception as exc:
            self.logger.error("知识库检索失败: %s", exc)
            raise

        hits = response.get("hits", {}).get("hits", [])
        results = []
        for hit in hits:
            score = hit.get("_score", 0.0)
            if score < min_score:
                continue
            source = hit.get("_source", {})
            results.append(
                {
                    "score": score,
                    "paper_id": source.get("paper_id"),
                    "paper_title": source.get("paper_title"),
                    "paper_url": source.get("paper_url"),
                    "content": source.get("content"),
                    "saved_at": source.get("saved_at"),
                    "metadata": source.get("metadata", {}),
                }
            )

        return results

