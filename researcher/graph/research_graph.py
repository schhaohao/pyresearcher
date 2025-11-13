"""
研究图定义
使用 LangGraph 定义多智能体工作流
"""
from typing import TypedDict, List, Dict, Optional
import os
from langgraph.graph import StateGraph, END
from researcher.agents.searcher import SearcherAgent
from researcher.agents.analyzer import AnalyzerAgent
from researcher.agents.summarizer import SummarizerAgent
from researcher.agents.writer import WriterAgent
from researcher_demo.researcher.utils import logger
from researcher.tools.paper_tools import save_pdf_to_knowledge_base, download_paper


class ResearchState(TypedDict):
    """研究状态"""
    topic: str
    max_papers: int
    papers: List[Dict]
    analyses: List[Dict]
    summaries: List[Dict]
    report: Optional[str]


class ResearchGraph:
    """研究图"""
    
    def __init__(self, config: Optional[dict] = None):
        """
        初始化研究图
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        
        # 初始化智能体
        self.searcher = SearcherAgent()
        self.analyzer = AnalyzerAgent()
        self.summarizer = SummarizerAgent()
        self.writer = WriterAgent()
        
        # 构建图
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """构建状态图"""
        workflow = StateGraph(ResearchState)
        
        # 添加节点
        workflow.add_node("search", self._search_node)
        workflow.add_node("ingest", self._ingest_node)
        workflow.add_node("analyze", self._analyze_node)
        workflow.add_node("summarize", self._summarize_node)
        workflow.add_node("write", self._write_node)
        
        # 定义边
        workflow.set_entry_point("search")
        workflow.add_edge("search", "ingest")
        workflow.add_edge("ingest", "analyze")
        workflow.add_edge("analyze", "summarize")
        workflow.add_edge("summarize", "write")
        workflow.add_edge("write", END)
        
        return workflow.compile()
    
    def _search_node(self, state: ResearchState) -> ResearchState:
        """搜索节点"""
        logger.info("正在搜索论文...")
        papers = self.searcher.search(
            topic=state["topic"],
            max_papers=state["max_papers"]
        )
        return {**state, "papers": papers}
    
    def _ingest_node(self, state: ResearchState) -> ResearchState:
        """知识库入库节点：尝试将搜索结果中的 PDF 写入知识库"""
        logger.info("正在将搜索结果入库（如可用 PDF）...")
        papers = state["papers"] or []
        ingested = 0
        for p in papers:
            source = p.get("source")
            title = p.get("title", "")
            url = p.get("url", "")
            pdf_url = p.get("pdf_url") or ""
            # 对 arXiv：构造或使用 pdf_url
            if source == "arxiv":
                if not pdf_url:
                    paper_id = (p.get("id") or "").split("v")[0] or p.get("id", "")
                    if paper_id:
                        pdf_url = f"https://arxiv.org/pdf/{paper_id}.pdf"
            # 入库（若能解析成功）
            try:
                if pdf_url:
                    # 先下载到本地再解析入库，保证解析器兼容性
                    logger.info("正在下载论文 PDF：%s", pdf_url)
                    local_pdf = download_paper(pdf_url) or ""
                    if local_pdf and os.path.exists(local_pdf):
                        logger.info("正在将论文存入知识库：%s", title)
                        save_pdf_to_knowledge_base(
                            pdf_path=local_pdf,
                            paper_title=title,
                            paper_url=url or pdf_url,
                        )
                        ingested += 1
            except Exception as exc:
                logger.error("入库失败：%s (%s) - %s", title, pdf_url or url, exc)
        logger.info("入库完成，成功入库 %d 篇。", ingested)
        return state
    
    def _analyze_node(self, state: ResearchState) -> ResearchState:
        """分析节点"""
        logger.info("正在分析论文...")
        analyses = self.analyzer.analyze_batch(state["papers"])
        return {**state, "analyses": analyses}
    
    def _summarize_node(self, state: ResearchState) -> ResearchState:
        """摘要节点"""
        logger.info("正在生成摘要...")
        summaries = self.summarizer.summarize_batch(state["analyses"])
        return {**state, "summaries": summaries}
    
    def _write_node(self, state: ResearchState) -> ResearchState:
        """撰写节点"""
        logger.info("正在撰写报告...")
        report = self.writer.write_report(
            topic=state["topic"],
            summaries=state["summaries"]
        )
        return {**state, "report": report}
    
    def run(self, topic: str, max_papers: int = 10) -> Dict:
        """
        运行研究图
        
        Args:
            topic: 调研主题
            max_papers: 最大论文数量
            
        Returns:
            最终状态字典
        """
        initial_state: ResearchState = {
            "topic": topic,
            "max_papers": max_papers,
            "papers": [],
            "analyses": [],
            "summaries": [],
            "report": None,
        }
        
        final_state = self.graph.invoke(initial_state)
        return final_state
    
    def generate_report(self, research_result: Dict) -> str:
        """
        生成报告（如果还没有生成）
        
        Args:
            research_result: 研究结果字典
            
        Returns:
            报告文本
        """
        if research_result.get("report"):
            return research_result["report"]
        
        # 如果没有报告，重新运行撰写节点
        report = self.writer.write_report(
            topic=research_result["topic"],
            summaries=research_result["summaries"]
        )
        return report

