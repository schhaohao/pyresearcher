"""
Anthropic (Claude) LLM Implementation
"""
from typing import List, Optional, Iterator
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage
from langchain_anthropic import ChatAnthropic
from researcher.llm.base import BaseLLM


class AnthropicLLM(BaseLLM):
    """Anthropic (Claude) LLM 实现"""
    
    def __init__(self, api_key: str, model: str = "claude-3-sonnet-20240229",
                 temperature: float = 0.7, max_tokens: Optional[int] = None, **kwargs):
        """
        初始化 Anthropic LLM
        
        Args:
            api_key: Anthropic API key
            model: 模型名称，如 claude-3-opus-20240229, claude-3-sonnet-20240229 等
            temperature: 采样温度
            max_tokens: 最大生成 token 数
            **kwargs: 其他参数
        """
        super().__init__(api_key, model, temperature, max_tokens, **kwargs)
        self._client = ChatAnthropic(
            api_key=api_key,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens or 4096,
            **kwargs
        )
    
    def invoke(self, messages: List[BaseMessage], **kwargs) -> AIMessage:
        """调用 LLM（LangChain 兼容接口）"""
        return self._client.invoke(messages, **kwargs)
    
    def generate(self, prompt: str, **kwargs) -> str:
        """生成文本"""
        messages = [HumanMessage(content=prompt)]
        response = self.invoke(messages, **kwargs)
        return response.content
    
    def stream_generate(self, prompt: str, **kwargs) -> Iterator[str]:
        """流式生成文本"""
        messages = [HumanMessage(content=prompt)]
        for chunk in self._client.stream(messages, **kwargs):
            if hasattr(chunk, 'content'):
                yield chunk.content
            else:
                yield str(chunk)

