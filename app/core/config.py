import os
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # アプリケーション基本設定
    APP_NAME: str = "AI API"
    DEBUG: bool = False

    # OpenAI設定
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    MODEL_NAME: str = "gpt-3.5-turbo"  # デフォルトのモデル
    TEMPERATURE: float = 0.7  # デフォルトの温度

    # Pinecone設定
    PINECONE_API_KEY: Optional[str] = None
    PINECONE_INDEX: Optional[str] = None

    # LangSmith設定
    LANGSMITH_TRACING: bool = False
    LANGSMITH_ENDPOINT: Optional[str] = None
    LANGSMITH_API_KEY: Optional[str] = None
    LANGSMITH_PROJECT: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    """
    設定を取得する関数
    キャッシュを使用して、設定の読み込みを最適化
    """
    return Settings()
