"""
多智能体文献调研系统
基于 LangGraph 的自动文献调研和综述生成系统
"""

__version__ = "0.1.0"
__author__ = "sunchenhao"

# 延迟导入，避免循环依赖
def __getattr__(name):
    if name == "ResearchAgent":
        from researcher.main import ResearchAgent
        return ResearchAgent
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

__all__ = ["ResearchAgent"]

