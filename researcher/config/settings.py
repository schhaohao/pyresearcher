"""
配置设置
"""
from typing import Optional
from dotenv import load_dotenv
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings


# 加载环境变量
load_dotenv()


class Settings(BaseSettings):
    """应用配置
    
    Pydantic BaseSettings 会自动从环境变量读取配置
    环境变量名会自动转换为字段名（大写+下划线 -> 小写+下划线）
    例如：OPENAI_API_KEY -> openai_api_key
    """
    
    # API Keys
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    deepseek_api_key: Optional[str] = None
    siliconflow_api_key: Optional[str] = None
    
    # 默认提供商
    default_provider: str = "siliconflow"
    
    # 模型配置
    default_model: str = "deepseek-ai/DeepSeek-V3.2-Exp"
    temperature: float = 0.7
    max_tokens: int = 4096
    
    # 各厂商的默认模型
    openai_model: str = "gpt-4"
    anthropic_model: str = "claude-3-sonnet-20240229"
    deepseek_model: str = "deepseek-chat"
    siliconflow_model: str = "deepseek-ai/DeepSeek-V3.2-Exp"  # 或其他可用模型，如 Qwen/QwQ-32B
    
    # Elasticsearch 配置
    es_enabled: bool = True
    es_host: str = "localhost"
    es_port: int = 9200
    es_scheme: str = "http"
    es_index: str = "researcher-knowledge-base"
    es_embedding_model: str = "text-m3"
    es_username: Optional[str] = None
    es_password: Optional[str] = None
    es_ca_cert_path: Optional[str] = None
    
    # Embedding 服务配置
    embedding_service_base_url: str = "http://localhost:8000/v1"
    embedding_service_api_key: Optional[str] = None
    embedding_service_model_name: str = "bge-m3"
    
    # 搜索配置
    max_papers: int = 10
    default_search_engine: str = "arxiv"
    
    # 输出配置
    output_dir: str = "./outputs"
    papers_dir: str = "./outputs/papers"
    reports_dir: str = "./outputs/reports"
    
    # 日志配置
    log_level: str = "INFO"
    log_file: Optional[str] = None
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# 全局配置实例
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    获取配置实例（单例模式）
    
    Returns:
        配置实例
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

