"""
LLM 使用示例
展示如何使用多厂商 LLM
"""
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from researcher.llm import LLMFactory, LLMProvider
from langchain_core.messages import SystemMessage, HumanMessage


def example_basic_usage():
    """基本使用示例：使用默认配置创建 LLM"""
    print("=" * 50)
    print("示例 1: 使用默认配置创建 LLM")
    print("=" * 50)
    
    # 使用默认配置（从 .env 文件读取）
    llm = LLMFactory.create()
    print(f"创建的 LLM: {llm}")
    
    # 使用 LLM
    messages = [
        SystemMessage(content="你是一个有用的助手。"),
        HumanMessage(content="请用一句话介绍你自己。")
    ]
    
    try:
        response = llm.invoke(messages)
        print(f"响应: {response.content}\n")
    except Exception as e:
        print(f"错误: {e}\n")


def example_specific_provider():
    """指定提供商示例"""
    print("=" * 50)
    print("示例 2: 指定提供商创建 LLM")
    print("=" * 50)
    
    providers = [
        LLMProvider.OPENAI,
        LLMProvider.ANTHROPIC,
        LLMProvider.DEEPSEEK,
        LLMProvider.SILICONFLOW,
    ]
    
    for provider in providers:
        try:
            print(f"\n尝试创建 {provider.value} LLM...")
            llm = LLMFactory.create(provider=provider)
            print(f"成功创建: {llm}")
        except Exception as e:
            print(f"创建失败: {e}")


def example_custom_config():
    """自定义配置示例"""
    print("=" * 50)
    print("示例 3: 使用自定义配置创建 LLM")
    print("=" * 50)
    
    try:
        # 使用自定义配置
        llm = LLMFactory.create(
            provider=LLMProvider.OPENAI,
            model="gpt-3.5-turbo",  # 使用更便宜的模型
            temperature=0.5,  # 降低随机性
            max_tokens=1000,  # 限制输出长度
        )
        print(f"创建的 LLM: {llm}")
        print(f"模型: {llm.model}")
        print(f"温度: {llm.temperature}")
        print(f"最大 tokens: {llm.max_tokens}\n")
    except Exception as e:
        print(f"错误: {e}\n")


def example_direct_api_key():
    """直接使用 API key 示例"""
    print("=" * 50)
    print("示例 4: 直接使用 API key 创建 LLM")
    print("=" * 50)
    
    # 注意：实际使用时应该从环境变量读取，不要硬编码
    api_key = os.getenv("OPENAI_API_KEY")
    
    if api_key:
        try:
            llm = LLMFactory.create(
                provider=LLMProvider.OPENAI,
                api_key=api_key,
                model="gpt-4",
            )
            print(f"成功创建 LLM: {llm}\n")
        except Exception as e:
            print(f"错误: {e}\n")
    else:
        print("未找到 OPENAI_API_KEY，跳过此示例\n")


def example_list_providers():
    """列出所有支持的提供商"""
    print("=" * 50)
    print("示例 5: 列出所有支持的提供商")
    print("=" * 50)
    
    providers = LLMFactory.list_providers()
    print("支持的 LLM 提供商:")
    for provider in providers:
        print(f"  - {provider.value}")
    print()


def main():
    """主函数"""
    print("\n" + "=" * 50)
    print("多厂商 LLM 使用示例")
    print("=" * 50 + "\n")
    
    # 运行示例
    example_list_providers()
    example_basic_usage()
    example_specific_provider()
    example_custom_config()
    example_direct_api_key()
    
    print("=" * 50)
    print("示例运行完成")
    print("=" * 50)


if __name__ == "__main__":
    main()

