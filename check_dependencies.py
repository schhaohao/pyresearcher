"""
检查依赖是否已安装
"""
import sys

def check_dependency(module_name, package_name=None):
    """检查单个依赖"""
    if package_name is None:
        package_name = module_name
    
    try:
        __import__(module_name)
        print(f"✅ {package_name}")
        return True
    except ImportError:
        print(f"❌ {package_name} (未安装)")
        return False

def main():
    """主函数"""
    print("检查依赖包...\n")
    
    dependencies = [
        ("langchain", "langchain"),
        ("langchain_core", "langchain-core"),
        ("langchain_openai", "langchain-openai"),
        ("langchain_anthropic", "langchain-anthropic"),
        ("langchain_elasticsearch", "langchain-elasticsearch"),
        ("elasticsearch", "elasticsearch"),
        ("arxiv", "arxiv"),
        ("pypdf", "pypdf"),
        ("dotenv", "python-dotenv"),
        ("pydantic", "pydantic"),
    ]
    
    results = []
    for module, package in dependencies:
        results.append(check_dependency(module, package))
    
    print("\n" + "="*50)
    if all(results):
        print("✅ 所有依赖已安装！")
        print("\n可以运行测试：")
        print("  python tests/test_llm_standalone.py")
        return 0
    else:
        print("❌ 部分依赖未安装")
        print("\n请先安装依赖：")
        print("  pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())

