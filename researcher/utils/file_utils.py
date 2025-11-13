"""
文件操作工具
"""
import os
from typing import Optional


def ensure_dir(dir_path: str) -> None:
    """
    确保目录存在，如果不存在则创建
    
    Args:
        dir_path: 目录路径
    """
    os.makedirs(dir_path, exist_ok=True)


def read_file(file_path: str, encoding: str = "utf-8") -> str:
    """
    读取文件内容
    
    Args:
        file_path: 文件路径
        encoding: 编码格式
        
    Returns:
        文件内容
    """
    with open(file_path, "r", encoding=encoding) as f:
        return f.read()


def write_file(file_path: str, content: str, encoding: str = "utf-8") -> None:
    """
    写入文件内容
    
    Args:
        file_path: 文件路径
        content: 文件内容
        encoding: 编码格式
    """
    ensure_dir(os.path.dirname(file_path))
    with open(file_path, "w", encoding=encoding) as f:
        f.write(content)

