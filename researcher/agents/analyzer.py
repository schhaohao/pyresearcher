"""
内容分析智能体
负责分析论文内容，提取关键信息
"""
from typing import Dict, List

from langchain_core.messages import HumanMessage, SystemMessage

from researcher.config.settings import get_settings
from researcher.llm import LLMFactory
from researcher.prompts.analysis_prompts import ANALYZER_SYSTEM_PROMPT

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

class AnalyzerAgent:
    """内容分析智能体"""
    
    def __init__(self, llm=None):
        """
        初始化分析智能体
        
        Args:
            llm: 语言模型实例
        """
        self.llm = llm or LLMFactory.create(
            provider=DEFAULT_PROVIDER,
            model=DEFAULT_MODEL,
            temperature=0.3,
            max_tokens=DEFAULT_MAX_TOKENS,
        )
        self.system_prompt = ANALYZER_SYSTEM_PROMPT
    
    def analyze(self, paper: Dict) -> Dict:
        """
        分析单篇论文
        
        Args:
            paper: 论文信息字典，包含 title, abstract, content 等
            
        Returns:
            分析结果，包含关键点、方法、贡献等
        """
        content = f"""
标题: {paper.get('title', '')}
摘要: {paper.get('abstract', '')}
内容: {paper.get('content', '')[:2000]}  # 限制长度
"""
        
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"请分析以下论文：\n{content}")
        ]
        
        response = self.llm.invoke(messages)
        
        return {
            "paper_id": paper.get("id", ""),
            "title": paper.get("title", ""),
            "analysis": response.content,
            "key_points": self._extract_key_points(response.content),
            "methodology": self._extract_methodology(response.content),
            "contributions": self._extract_contributions(response.content),
        }
    
    def analyze_batch(self, papers: List[Dict]) -> List[Dict]:
        """
        批量分析论文
        
        Args:
            papers: 论文列表
            
        Returns:
            分析结果列表
        """
        return [self.analyze(paper) for paper in papers]
    
    def _extract_key_points(self, analysis: str) -> List[str]:
        """从分析文本中提取关键点"""
        # 简单实现，可以后续优化
        lines = analysis.split("\n")
        key_points = [line.strip() for line in lines if line.strip().startswith("-") or line.strip().startswith("•")]
        return key_points[:5]  # 返回前5个关键点
    
    def _extract_methodology(self, analysis: str) -> str:
        """提取方法论"""
        # 简单实现，可以后续优化
        if "方法" in analysis or "methodology" in analysis.lower():
            # 提取方法相关段落
            return analysis
        return ""
    
    def _extract_contributions(self, analysis: str) -> List[str]:
        """提取贡献点"""
        # 简单实现，可以后续优化
        if "贡献" in analysis or "contribution" in analysis.lower():
            lines = analysis.split("\n")
            contributions = [line.strip() for line in lines if "贡献" in line or "contribution" in line.lower()]
            return contributions
        return []

