"""
Configuration management using Pydantic settings
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
import os

class Settings(BaseSettings):
    """Application settings"""
    
    # Server
    HOST: str = Field(default="0.0.0.0", description="Server host")
    PORT: int = Field(default=8000, description="Server port")
    DEBUG: bool = Field(default=True, description="Debug mode")
    
    # Security
    SECRET_KEY: str = Field(default="dev-secret-key-change-in-production")
    ALLOWED_ORIGINS: List[str] = Field(default=["http://localhost:3000", "http://127.0.0.1:3000"])
    ALLOWED_HOSTS: List[str] = Field(default=["localhost", "127.0.0.1"])
    
    # LLM Configuration
    OLLAMA_HOST: str = Field(default="http://localhost:11434", description="Ollama server URL")
    OLLAMA_MODEL: str = Field(default="llama3:8b", description="Default Ollama model")
    HUGGINGFACE_MODEL: str = Field(default="microsoft/DialoGPT-medium", description="Fallback HF model")
    
    # Database
    DATABASE_URL: str = Field(default="sqlite:///./cqia_tool.db", description="Database URL")
    
    # Analysis Settings
    MAX_REPO_SIZE_MB: int = Field(default=100, description="Maximum repository size in MB")
    MAX_FILE_SIZE_KB: int = Field(default=1000, description="Maximum file size in KB")
    CHUNK_SIZE: int = Field(default=1000, description="Code chunk size for processing")
    
    # RAG Settings
    EMBEDDING_MODEL: str = Field(default="all-MiniLM-L6-v2", description="Sentence transformer model")
    VECTOR_DB_PATH: str = Field(default="./vector_db", description="ChromaDB path")
    TOP_K_RETRIEVAL: int = Field(default=5, description="Top K documents for RAG")
    
    # GitHub Integration
    GITHUB_TOKEN: str = Field(default="", description="GitHub API token")
    
    # Rate Limiting
    RATE_LIMIT: str = Field(default="100/minute", description="API rate limit")
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FILE: str = Field(default="cqia_tool.log", description="Log file path")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

_settings = None

def get_settings() -> Settings:
    """Get cached settings instance"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
