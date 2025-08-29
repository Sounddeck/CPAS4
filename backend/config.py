
"""
Configuration management for Enhanced CPAS Backend
"""

from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings"""
    
    # MongoDB Configuration
    mongodb_uri: str = "mongodb://localhost:27017/cpas_enhanced"
    mongodb_db_name: str = "cpas_enhanced"
    
    # Ollama Configuration
    ollama_base_url: str = "http://localhost:11434"
    default_model: str = "llama3.2:3b"
    
    # FastAPI Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = True
    
    # MemOS Configuration
    memos_backend: str = "mongodb"
    memos_collection: str = "memories"
    memos_index_collection: str = "memory_index"
    
    # Future API Keys
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    
    # Voice Configuration (Future)
    voice_enabled: bool = False
    voice_input_device: Optional[str] = None
    voice_output_device: Optional[str] = None
    
    # Agent Configuration (Future)
    max_agents: int = 10
    agent_timeout: int = 300
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()
