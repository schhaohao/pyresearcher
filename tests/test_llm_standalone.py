"""
独立的 LLM 测试脚本
不依赖其他模块，只测试 LLM 功能
"""
import os
import sys
from typing import Dict, Optional

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 只导入 LLM 相关模块
from researcher.llm import LLMFactory, LLMProvider
from researcher.config.settings import get_settings
from langchain_core.messages import SystemMessage, HumanMessage


def check_api_keys():
    """检查已配置的 API keys"""
    settings = get_settings()
    providers = {
        "openai": settings.openai_api_key,
        "anthropic": settings.anthropic_api_key,
        "deepseek": settings.deepseek_api_key,
        "siliconflow": settings.siliconflow_api_key,
    }
    
    configured = {k: bool(v) for k, v in providers.items()}
    return configured


def test_provider(provider_name: str) -> Dict:
    """测试单个提供商"""
    result = {
        "provider": provider_name,
        "status": "unknown",
        "error": None,
        "response": None,
        "api_key_configured": False,
    }
    
    print(f"\n{'='*60}")
    print(f"测试 {provider_name.upper()}...")
    print(f"{'='*60}")
    
    try:
        # 检查 API key
        settings = get_settings()
        api_key_map = {
            "openai": settings.openai_api_key,
            "anthropic": settings.anthropic_api_key,
            "deepseek": settings.deepseek_api_key,
            "siliconflow": settings.siliconflow_api_key,
        }
        
        api_key = api_key_map.get(provider_name)
        if not api_key:
            result["status"] = "skipped"
            result["error"] = "API key 未配置"
            print(f"⏭️  API key 未配置，跳过测试")
            return result
        
        result["api_key_configured"] = True
        print(f"✅ API key 已配置")
        
        # 创建 LLM
        print(f"正在创建 LLM 实例...")
        provider_enum = LLMProvider(provider_name.lower())
        llm = LLMFactory.create(provider=provider_enum)
        print(f"✅ LLM 实例创建成功")
        print(f"   模型: {llm.model}")
        print(f"   温度: {llm.temperature}")
        
        # 发送测试消息
        print(f"正在发送测试消息...")
        messages = [
            SystemMessage(content="你是一个有用的助手。请用一句话介绍你自己。"),
            HumanMessage(content="你好！")
        ]
        
        response = llm.invoke(messages)
        result["response"] = response.content
        result["status"] = "success"
        
        print(f"✅ 测试成功！")
        print(f"\n响应:\n{response.content}\n")
        
    except ValueError as e:
        result["status"] = "failed"
        result["error"] = str(e)
        print(f"❌ 配置错误: {e}")
    except Exception as e:
        result["status"] = "failed"
        result["error"] = str(e)
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    return result


def main():
    """主函数"""
    print("\n" + "="*60)
    print("LLM 模型可用性测试")
    print("="*60)
    
    # 检查 API keys
    print("\n检查 API key 配置...")
    configured = check_api_keys()
    for provider, has_key in configured.items():
        status = "✅ 已配置" if has_key else "❌ 未配置"
        print(f"  {provider.upper()}: {status}")
    
    # 测试所有提供商
    results = {}
    providers = ["openai", "anthropic", "deepseek", "siliconflow"]
    
    for provider in providers:
        if configured.get(provider):
            result = test_provider(provider)
            results[provider] = result
        else:
            print(f"\n⏭️  跳过 {provider.upper()} (API key 未配置)")
            results[provider] = {
                "provider": provider,
                "status": "skipped",
                "error": "API key 未配置",
                "api_key_configured": False,
            }
    
    # 打印总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    
    total = len(results)
    success = sum(1 for r in results.values() if r["status"] == "success")
    failed = sum(1 for r in results.values() if r["status"] == "failed")
    skipped = sum(1 for r in results.values() if r["status"] == "skipped")
    
    print(f"\n总计: {total} 个提供商")
    print(f"✅ 成功: {success}")
    print(f"❌ 失败: {failed}")
    print(f"⏭️  跳过: {skipped}")
    
    if success > 0:
        print(f"\n✅ 至少有一个提供商可用！")
        return 0
    else:
        print(f"\n❌ 没有可用的提供商，请检查配置。")
        return 1


if __name__ == "__main__":
    sys.exit(main())

