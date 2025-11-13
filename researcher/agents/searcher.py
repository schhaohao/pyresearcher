"""
文献搜索智能体
负责搜索和收集相关文献
"""
from typing import Dict, List

from langchain_core.messages import HumanMessage, SystemMessage

from researcher.config.settings import get_settings
from researcher.llm import LLMFactory
from researcher.prompts.search_prompts import SEARCHER_SYSTEM_PROMPT
from researcher.tools.search_tools import search_arxiv, search_papers

settings = get_settings()
DEFAULT_PROVIDER = settings.default_provider
PROVIDER_MODEL_MAP = {
    "openai": settings.openai_model,
    "anthropic": settings.anthropic_model,
    "deepseek": settings.deepseek_model,
    "siliconflow": settings.siliconflow_model,
}
DEFAULT_MODEL = PROVIDER_MODEL_MAP.get(DEFAULT_PROVIDER, settings.default_model)
DEFAULT_MAX_TOKENS = settings.max_tokens

class SearcherAgent:
    """文献搜索智能体"""
    
    def __init__(self, llm=None):
        """
        初始化搜索智能体
        
        Args:
            llm: 语言模型实例，如果为 None 则使用默认的 OpenAI 模型
        """
        self.llm = llm or LLMFactory.create(
            provider=DEFAULT_PROVIDER,
            model=DEFAULT_MODEL,
            temperature=0.7,
            max_tokens=DEFAULT_MAX_TOKENS,
        )
        self.system_prompt = SEARCHER_SYSTEM_PROMPT
    
    def search(self, topic: str, max_papers: int = 10) -> List[Dict]:
        """
        搜索相关文献
        
        Args:
            topic: 搜索主题
            max_papers: 最大论文数量
            
        Returns:
            论文列表，每个论文包含 title, authors, abstract, url 等信息
        """
        # 使用 LLM 优化搜索关键词
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"请为以下主题生成搜索关键词：{topic}")
        ]
        response = self.llm.invoke(messages)
        keywords = response.content
        
        # 执行搜索
        papers = search_arxiv(keywords, max_results=max_papers)
        
        # 如果 arxiv 结果不足，可以使用其他搜索工具
        if len(papers) < max_papers:
            additional_papers = search_papers(keywords, max_results=max_papers - len(papers))
            papers.extend(additional_papers)
        
        return papers[:max_papers]

