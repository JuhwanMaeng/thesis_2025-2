from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """환경 변수에서 로드되는 애플리케이션 설정."""
    
    openai_api_key: str = Field(..., description="OpenAI API key")
    openai_chat_model: str = Field(default="gpt-4o-mini", description="GPT model for chat/completions")
    openai_embedding_model: str = Field(default="text-embedding-3-large", description="OpenAI embeddings model")
    openai_embedding_dim: int = Field(default=3072, description="Embedding dimension", gt=0)
    
    mongodb_uri: str = Field(default="mongodb://localhost:27017", description="MongoDB connection URI")
    mongodb_db: str = Field(default="ai_npc_framework", description="MongoDB database name")
    
    faiss_index_dir: str = Field(default="storage/faiss/indices", description="FAISS index directory")
    faiss_meta_dir: str = Field(default="storage/faiss/meta", description="FAISS metadata directory")
    
    app_env: str = Field(default="dev", description="Application environment")
    app_host: str = Field(default="0.0.0.0", description="Application host")
    app_port: int = Field(default=8000, description="Application port", gt=0, lt=65536)
    log_level: str = Field(default="INFO", description="Logging level")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False
    )


settings = Settings()
