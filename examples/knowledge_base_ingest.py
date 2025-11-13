"""
知识库写入示例

用法：
    python examples/knowledge_base_ingest.py --pdf path/to/file.pdf --title "论文标题" --url "http://example.com"
或：
    python examples/knowledge_base_ingest.py --text-file path/to/file.txt --title "论文标题"
或：
    python examples/knowledge_base_ingest.py --title "示例论文" --text "这是论文内容..."
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from researcher.config.settings import get_settings
from researcher.tools.paper_tools import (
    extract_text_from_pdf,
    save_pdf_to_knowledge_base,
)


def load_text(args: argparse.Namespace) -> str:
    """
    根据参数获取论文文本
    """
    if args.text:
        return args.text
    if args.pdf:
        print(f"从 PDF 读取内容: {args.pdf}")
        return extract_text_from_pdf(args.pdf)
    if args.text_file:
        print(f"从文本文件读取内容: {args.text_file}")
        with open(args.text_file, "r", encoding="utf-8") as f:
            return f.read()
    raise ValueError("必须提供 --text、--pdf 或 --text-file 之一")


def main() -> int:
    parser = argparse.ArgumentParser(description="论文写入知识库示例")
    parser.add_argument("--title", required=True, help="论文标题")
    parser.add_argument("--url", default="", help="论文来源 URL")
    parser.add_argument("--pdf", help="PDF 文件路径")
    parser.add_argument("--text-file", help="纯文本文件路径")
    parser.add_argument("--text", help="直接传入的论文内容")

    args = parser.parse_args()
    settings = get_settings()

    paper_text = load_text(args)
    if not paper_text.strip():
        print("论文内容为空，终止。")
        return 1

    print(f"准备写入知识库，标题: {args.title}")
    save_pdf_to_knowledge_base(
        # paper_text=paper_text,
        pdf_path=args.pdf,
        paper_title=args.title,
        paper_url=args.url,
    )

    if settings.es_enabled:
        print("Elasticsearch 知识库已启用，内容已同步写入。")
    else:
        print("当前未启用 Elasticsearch，仅写入本地知识库。")

    print("完成。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())



# python examples/knowledge_base_ingest.py --pdf /Users/sunchenhao/Desktop/多模态方面的论文/De-Diffusion.pdf --title "De-Diffusion" --url "http://example.com"