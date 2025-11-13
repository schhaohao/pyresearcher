"""
LLM 模型可用性测试
测试所有配置的 LLM 提供商是否可用
"""
import os
import sys
from typing import Dict, Optional

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from researcher.llm import LLMFactory, LLMProvider
from researcher.config.settings import get_settings
from langchain_core.messages import SystemMessage, HumanMessage


class LLMTester:
    """LLM 测试类"""
    
    def __init__(self):
        self.settings = get_settings()
        self.results: Dict[str, Dict] = {}
    
    def test_provider(self, provider: LLMProvider) -> Dict:
        """
        测试单个提供商
        
        Args:
            provider: LLM 提供商
            
        Returns:
            测试结果字典
        """
        result = {
            "provider": provider.value,
            "status": "unknown",
            "error": None,
            "response": None,
            "api_key_configured": False,
        }
        
        print(f"\n{'='*60}")
        print(f"测试 {provider.value.upper()}...")
        print(f"{'='*60}")
        
        # 检查 API key 是否配置
        api_key = self._get_api_key(provider)
        if not api_key:
            result["status"] = "skipped"
            result["error"] = "API key 未配置"
            print(f"❌ API key 未配置，跳过测试")
            return result
        
        result["api_key_configured"] = True
        print(f"✅ API key 已配置")
        
        try:
            # 创建 LLM 实例
            print(f"正在创建 LLM 实例...")
            llm = LLMFactory.create(provider=provider)
            print(f"✅ LLM 实例创建成功: {llm}")
            
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
            print(f"响应: {response.content[:200]}...")
            
        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            print(f"❌ 测试失败: {e}")
        
        return result
    
    def _get_api_key(self, provider: LLMProvider) -> Optional[str]:
        """获取指定提供商的 API key"""
        key_map = {
            LLMProvider.OPENAI: "openai_api_key",
            LLMProvider.ANTHROPIC: "anthropic_api_key",
            LLMProvider.DEEPSEEK: "deepseek_api_key",
            LLMProvider.SILICONFLOW: "siliconflow_api_key",
        }
        key_name = key_map.get(provider)
        if key_name:
            return getattr(self.settings, key_name, None)
        return None
    
    def test_all(self) -> Dict[str, Dict]:
        """测试所有提供商"""
        print("\n" + "="*60)
        print("开始测试所有 LLM 提供商")
        print("="*60)
        
        providers = [
            LLMProvider.OPENAI,
            LLMProvider.ANTHROPIC,
            LLMProvider.DEEPSEEK,
            LLMProvider.SILICONFLOW,
        ]
        
        for provider in providers:
            result = self.test_provider(provider)
            self.results[provider.value] = result
        
        return self.results
    
    def print_summary(self):
        """打印测试总结"""
        print("\n" + "="*60)
        print("测试总结")
        print("="*60)
        
        total = len(self.results)
        success = sum(1 for r in self.results.values() if r["status"] == "success")
        failed = sum(1 for r in self.results.values() if r["status"] == "failed")
        skipped = sum(1 for r in self.results.values() if r["status"] == "skipped")
        
        print(f"\n总计: {total} 个提供商")
        print(f"✅ 成功: {success}")
        print(f"❌ 失败: {failed}")
        print(f"⏭️  跳过: {skipped}")
        
        print("\n详细结果:")
        for provider, result in self.results.items():
            status_icon = {
                "success": "✅",
                "failed": "❌",
                "skipped": "⏭️ ",
            }.get(result["status"], "❓")
            
            print(f"\n{status_icon} {provider.upper()}")
            print(f"   状态: {result['status']}")
            if result["api_key_configured"]:
                print(f"   API Key: 已配置")
            else:
                print(f"   API Key: 未配置")
            
            if result["error"]:
                print(f"   错误: {result['error']}")
            
            if result["response"]:
                print(f"   响应预览: {result['response'][:100]}...")


def main():
    """主函数"""
    tester = LLMTester()
    
    # 测试所有提供商
    results = tester.test_all()
    
    # 打印总结
    tester.print_summary()
    
    # 返回退出码
    success_count = sum(1 for r in results.values() if r["status"] == "success")
    if success_count > 0:
        print(f"\n✅ 至少有一个提供商可用！")
        return 0
    else:
        print(f"\n❌ 没有可用的提供商，请检查配置。")
        return 1


if __name__ == "__main__":
    sys.exit(main())

