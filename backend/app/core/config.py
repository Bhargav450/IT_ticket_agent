import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Autonomous IT Support Agent"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    # LLM Settings (Ollama by default)
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.2")
    OLLAMA_EMBED_MODEL: str = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
    
    # Optional Cloud API keys
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", None)
    AZURE_OPENAI_API_KEY: Optional[str] = os.getenv("AZURE_OPENAI_API_KEY", None)
    AZURE_OPENAI_ENDPOINT: Optional[str] = os.getenv("AZURE_OPENAI_ENDPOINT", None)
    
    # Database (SQLite default for zero-friction setup, PostgreSQL supported)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./it_support_agent.db")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-it-support-agent-jwt-key-32chars")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    
    # LangSmith Tracing (Optional)
    LANGCHAIN_TRACING_V2: str = os.getenv("LANGCHAIN_TRACING_V2", "false")
    LANGCHAIN_API_KEY: Optional[str] = os.getenv("LANGCHAIN_API_KEY", None)
    LANGCHAIN_PROJECT: str = os.getenv("LANGCHAIN_PROJECT", "autonomous-it-support")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
