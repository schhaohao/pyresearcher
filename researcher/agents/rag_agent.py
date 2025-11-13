"""
基于 Elasticsearch 知识库的检索增强智能体
"""
from typing import List, Optional

from langchain_core.messages import HumanMessage, SystemMessage

from researcher.config.settings import get_settings
from researcher.knowledge_base import get_elasticsearch_knowledge_base
from researcher.llm import LLMFactory, LLMProvider
from researcher.utils.logger import get_logger


DEFAULT_SYSTEM_PROMPT = (
    "你是一名资深的科研助手。请结合提供的参考资料，"
    "以严谨、有条理的方式回答用户的问题。若参考资料不足以支撑答案，"
    "需要明确说明，"
    "并且给出自己的简介。"
    "请使用中文回答，专业术语可保持英文。"
    "以markdown 格式输出。"
)


class RetrievalQAAgent:
    """
    检索增强问答智能体
    """

    def __init__(
        self,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
    ) -> None:
        self.settings = get_settings()
        self.logger = get_logger("retrieval_qa_agent")
        self.provider = provider or self.settings.default_provider
        self.model = model
        self.system_prompt = system_prompt

    def _ensure_knowledge_base(self):
        if not self.settings.es_enabled:
            raise RuntimeError("Elasticsearch 知识库未启用，请设置 ES_ENABLED=true")
        return get_elasticsearch_knowledge_base()

    def _retrieve_contexts(
        self,
        question: str,
        top_k: int = 5,
        min_score: float = 0.0,
    ) -> List[dict]:
        knowledge_base = self._ensure_knowledge_base()
        results = knowledge_base.search(
            query=question,
            top_k=top_k,
            min_score=min_score,
        )
        if not results:
            self.logger.warning("知识库检索未命中任何片段。")
        else:
            self.logger.info("知识库检索命中 %d 个片段。", len(results))
        return results

    @staticmethod
    def _build_prompt(question: str, contexts: List[dict]) -> str:
        context_blocks = []
        for idx, ctx in enumerate(contexts, 1):
            snippet = ctx.get("content", "").strip()
            title = ctx.get("paper_title", "未知来源")
            score = ctx.get("score", 0.0)
            context_blocks.append(
                f"【参考片段 {idx}｜得分 {score:.4f}｜来源 {title}】\n{snippet}"
            )

        references = "\n\n".join(context_blocks) if context_blocks else "（无参考资料）"
        prompt = (
            "请阅读下面的参考资料，并回答用户问题。回答需基于资料内容，"
            "必要时可指出资料不足。\n\n"
            f"### 用户问题\n{question}\n\n"
            f"### 参考资料\n{references}\n\n"
            "请提供结构化、条理清晰的回答。"
        )
        return prompt

    def answer(
        self,
        question: str,
        *,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        top_k: int = 5,
        min_score: float = 0.0,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        检索增强回答问题

        Args:
            question: 用户问题
            provider: 可选，指定 LLM 提供商
            model: 可选，指定模型
            top_k: 检索片段数量
            min_score: 最小得分阈值
            temperature: 模型温度
            max_tokens: 最大生成 token 数
        """
        contexts = self._retrieve_contexts(
            question=question,
            top_k=top_k,
            min_score=min_score,
        )

        # 构造消息
        messages = [SystemMessage(content=self.system_prompt)]
        prompt = self._build_prompt(question, contexts) if contexts else question
        messages.append(HumanMessage(content=prompt))

        # 创建模型
        llm = LLMFactory.create(
            provider=provider or self.provider,
            model=model or self.model,
            temperature=temperature or self.settings.temperature,
            max_tokens=max_tokens or self.settings.max_tokens,
        )

        self.logger.info(
            "调用 LLM 进行回答，provider=%s，model=%s，检索片段=%d",
            provider or self.provider,
            llm.model,
            len(contexts),
        )

        response = llm.invoke(messages)
        return response.content


__all__ = ["RetrievalQAAgent"]

