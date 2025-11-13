"""
报告撰写智能体
负责生成综述报告
"""
from typing import Dict, List

from langchain_core.messages import HumanMessage, SystemMessage

from researcher.config.settings import get_settings
from researcher.llm import LLMFactory
from researcher.prompts.writing_prompts import WRITER_SYSTEM_PROMPT

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


class WriterAgent:
    """报告撰写智能体"""
    
    def __init__(self, llm=None):
        """
        初始化撰写智能体
        
        Args:
            llm: 语言模型实例
        """
        self.llm = llm or LLMFactory.create(
            provider=DEFAULT_PROVIDER,
            model=DEFAULT_MODEL,
            temperature=0.7,
            max_tokens=DEFAULT_MAX_TOKENS,
        )
        self.system_prompt = WRITER_SYSTEM_PROMPT
    
    def write_report(self, topic: str, summaries: List[Dict]) -> str:
        """
        生成综述报告
        
        Args:
            topic: 调研主题
            summaries: 包含摘要的论文列表
            
        Returns:
            生成的报告文本
        """
        # 整理论文信息
        papers_info = []
        for summary in summaries:
            papers_info.append({
                "title": summary.get("title", ""),
                "summary": summary.get("summary", ""),
                "key_points": summary.get("key_points", []),
                "contributions": summary.get("contributions", []),
            })
        
        content = f"""
调研主题: {topic}

论文列表:
{self._format_papers_info(papers_info)}
"""
        
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"请基于以下信息生成综述报告：\n{content}")
        ]
        
        response = self.llm.invoke(messages)
        return response.content
    
    def _format_papers_info(self, papers_info: List[Dict]) -> str:
        """格式化论文信息"""
        formatted = []
        for i, paper in enumerate(papers_info, 1):
            formatted.append(f"\n## 论文 {i}: {paper['title']}")
            formatted.append(f"\n摘要: {paper['summary']}")
            if paper.get('key_points'):
                formatted.append(f"\n关键点:")
                for point in paper['key_points']:
                    formatted.append(f"- {point}")
            if paper.get('contributions'):
                formatted.append(f"\n贡献:")
                for contrib in paper['contributions']:
                    formatted.append(f"- {contrib}")
            formatted.append("\n" + "-" * 50)
        
        return "\n".join(formatted)

