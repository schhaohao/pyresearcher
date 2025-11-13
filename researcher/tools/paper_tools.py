"""
论文处理工具
"""
import hashlib
import json
import os
import re
from datetime import datetime
from typing import Optional

import requests
from pypdf import PdfReader

from researcher.config.settings import get_settings
from researcher.knowledge_base import get_elasticsearch_knowledge_base
from researcher.utils.file_utils import ensure_dir, write_file
from researcher.utils.logger import get_logger
from langchain_community.document_loaders import PyPDFLoader
# from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_text_splitters import RecursiveCharacterTextSplitter



def download_paper(url: str, output_dir: str = "./outputs/papers") -> Optional[str]:
    """
    下载论文 PDF
    
    Args:
        url: 论文 URL
        output_dir: 输出目录
        
    Returns:
        下载的文件路径，如果失败返回 None
    """
    try:
        os.makedirs(output_dir, exist_ok=True)
        
        # 从 URL 提取文件名
        filename = url.split("/")[-1] + ".pdf"
        filepath = os.path.join(output_dir, filename)
        
        # 如果文件已存在，直接返回
        if os.path.exists(filepath):
            return filepath
        
        # 下载文件
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        with open(filepath, "wb") as f:
            f.write(response.content)
        
        return filepath
    except Exception as e:
        print(f"下载论文失败: {e}")
        return None


logger = get_logger("paper_tools")


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    从 PDF 中提取文本
    
    Args:
        pdf_path: PDF 文件路径
        
    Returns:
        提取的文本内容
    """
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"提取 PDF 文本失败: {e}")
        return ""

# #把搜索到的论文都存进知识库中
# def save_paper_to_knowledge_base(
#     paper_text: str,
#     paper_title: str,
#     paper_url: str,
#     output_dir: str = "./outputs/knowledge_base",
# ) -> None:
#     """
#     将论文保存到知识库中

#     Args:
#         paper_text: 论文文本内容
#         paper_title: 论文标题
#         paper_url: 论文 URL
#         output_dir: 输出目录
#     """
#     if not paper_text:
#         logger.warning("论文内容为空，跳过保存: %s", paper_title)
#         return

#     ensure_dir(output_dir)

#     # 生成唯一 ID
#     identifier_source = paper_url or paper_title or str(datetime.utcnow())
#     paper_id = hashlib.md5(identifier_source.encode("utf-8")).hexdigest()

#     timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
#     safe_title = re.sub(r"[^\w\u4e00-\u9fa5]+", "_", paper_title).strip("_") or "paper"
#     filename = f"{timestamp.replace(':', '').replace('-', '')}_{safe_title[:50]}_{paper_id[:8]}.md"
#     filepath = os.path.join(output_dir, filename)

#     # 准备文档内容
#     word_count = len(paper_text.split())
#     preview = paper_text.strip().replace("\n", " ")[:200]
#     document_content = (
#         f"# {paper_title}\n\n"
#         f"- Saved At: {timestamp}\n"
#         f"- Source: {paper_url or 'N/A'}\n"
#         f"- Paper ID: {paper_id}\n"
#         f"- Word Count: {word_count}\n"
#         f"- Preview: {preview}...\n\n"
#         "## Full Text\n\n"
#         f"{paper_text.strip()}\n"
#     )

#     write_file(filepath, document_content)

#     # 更新索引文件
#     index_path = os.path.join(output_dir, "index.jsonl")
#     entries = {}
#     if os.path.exists(index_path):
#         with open(index_path, "r", encoding="utf-8") as index_file:
#             for line in index_file:
#                 if not line.strip():
#                     continue
#                 try:
#                     entry = json.loads(line)
#                     entry_id = entry.get("paper_id")
#                     if entry_id:
#                         entries[entry_id] = entry
#                 except json.JSONDecodeError:
#                     continue

#     entries[paper_id] = {
#         "paper_id": paper_id,
#         "title": paper_title,
#         "url": paper_url,
#         "file": filename,
#         "saved_at": timestamp,
#         "word_count": word_count,
#         "preview": preview,
#     }

#     with open(index_path, "w", encoding="utf-8") as index_file:
#         for entry in entries.values():
#             index_file.write(json.dumps(entry, ensure_ascii=False) + "\n")

#     logger.info("论文已保存到本地知识库: %s -> %s", paper_title, filepath)

#     # 同步写入 Elasticsearch 知识库
#     settings = get_settings()
#     if settings.es_enabled:
#         try:
#             kb = get_elasticsearch_knowledge_base(settings)
#             kb.ingest_document(
#                 paper_id=paper_id,
#                 paper_title=paper_title,
#                 paper_url=paper_url,
#                 paper_text=paper_text,
#             )
#             logger.info("论文已写入 Elasticsearch 知识库: %s", paper_title)
#         except Exception as exc:
#             logger.error("写入 Elasticsearch 知识库失败: %s", exc)


def save_pdf_to_knowledge_base(
    pdf_path: str,
    paper_title: str,
    paper_url: str = "",
    output_dir: str = "./outputs/knowledge_base",
) -> None:
    """
    使用 LangChain 的 PDF 解析器解析 PDF，并写入本地与 Elasticsearch 知识库。
    优先以解析后的 chunks 直接写入 ES，避免二次切分。
    """
    if not os.path.exists(pdf_path):
        logger.error("PDF 文件不存在: %s", pdf_path)
        return

    # 解析 PDF 为页面文档
    loader = PyPDFLoader(pdf_path)
    pages = loader.load()

    # 切分为更小的片段
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=150, separators=["\n\n", "\n", "。", "！", "？", " ", ""]
    )
    chunks_docs = splitter.split_documents(pages)
    chunks = [doc.page_content for doc in chunks_docs if doc.page_content and doc.page_content.strip()]

    if not chunks:
        logger.warning("解析 PDF 后未得到有效片段，跳过: %s", pdf_path)
        return

    # # 本地 Markdown 备份
    # combined_text = "\n\n".join(chunks)
    # save_paper_to_knowledge_base(
    #     paper_text=combined_text,
    #     paper_title=paper_title,
    #     paper_url=paper_url,
    #     output_dir=output_dir,
    # )

    # 直接写入 ES（使用解析后的 chunks）
    settings = get_settings()
    if settings.es_enabled:
        try:
            identifier_source = paper_url or pdf_path or paper_title
            paper_id = hashlib.md5(identifier_source.encode("utf-8")).hexdigest()
            kb = get_elasticsearch_knowledge_base()
            kb.ingest_chunks(
                paper_id=paper_id,
                paper_title=paper_title,
                paper_url=paper_url or pdf_path,
                chunks=chunks,
            )
            logger.info("PDF 解析片段已写入 Elasticsearch 知识库: %s", paper_title)
        except Exception as exc:
            logger.error("写入 Elasticsearch 知识库失败（PDF 模式）: %s", exc)
