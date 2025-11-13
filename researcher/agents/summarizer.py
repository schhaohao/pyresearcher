"""
摘要生成智能体
负责生成论文摘要和总结
"""
from typing import Dict, List

from langchain_core.messages import HumanMessage, SystemMessage

from researcher.config.settings import get_settings
from researcher.llm import LLMFactory
from researcher.prompts.analysis_prompts import SUMMARIZER_SYSTEM_PROMPT

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

class SummarizerAgent:
    """摘要生成智能体"""
    
    def __init__(self, llm=None):
        """
        初始化摘要智能体
        
        Args:
            llm: 语言模型实例
        """
        self.llm = llm or LLMFactory.create(
            provider=DEFAULT_PROVIDER,
            model=DEFAULT_MODEL,
            temperature=0.5,
            max_tokens=DEFAULT_MAX_TOKENS,
        )
        self.system_prompt = SUMMARIZER_SYSTEM_PROMPT
    
    def summarize(self, analysis: Dict) -> Dict:
        """
        生成论文摘要
        
        Args:
            analysis: 分析结果字典
            
        Returns:
            包含摘要的字典
        """
        content = f"""
标题: {analysis.get('title', '')}
分析: {analysis.get('analysis', '')}
关键点: {analysis.get('key_points', [])}
"""
        
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"请为以下论文生成摘要：\n{content}")
        ]
        
        response = self.llm.invoke(messages)
        
        return {
            **analysis,
            "summary": response.content,
        }
    
    def summarize_batch(self, analyses: List[Dict]) -> List[Dict]:
        """
        批量生成摘要
        
        Args:
            analyses: 分析结果列表
            
        Returns:
            包含摘要的结果列表
        """
        return [self.summarize(analysis) for analysis in analyses]

