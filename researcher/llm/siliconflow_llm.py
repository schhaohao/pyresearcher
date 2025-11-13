"""
SiliconFlow LLM Implementation
SiliconFlow 使用 OpenAI 兼容的 API
"""
from typing import List, Optional, Iterator
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
from researcher.llm.base import BaseLLM


class SiliconFlowLLM(BaseLLM):
    """SiliconFlow LLM 实现（使用 OpenAI 兼容 API）"""
    
    def __init__(
        self,
        api_key: str,
        model: str = "deepseek-ai/DeepSeek-V3.2-Exp",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None, 
        base_url: Optional[str] = None,
        **kwargs
        ):
        """
        初始化 SiliconFlow LLM
        
        Args:
            api_key: SiliconFlow API key
            model: 模型名称，如 deepseek-ai/DeepSeek-V3.2-Exp, Qwen/QwQ-32B 等
            temperature: 采样温度
            max_tokens: 最大生成 token 数
            base_url: API base URL，默认为 https://api.siliconflow.cn/v1
                     注意：LangChain 会自动添加 /chat/completions 路径
            **kwargs: 其他参数
        """
        super().__init__(api_key, model, temperature, max_tokens, **kwargs)
        # SiliconFlow 使用 OpenAI 兼容的 API
        # base_url 应该是基础 URL，LangChain 会自动添加 /chat/completions
        self._client = ChatOpenAI(
            api_key=api_key,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            base_url=base_url or "https://api.siliconflow.cn/v1",
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

