"""
LLM Base Class

This module defines the abstract base class for all LLM providers.
所有 LLM 实现都应该兼容 LangChain 的接口（invoke 方法）
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Iterator, List, Union
from langchain_core.messages import BaseMessage, AIMessage


class BaseLLM(ABC):
    """
    Abstract base class for LLM providers.

    All LLM implementations (OpenAI, Anthropic, DeepSeek, SiliconFlow) should 
    inherit from this class and implement the required abstract methods.
    
    所有实现都应该兼容 LangChain 的接口，特别是 invoke 方法。
    """

    def __init__(
        self,
        api_key: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
        ):
        """
        Initialize the LLM.

        Args:
            api_key: API key for the LLM provider
            model: Model name/identifier
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional configuration parameters
        """
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.config = kwargs

    @abstractmethod
    def invoke(self, messages: List[BaseMessage], **kwargs) -> AIMessage:
        """
        Invoke the LLM with a list of messages (LangChain compatible).
        
        Args:
            messages: List of message objects (SystemMessage, HumanMessage, etc.)
            **kwargs: Additional generation parameters
            
        Returns:
            AIMessage object with the response content
        """
        pass

    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate text from a prompt.

        Args:
            prompt: The input prompt
            **kwargs: Additional generation parameters (temperature, max_tokens, etc.)

        Returns:
            Generated text response
        """
        pass

    @abstractmethod
    def stream_generate(self, prompt: str, **kwargs) -> Iterator[str]:
        """
        Stream generate text from a prompt.

        Args:
            prompt: The input prompt
            **kwargs: Additional generation parameters

        Yields:
            Text chunks as they are generated
        """
        pass

    def __repr__(self) -> str:
        """String representation of the LLM instance."""
        return f"{self.__class__.__name__}(model={self.model})"