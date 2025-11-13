# LLM 模块说明

本模块提供了统一的多厂商 LLM 接口，支持以下提供商：

- **OpenAI**: GPT-4, GPT-3.5-turbo 等
- **Anthropic**: Claude 3 系列模型
- **DeepSeek**: DeepSeek Chat, DeepSeek Coder 等
- **SiliconFlow**: 各种开源模型（如 Llama, Qwen 等）

## 快速开始

### 1. 基本使用

```python
from researcher.llm import LLMFactory
from langchain_core.messages import SystemMessage, HumanMessage

# 使用默认配置创建 LLM（从 .env 文件读取）
llm = LLMFactory.create()

# 使用 LLM
messages = [
    SystemMessage(content="你是一个有用的助手。"),
    HumanMessage(content="你好！")
]
response = llm.invoke(messages)
print(response.content)
```

### 2. 指定提供商

```python
from researcher.llm import LLMFactory, LLMProvider

# 使用 OpenAI
llm = LLMFactory.create(provider=LLMProvider.OPENAI)

# 使用 Anthropic
llm = LLMFactory.create(provider=LLMProvider.ANTHROPIC)

# 使用 DeepSeek
llm = LLMFactory.create(provider=LLMProvider.DEEPSEEK)

# 使用 SiliconFlow
llm = LLMFactory.create(provider=LLMProvider.SILICONFLOW)
```

### 3. 自定义配置

```python
llm = LLMFactory.create(
    provider=LLMProvider.OPENAI,
    model="gpt-3.5-turbo",
    temperature=0.5,
    max_tokens=1000,
)
```

### 4. 直接使用 API Key

```python
llm = LLMFactory.create(
    provider=LLMProvider.OPENAI,
    api_key="your-api-key",
    model="gpt-4",
)
```

## 配置

在 `.env` 文件中配置 API keys：

```env
# OpenAI
OPENAI_API_KEY=your_openai_api_key

# Anthropic
ANTHROPIC_API_KEY=your_anthropic_api_key

# DeepSeek
DEEPSEEK_API_KEY=your_deepseek_api_key

# SiliconFlow
SILICONFLOW_API_KEY=your_siliconflow_api_key

# 默认提供商
DEFAULT_PROVIDER=openai
```

## 架构设计

### BaseLLM

所有 LLM 实现都继承自 `BaseLLM` 抽象基类，必须实现以下方法：

- `invoke(messages, **kwargs)`: 调用 LLM（LangChain 兼容接口）
- `generate(prompt, **kwargs)`: 生成文本
- `stream_generate(prompt, **kwargs)`: 流式生成文本

### LLMFactory

`LLMFactory` 提供了统一的创建接口，支持：

- 自动从配置读取 API keys
- 支持指定提供商或使用默认提供商
- 支持自定义模型、温度等参数
- 自动处理错误和验证

## 扩展新的提供商

要添加新的 LLM 提供商：

1. 在 `researcher/llm/` 目录下创建新的实现文件
2. 继承 `BaseLLM` 并实现所有抽象方法
3. 在 `factory.py` 中注册新的提供商

示例：

```python
# researcher/llm/new_provider_llm.py
from researcher.llm.base import BaseLLM

class NewProviderLLM(BaseLLM):
    def __init__(self, api_key: str, model: str, **kwargs):
        super().__init__(api_key, model, **kwargs)
        # 初始化客户端
    
    def invoke(self, messages, **kwargs):
        # 实现 invoke 方法
        pass
    
    def generate(self, prompt, **kwargs):
        # 实现 generate 方法
        pass
    
    def stream_generate(self, prompt, **kwargs):
        # 实现 stream_generate 方法
        pass
```

然后在 `factory.py` 中注册：

```python
_PROVIDER_MAP = {
    # ... 现有提供商
    LLMProvider.NEW_PROVIDER: NewProviderLLM,
}
```

## 注意事项

1. 所有 LLM 实现都兼容 LangChain 的接口，可以直接替换现有的 `ChatOpenAI` 等实例
2. API keys 应该通过环境变量配置，不要硬编码在代码中
3. 不同提供商的模型名称和参数可能不同，请参考各提供商的文档

