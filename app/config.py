from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置"""
    
    # 服务配置
    APP_NAME: str = "AI Customer Service Agent"
    APP_VERSION: str = "3.0.0"
    DEBUG: bool = False
    
    # Java 服务配置
    JAVA_SERVICE_URL: str = "http://localhost:8080"
    
    # LLM 配置
    LLM_PROVIDER: str = "openai"  # openai, claude
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_BASE_URL: Optional[str] = None  # 支持 OpenAI 兼容 API（如 Moonshot）
    
    CLAUDE_API_KEY: Optional[str] = None
    CLAUDE_MODEL: str = "claude-3-5-sonnet-20241022"
    
    # 向量数据库配置
    CHROMA_PERSIST_DIR: str = "./data/chroma"
    
    # Embedding 配置
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    
    # Agent 配置
    MAX_CONVERSATION_TURNS: int = 30
    MAX_UNRESOLVED_COUNT: int = 3
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
