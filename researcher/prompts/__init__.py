"""
提示词模板模块
"""

from researcher.prompts.search_prompts import SEARCHER_SYSTEM_PROMPT
from researcher.prompts.analysis_prompts import ANALYZER_SYSTEM_PROMPT, SUMMARIZER_SYSTEM_PROMPT
from researcher.prompts.writing_prompts import WRITER_SYSTEM_PROMPT

__all__ = [
    "SEARCHER_SYSTEM_PROMPT",
    "ANALYZER_SYSTEM_PROMPT",
    "SUMMARIZER_SYSTEM_PROMPT",
    "WRITER_SYSTEM_PROMPT",
]

