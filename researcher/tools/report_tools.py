"""
报告生成工具
"""
import os
from datetime import datetime
from typing import Optional


def save_report(report: str, output_path: Optional[str] = None) -> str:
    """
    保存报告到文件
    
    Args:
        report: 报告内容
        output_path: 输出路径，如果为 None 则自动生成
        
    Returns:
        保存的文件路径
    """
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = "./outputs/reports"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"report_{timestamp}.md")
    
    # 确保目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)
    
    return output_path

