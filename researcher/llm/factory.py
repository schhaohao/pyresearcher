"""
LLM Factory
LLM 工厂类，用于创建不同厂商的 LLM 实例
"""
from typing import Optional, Dict, Any, Union
from enum import Enum

from researcher.llm.base import BaseLLM
from researcher.llm.openai_llm import OpenAILLM
from researcher.llm.anthropic_llm import AnthropicLLM
from researcher.llm.deepseek_llm import DeepSeekLLM
from researcher.llm.siliconflow_llm import SiliconFlowLLM
from researcher.config.settings import get_settings


class LLMProvider(str, Enum):
    """LLM 提供商枚举"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    DEEPSEEK = "deepseek"
    SILICONFLOW = "siliconflow"


class LLMFactory:
    """LLM 工厂类"""
    
    # 提供商到实现类的映射
    _PROVIDER_MAP = {
        LLMProvider.OPENAI: OpenAILLM,
        LLMProvider.ANTHROPIC: AnthropicLLM,
        LLMProvider.DEEPSEEK: DeepSeekLLM,
        LLMProvider.SILICONFLOW: SiliconFlowLLM,
    }
    
    @classmethod
    def create(
        cls,
        provider: Optional[Union[str, LLMProvider]] = None,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> BaseLLM:
        """
        创建 LLM 实例
        
        Args:
            provider: 提供商名称（openai, anthropic, deepseek, siliconflow）
                     如果为 None，则从配置中读取
            model: 模型名称，如果为 None，则使用默认模型
            api_key: API key，如果为 None，则从配置中读取
            temperature: 采样温度，如果为 None，则使用默认值
            max_tokens: 最大 token 数，如果为 None，则使用默认值
            **kwargs: 其他参数
            
        Returns:
            LLM 实例
            
        Raises:
            ValueError: 如果提供商不支持或缺少必要的配置
        """
        settings = get_settings()
        
        # 确定提供商
        if provider is None:
            provider = getattr(settings, 'default_provider', LLMProvider.OPENAI)
        
        if isinstance(provider, str):
            provider = LLMProvider(provider.lower())
        
        if provider not in cls._PROVIDER_MAP:
            supported = [p.value for p in cls._PROVIDER_MAP.keys()]
            raise ValueError(
                f"不支持的 LLM 提供商: {provider.value if hasattr(provider, 'value') else provider}. "
                f"支持的提供商: {', '.join(supported)}"
            )
        
        # 获取 API key
        if api_key is None:
            api_key = cls._get_api_key(provider, settings)
            if not api_key:
                raise ValueError(
                    f"未找到 {provider.value} 的 API key。"
                    f"请在 .env 文件中设置相应的环境变量。"
                )
        
        # 获取模型名称
        if model is None:
            model = cls._get_default_model(provider, settings)
        
        # 获取其他参数
        if temperature is None:
            temperature = settings.temperature
        if max_tokens is None:
            max_tokens = settings.max_tokens
        
        # 创建实例
        llm_class = cls._PROVIDER_MAP[provider]
        return llm_class(
            api_key=api_key,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
    
    @classmethod
    def _get_api_key(cls, provider: LLMProvider, settings) -> Optional[str]:
        """获取指定提供商的 API key"""
        key_map = {
            LLMProvider.OPENAI: "openai_api_key",
            LLMProvider.ANTHROPIC: "anthropic_api_key",
            LLMProvider.DEEPSEEK: "deepseek_api_key",
            LLMProvider.SILICONFLOW: "siliconflow_api_key",
        }
        key_name = key_map.get(provider)
        if key_name:
            return getattr(settings, key_name, None)
        return None
    
    @classmethod
    def _get_default_model(cls, provider: LLMProvider, settings) -> str:
        """获取指定提供商的默认模型"""
        model_map = {
            LLMProvider.OPENAI: getattr(settings, 'openai_model', 'gpt-4'),
            LLMProvider.ANTHROPIC: getattr(settings, 'anthropic_model', 'claude-3-sonnet-20240229'),
            LLMProvider.DEEPSEEK: getattr(settings, 'deepseek_model', 'deepseek-chat'),
            LLMProvider.SILICONFLOW: getattr(settings, 'siliconflow_model', 'deepseek-ai/DeepSeek-V3.2-Exp'),
        }
        return model_map.get(provider, 'gpt-4')
    
    @classmethod
    def list_providers(cls) -> list:
        """列出所有支持的提供商"""
        return list(cls._PROVIDER_MAP.keys())

