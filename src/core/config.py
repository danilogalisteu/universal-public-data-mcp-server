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
    """Main configuration class with enhanced environment detection."""
    server: ServerConfig = Field(default_factory=ServerConfig)
    cache: CacheConfig = Field(default_factory=CacheConfig)
    rate_limit: RateLimitConfig = Field(default_factory=RateLimitConfig)
    api_keys: APIKeysConfig = Field(default_factory=APIKeysConfig)
    apis: APIEndpointsConfig = Field(default_factory=APIEndpointsConfig)
    
    @classmethod
    def load(cls, config_path: Optional[str] = None) -> "Config":
        """
        Load configuration from file and environment variables with smart defaults.
        
        Args:
            config_path: Path to YAML configuration file
            
        Returns:
            Config instance with optimized settings
        """
        config_data = {}
        
        # Detect environment
        environment = cls._detect_environment()
        logger.info("Environment detected", environment=environment)
        
        # Apply environment-specific defaults
        config_data.update(cls._get_environment_defaults(environment))
        
        # Load from YAML file if provided
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r') as f:
                    file_config = yaml.safe_load(f) or {}
                config_data = cls._merge_configs(config_data, file_config)
                logger.info("Configuration loaded from file", path=config_path)
            except Exception as e:
                logger.warning("Failed to load config file", path=config_path, error=str(e))
        
        # Override with environment variables
        env_overrides = cls._get_env_overrides()
        config_data = cls._merge_configs(config_data, env_overrides)
        
        # Validate and optimize configuration
        instance = cls(**config_data)
        instance._validate_configuration()
        instance._log_configuration_summary()
        
        return instance
    
    @staticmethod
    def _detect_environment() -> str:
        """Detect the current environment (colab, docker, local, etc.)."""
        import sys
        import platform
        
        # Check for Google Colab
        try:
            import google.colab
            return "colab"
        except ImportError:
            pass
        
        # Check for Docker
        if os.path.exists("/.dockerenv"):
            return "docker"
        
        # Check for common CI environments
        ci_indicators = ["CI", "CONTINUOUS_INTEGRATION", "GITHUB_ACTIONS", "GITLAB_CI"]
        if any(os.getenv(indicator) for indicator in ci_indicators):
            return "ci"
        
        # Check for cloud environments
        cloud_indicators = {
            "AWS_LAMBDA_FUNCTION_NAME": "aws_lambda",
            "GOOGLE_CLOUD_PROJECT": "gcp",
            "WEBSITE_SITE_NAME": "azure"
        }
        for env_var, environment in cloud_indicators.items():
            if os.getenv(env_var):
                return environment
        
        # Check for development indicators
        if os.path.exists(".git") or os.path.exists("pyproject.toml") or os.path.exists("setup.py"):
            return "development"
        
        return "production"
    
    @staticmethod
    def _get_environment_defaults(environment: str) -> Dict[str, Any]:
        """Get optimized defaults for specific environments."""
        defaults = {
            "colab": {
                "server": {
                    "debug": False,
                    "log_level": "INFO"
                },
                "cache": {
                    "enabled": True,
                    "default_ttl": 600,  # Longer TTL in Colab
                    "max_size": 500,  # Smaller cache in Colab
                    "redis_enabled": False
                },
                "rate_limit": {
                    "enabled": True,
                    "requests_per_minute": 30,  # Conservative for Colab
                    "burst_limit": 5
                }
            },
            "docker": {
                "server": {
                    "debug": False,
                    "log_level": "INFO"
                },
                "cache": {
                    "enabled": True,
                    "default_ttl": 300,
                    "max_size": 2000,
                    "redis_enabled": True  # Redis likely available in Docker
                },
                "rate_limit": {
                    "enabled": True,
                    "requests_per_minute": 120,
                    "burst_limit": 20
                }
            },
            "development": {
                "server": {
                    "debug": True,
                    "log_level": "DEBUG"
                },
                "cache": {
                    "enabled": False,  # Disable cache for development
                    "default_ttl": 60,
                    "max_size": 100,
                    "redis_enabled": False
                },
                "rate_limit": {
                    "enabled": False  # No rate limiting in development
                }
            },
            "production": {
                "server": {
                    "debug": False,
                    "log_level": "INFO"
                },
                "cache": {
                    "enabled": True,
                    "default_ttl": 300,
                    "max_size": 5000,
                    "redis_enabled": True
                },
                "rate_limit": {
                    "enabled": True,
                    "requests_per_minute": 100,
                    "burst_limit": 25
                }
            }
        }
        
        return defaults.get(environment, defaults["production"])
    
    def _validate_configuration(self):
        """Validate configuration settings and provide warnings."""
        # Check cache configuration
        if self.cache.enabled and self.cache.redis_enabled:
            # Warn if Redis URL looks invalid
            if not self.cache.redis_url.startswith(("redis://", "rediss://")):
                logger.warning("Redis URL format may be invalid", url=self.cache.redis_url)
        
        # Check rate limiting
        if self.rate_limit.enabled and self.rate_limit.requests_per_minute > 1000:
            logger.warning("Very high rate limit configured", 
                         requests_per_minute=self.rate_limit.requests_per_minute)
        
        # Check API keys
        if not any([self.api_keys.nasa, self.api_keys.alpha_vantage, self.api_keys.news_api]):
            logger.info("No API keys configured - using free tier limits")
    
    def _log_configuration_summary(self):
        """Log a summary of the current configuration."""
        logger.info("Configuration summary",
                   debug=self.server.debug,
                   cache_enabled=self.cache.enabled,
                   redis_enabled=self.cache.redis_enabled,
                   rate_limit_enabled=self.rate_limit.enabled,
                   requests_per_minute=self.rate_limit.requests_per_minute,
                   has_api_keys=bool(self.api_keys.nasa or self.api_keys.alpha_vantage))
    
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