# API configuration module
import os
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Results directory for storing research outputs
RESULTS_DIR = BASE_DIR / "results"
if not RESULTS_DIR.exists():
    RESULTS_DIR.mkdir(parents=True)

# API Configuration
API_CONFIG: Dict[str, Any] = {
    "title": "FuturNod Researcher API",
    "description": "API for conducting AI-powered research using GPT-Researcher and Tavily API",
    "version": "1.0.0",
    "docs_url": "/docs",
    "redoc_url": "/redoc"
}

# Security Configuration
SECURITY_CONFIG: Dict[str, Any] = {
    "secret_key": os.getenv("SECRET_KEY", "default-insecure-key-change-this"),
    "algorithm": "HS256",
    "access_token_expire_minutes": 30,
    "ssl_enabled": os.getenv("SSL_ENABLED", "false").lower() == "true"
}

# GPT-Researcher and Tavily API Config
RESEARCHER_CONFIG: Dict[str, Any] = {
    "openai_api_key": os.getenv("OPENAI_API_KEY", ""),
    "tavily_api_key": os.getenv("TAVILY_API_KEY", ""),
    "other_api_keys": {}  # Add other API keys as needed
}

# Cache Configuration
CACHE_CONFIG: Dict[str, Any] = {
    "enabled": os.getenv("CACHE_ENABLED", "true").lower() == "true",
    "type": os.getenv("CACHE_TYPE", "memory"),  # "memory" or "redis"
    "redis_url": os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    "ttl": int(os.getenv("CACHE_TTL", "3600"))  # Default cache TTL in seconds (1 hour)
}

# Logging Configuration
LOGGING_CONFIG: Dict[str, Any] = {
    "level": os.getenv("LOG_LEVEL", "INFO"),
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
}

# Get encrypted API key
def get_api_key(key_name: str) -> Optional[str]:
    """
    Get an API key from environment variables.
    In a production environment, implement proper encryption/decryption.
    """
    # For demonstration, we're just getting from env vars
    # In production, implement proper encryption/decryption
    return RESEARCHER_CONFIG.get(key_name, None)