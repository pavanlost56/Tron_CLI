"""Configuration management for CodeInsight."""
import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    app_name: str = "CodeInsight"
    version: str = "0.1.0"
    debug: bool = Field(default=False, env="DEBUG")
    
    # Paths
    base_dir: Path = Path(__file__).parent.parent.parent.parent
    data_dir: Path = Field(default_factory=lambda: Path.home() / ".codeinsight")
    cache_dir: Path = Field(default_factory=lambda: Path.home() / ".codeinsight" / "cache")
    
    # LLM Settings
    llm_provider: str = Field(default="ollama", env="LLM_PROVIDER")
    llm_model: str = Field(default="codellama:13b", env="LLM_MODEL")
    ollama_host: str = Field(default="http://localhost:11434", env="OLLAMA_HOST")
    
    # Mistral AI Settings
    mistral_api_key: Optional[str] = Field(default=None, env="MISTRAL_API_KEY")
    mistral_embedding_model: str = Field(default="mistral-embed", env="MISTRAL_EMBEDDING_MODEL")
    mistral_chat_model: str = Field(default="mistral-small", env="MISTRAL_CHAT_MODEL")
    use_mistral_embeddings: bool = Field(default=False, env="USE_MISTRAL_EMBEDDINGS")
    
    # Vector Database
    vector_db_path: Path = Field(default_factory=lambda: Path.home() / ".codeinsight" / "vectordb")
    embedding_model: str = Field(default="all-MiniLM-L6-v2", env="EMBEDDING_MODEL")
    
    # API Settings
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    
    # MCP Settings
    mcp_timeout: int = Field(default=30, env="MCP_TIMEOUT")
    max_retries: int = Field(default=3, env="MAX_RETRIES")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    def ensure_directories(self):
        """Create necessary directories if they don't exist."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.vector_db_path.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
settings.ensure_directories()
