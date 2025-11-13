"""
知识库模块
"""

# from functools import lru_cache
# from typing import Optional

# from researcher.config.settings import Settings, get_settings
# from researcher.knowledge_base.elasticsearch_store import ElasticsearchKnowledgeBase


# @lru_cache(maxsize=1)
# def get_elasticsearch_knowledge_base(settings: Optional[Settings] = None) -> ElasticsearchKnowledgeBase:
#     """
#     获取 Elasticsearch 知识库实例（单例）
#     """
#     settings = settings or get_settings()
#     return ElasticsearchKnowledgeBase(settings=settings)


from functools import lru_cache

from researcher.config.settings import get_settings
from researcher.knowledge_base.elasticsearch_store import ElasticsearchKnowledgeBase

@lru_cache(maxsize=1)
def get_elasticsearch_knowledge_base() -> ElasticsearchKnowledgeBase:
    settings = get_settings()
    return ElasticsearchKnowledgeBase(settings=settings)


__all__ = ["get_elasticsearch_knowledge_base", "ElasticsearchKnowledgeBase"]

