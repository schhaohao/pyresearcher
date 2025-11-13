"""
文献搜索工具
"""
import arxiv
from typing import List, Dict
import requests
from bs4 import BeautifulSoup
import random
import time

def search_arxiv(query: str, max_results: int = 5, max_retries: int = 3) -> List[Dict]:
    client = arxiv.Client()
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance
    )
    
    papers = []
    for attempt in range(max_retries):
        try:
            for result in client.results(search):
                arxiv_id = result.entry_id.split("/")[-1]
                pdf_url = getattr(result, "pdf_url", None) or f"https://arxiv.org/pdf/{arxiv_id}.pdf"
                papers.append({
                    "id": arxiv_id,
                    "title": result.title,
                    "authors": [author.name for author in result.authors],
                    "abstract": result.summary,
                    "url": result.entry_id,
                    "pdf_url": pdf_url,
                    "published": result.published.isoformat() if result.published else None,
                    "source": "arxiv",
                })
            break  # 成功则退出重试
        except arxiv.HTTPError as e:
            # arxiv.HTTPError 的状态码在 e.args[2]
            status = e.args[2] if len(e.args) > 2 else None
            if status == 429:
                wait = random.uniform(3, 6)  # 随机等待
                print(f"429 Too Many Requests, 等待 {wait:.1f}s 后重试...")
                time.sleep(wait)
            else:
                raise
    return papers[:max_results]


# def search_arxiv(query: str, max_results: int = 5) -> List[Dict]:
#     """
#     在 arXiv 上搜索论文
    
#     Args:
#         query: 搜索查询
#         max_results: 最大结果数
        
#     Returns:
#         论文列表
#     """
#     client = arxiv.Client()
#     search = arxiv.Search(
#         query=query,
#         max_results=max_results,
#         sort_by=arxiv.SortCriterion.Relevance
#     )
    
#     papers = []
#     for result in client.results(search):
#         arxiv_id = result.entry_id.split("/")[-1]
#         pdf_url = None
#         try:
#             # arxiv 库通常提供 .pdf_url 属性；若无则手动构造
#             pdf_url = getattr(result, "pdf_url", None) or f"https://arxiv.org/pdf/{arxiv_id}.pdf"
#         except Exception:
#             pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
#         papers.append({
#             "id": arxiv_id,
#             "title": result.title,
#             "authors": [author.name for author in result.authors],
#             "abstract": result.summary,
#             "url": result.entry_id,
#             "pdf_url": pdf_url,
#             "published": result.published.isoformat() if result.published else None,
#             "source": "arxiv",
#         })
    
#     return papers


def search_papers(query: str, max_results: int = 10) -> List[Dict]:
    """
    通用论文搜索（可以扩展支持其他数据库）
    
    Args:
        query: 搜索查询
        max_results: 最大结果数
        
    Returns:
        论文列表
    """
    # 这里可以扩展支持其他数据库，如 Google Scholar, Semantic Scholar 等
    # 目前先返回空列表，后续可以添加
    papers = []
    
    # 示例：可以添加 Semantic Scholar API 调用
    # papers.extend(search_semantic_scholar(query, max_results))
    
    return papers

