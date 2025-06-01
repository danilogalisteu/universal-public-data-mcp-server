"""
Configuration management for Universal Public Data MCP Server.
"""

import os
from typing import Dict, Any, Optional
from pathlib import Path

import structlog
from pydantic import BaseModel, Field
import yaml
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = structlog.get_logger(__name__)

class ServerConfig(BaseModel):
    """Server configuration."""
    debug: bool = Field(default=False, description="Enable debug mode")
    log_level: str = Field(default="INFO", description="Logging level")

class CacheConfig(BaseModel):
    """Cache configuration."""
    enabled: bool = Field(default=True, description="Enable caching")
    default_ttl: int = Field(default=300, description="Default TTL in seconds")
    max_size: int = Field(default=1000, description="Maximum cache size")
    redis_enabled: bool = Field(default=False, description="Enable Redis caching")
    redis_url: str = Field(default="redis://localhost:6379/0", description="Redis connection URL")

class RateLimitConfig(BaseModel):
    """Rate limiting configuration."""
    enabled: bool = Field(default=True, description="Enable rate limiting")
    requests_per_minute: int = Field(default=60, description="Requests per minute limit")
    burst_limit: int = Field(default=10, description="Burst request limit")

class APIKeysConfig(BaseModel):
    """API keys configuration."""
    nasa: Optional[str] = Field(default=None, description="NASA API key")
    alpha_vantage: Optional[str] = Field(default=None, description="Alpha Vantage API key")
    news_api: Optional[str] = Field(default=None, description="NewsAPI key")
    openweather: Optional[str] = Field(default=None, description="OpenWeatherMap API key")
    airnow: Optional[str] = Field(default=None, description="AirNow API key")
    github: Optional[str] = Field(default=None, description="GitHub API key")

class APIEndpointsConfig(BaseModel):
    """API endpoints configuration."""
    # Government APIs
    census_api_base: str = Field(default="https://api.census.gov/data", description="Census API base URL")
    fred_api_base: str = Field(default="https://api.stlouisfed.org/fred", description="FRED API base URL")
    
    # Scientific APIs
    nasa_api_base: str = Field(default="https://api.nasa.gov", description="NASA API base URL")
    noaa_api_base: str = Field(default="https://api.weather.gov", description="NOAA API base URL")
    
    # Financial APIs
    coingecko_api_base: str = Field(default="https://api.coingecko.com/api/v3", description="CoinGecko API base URL")
    
    # News APIs
    newsapi_base: str = Field(default="https://newsapi.org/v2", description="NewsAPI base URL")
    
    # Technology APIs
    github_api_base: str = Field(default="https://api.github.com", description="GitHub API base URL")

class Config(BaseModel):
    """Main configuration class."""
    server: ServerConfig = Field(default_factory=ServerConfig)
    cache: CacheConfig = Field(default_factory=CacheConfig)
    rate_limit: RateLimitConfig = Field(default_factory=RateLimitConfig)
    api_keys: APIKeysConfig = Field(default_factory=APIKeysConfig)
    apis: APIEndpointsConfig = Field(default_factory=APIEndpointsConfig)
    
    @classmethod
    def load(cls, config_path: Optional[str] = None) -> "Config":
        """
        Load configuration from file and environment variables.
        
        Args:
            config_path: Path to YAML configuration file
            
        Returns:
            Config instance
        """
        config_data = {}
        
        # Load from YAML file if provided
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r') as f:
                    config_data = yaml.safe_load(f) or {}
                logger.info("Configuration loaded from file", path=config_path)
            except Exception as e:
                logger.warning("Failed to load config file", path=config_path, error=str(e))
        
        # Override with environment variables
        env_overrides = cls._get_env_overrides()
        config_data = cls._merge_configs(config_data, env_overrides)
        
        return cls(**config_data)
    
    @staticmethod
    def _get_env_overrides() -> Dict[str, Any]:
        """Extract configuration from environment variables."""
        env_config = {}
        
        # Server configuration
        if os.getenv("DEBUG"):
            env_config.setdefault("server", {})["debug"] = os.getenv("DEBUG").lower() == "true"
        
        if os.getenv("LOG_LEVEL"):
            env_config.setdefault("server", {})["log_level"] = os.getenv("LOG_LEVEL")
        
        # Cache configuration
        if os.getenv("CACHE_ENABLED"):
            env_config.setdefault("cache", {})["enabled"] = os.getenv("CACHE_ENABLED").lower() == "true"
        
        if os.getenv("CACHE_TTL"):
            env_config.setdefault("cache", {})["default_ttl"] = int(os.getenv("CACHE_TTL"))
        
        if os.getenv("REDIS_ENABLED"):
            env_config.setdefault("cache", {})["redis_enabled"] = os.getenv("REDIS_ENABLED").lower() == "true"
        
        if os.getenv("REDIS_URL"):
            env_config.setdefault("cache", {})["redis_url"] = os.getenv("REDIS_URL")
        
        # Rate limiting
        if os.getenv("RATE_LIMIT_ENABLED"):
            env_config.setdefault("rate_limit", {})["enabled"] = os.getenv("RATE_LIMIT_ENABLED").lower() == "true"
        
        if os.getenv("REQUESTS_PER_MINUTE"):
            env_config.setdefault("rate_limit", {})["requests_per_minute"] = int(os.getenv("REQUESTS_PER_MINUTE"))
        
        # API keys from environment
        api_key_mapping = {
            "NASA_API_KEY": ("api_keys", "nasa"),
            "ALPHA_VANTAGE_API_KEY": ("api_keys", "alpha_vantage"),
            "NEWS_API_KEY": ("api_keys", "news_api"),
            "OPENWEATHER_API_KEY": ("api_keys", "openweather"),
            "AIRNOW_API_KEY": ("api_keys", "airnow"),
            "GITHUB_API_KEY": ("api_keys", "github"),
        }
        
        for env_key, (section, config_key) in api_key_mapping.items():
            if os.getenv(env_key):
                env_config.setdefault(section, {})[config_key] = os.getenv(env_key)
        
        return env_config
    
    @staticmethod
    def _merge_configs(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge configuration dictionaries."""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = Config._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result

# Global configuration instance
config = Config() 