"""
Application settings and configuration
"""
import os
from typing import Dict, Any
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Configuration
    app_name: str = "Hardware AI Orchestrator"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # AI Model API Keys
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    groq_api_key: str = ""
    
    # Model Configuration
    default_model: str = "gpt-4o"
    max_tokens: int = 2000
    temperature: float = 0.1
    
    # Classification Configuration
    min_confidence_threshold: float = 0.6
    enable_fallback_routing: bool = True
    
    # Performance Configuration
    request_timeout: int = 30
    max_concurrent_requests: int = 10
    enable_caching: bool = True
    cache_ttl: int = 3600  # 1 hour
    
    class Config:
        env_file = ".env"

# Global settings instance
settings = Settings()
