"""
单个 LLM 模型快速测试
用于快速测试指定的 LLM 提供商
"""
import os
import sys
import argparse

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from researcher.llm import LLMFactory, LLMProvider
from researcher.config.settings import get_settings
from researcher.knowledge_base import get_elasticsearch_knowledge_base
from langchain_core.messages import SystemMessage, HumanMessage


def _retrieve_context(
    query: str,
    top_k: int,
    min_score: float,
):
    """
    从 Elasticsearch 知识库检索相关上下文
    """
    settings = get_settings()
    if not settings.es_enabled:
        print("⚠️  未启用 Elasticsearch 知识库，跳过检索。")
        return []

    kb = get_elasticsearch_knowledge_base()
    results = kb.search(query=query, top_k=top_k, min_score=min_score)
    if not results:
        print("⚠️  检索未命中任何片段。")
    else:
        print(f"ℹ️  检索命中 {len(results)} 个片段（min_score={min_score}）。")
    return results


def build_rag_prompt(query: str, contexts: list[dict]) -> str:
    """
    构造 RAG Prompt
    """
    context_texts = []
    for idx, ctx in enumerate(contexts, 1):
        snippet = ctx.get("content", "").strip()
        title = ctx.get("paper_title", "未知来源")
        score = ctx.get("score", 0.0)
        context_texts.append(
            f"【参考片段 {idx}｜得分 {score:.4f}｜来源 {title}】\n{snippet}"
        )

    references = "\n\n".join(context_texts)
    prompt = (
        "你将扮演一名学术助手，根据提供的参考片段回答用户问题。"
        "如果参考资料不足或没有包含答案，需要明确说明。\n\n"
        f"### 用户问题\n{query}\n\n"
        f"### 参考资料\n{references}\n\n"
        "请在回答中引用关键论点，保持条理清晰。"
    )
    return prompt


def test_llm(
    provider: str,
    model: str = None,
    prompt: str = None,
    query: str = None,
    use_rag: bool = False,
    top_k: int = 5,
    min_score: float = 0.0,
):
    """
    测试指定的 LLM
    
    Args:
        provider: 提供商名称 (openai, anthropic, deepseek, siliconflow)
        model: 模型名称（可选）
        prompt: 测试提示词（可选）
    """
    print(f"\n{'='*60}")
    print(f"测试 {provider.upper()} LLM")
    print(f"{'='*60}\n")
    
    try:
        # 创建 LLM
        kwargs = {"provider": provider}
        if model:
            kwargs["model"] = model
        
        print(f"正在创建 LLM 实例...")
        llm = LLMFactory.create(**kwargs)
        print(f"✅ LLM 创建成功")
        print(f"   提供商: {provider}")
        print(f"   模型: {llm.model}")
        print(f"   温度: {llm.temperature}")
        print(f"   最大 tokens: {llm.max_tokens}\n")
        
        # 准备测试消息
        test_prompt = prompt or query or "请用一句话介绍你自己。"

        messages = [SystemMessage(content="你是一个有用的助手。")]

        if use_rag or query:
            search_query = query or test_prompt
            contexts = _retrieve_context(
                query=search_query,
                top_k=top_k,
                min_score=min_score,
            )
            if contexts:
                rag_prompt = build_rag_prompt(search_query, contexts)
                messages.append(HumanMessage(content=rag_prompt))
            else:
                messages.append(HumanMessage(content=test_prompt))
        else:
            messages.append(HumanMessage(content=test_prompt))
        
        print(f"正在发送测试消息...")
        print(f"提示词: {test_prompt}\n")
        
        # 调用 LLM
        response = llm.invoke(messages)
        
        print(f"{'='*60}")
        print(f"✅ 测试成功！")
        print(f"{'='*60}")
        print(f"\n响应:\n{response.content}\n")
        
        return True
        
    except ValueError as e:
        print(f"❌ 配置错误: {e}")
        print(f"\n提示: 请确保在 .env 文件中配置了 {provider.upper()}_API_KEY")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="测试单个 LLM 提供商")
    parser.add_argument(
        "--provider",
        type=str,
        required=True,
        choices=["openai", "anthropic", "deepseek", "siliconflow"],
        help="LLM 提供商"
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="模型名称（可选）"
    )
    parser.add_argument(
        "--prompt",
        type=str,
        default=None,
        help="测试提示词（可选）"
    )
    parser.add_argument(
        "--query",
        type=str,
        default=None,
        help="用于检索的查询（启用 RAG 时使用）"
    )
    parser.add_argument(
        "--rag",
        action="store_true",
        help="启用基于知识库的检索增强生成"
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="检索返回的最大片段数量（默认 5）"
    )
    parser.add_argument(
        "--min-score",
        type=float,
        default=0.0,
        help="检索最小得分阈值（默认 0.0）"
    )
    
    args = parser.parse_args()
    
    success = test_llm(
        provider=args.provider,
        model=args.model,
        prompt=args.prompt,
        query=args.query,
        use_rag=args.rag,
        top_k=args.top_k,
        min_score=args.min_score,
    )
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

