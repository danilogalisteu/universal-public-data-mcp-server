"""
Caching and rate limiting for Universal Public Data MCP Server.
"""

import asyncio
import hashlib
import json
import time
from typing import Any, Dict, Optional, Union, Callable
from datetime import datetime, timedelta
from functools import wraps

import structlog
from cachetools import TTLCache

# Optional Redis support
try:
    import aioredis
    REDIS_AVAILABLE = True
except (ImportError, TypeError) as e:
    # Handle both import errors and Python 3.13 compatibility issues
    REDIS_AVAILABLE = False
    aioredis = None

logger = structlog.get_logger(__name__)

class CacheManager:
    """
    Manages caching and rate limiting for API requests.
    Supports both in-memory and Redis caching (Redis optional).
    """
    
    def __init__(self, config):
        self.config = config
        self.enabled = config.cache.enabled
        
        # In-memory cache
        self.memory_cache = TTLCache(
            maxsize=config.cache.max_size,
            ttl=config.cache.default_ttl
        )
        
        # Redis cache (if enabled and available)
        self.redis_client = None
        self.redis_enabled = config.cache.redis_enabled and REDIS_AVAILABLE
        
        if not REDIS_AVAILABLE and config.cache.redis_enabled:
            logger.warning("Redis support disabled - aioredis not available")
        
        # Rate limiting storage
        self.rate_limits: Dict[str, Dict[str, Any]] = {}
        
        # Cache warming storage
        self.cache_warming_tasks: Dict[str, asyncio.Task] = {}
        
        # Cache statistics
        self.stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "errors": 0,
            "warm_cache_hits": 0
        }
        
        # Initialize Redis if configured and available
        if self.redis_enabled:
            # Don't create the task immediately - wait for first use
            self._redis_init_task = None
            logger.info("Redis cache will be initialized on first use")
    
    async def _init_redis(self):
        """Initialize Redis connection."""
        if not REDIS_AVAILABLE:
            return
            
        try:
            self.redis_client = await aioredis.from_url(
                self.config.cache.redis_url,
                decode_responses=True
            )
            await self.redis_client.ping()
            logger.info("Redis cache initialized successfully")
        except Exception as e:
            logger.warning("Failed to initialize Redis cache", error=str(e))
            self.redis_enabled = False
    
    def _generate_cache_key(self, prefix: str, **kwargs) -> str:
        """Generate a cache key from prefix and arguments."""
        # Sort kwargs for consistent key generation
        sorted_kwargs = sorted(kwargs.items())
        key_data = f"{prefix}:" + ":".join(f"{k}={v}" for k, v in sorted_kwargs)
        
        # Hash long keys to prevent issues
        if len(key_data) > 250:
            key_hash = hashlib.md5(key_data.encode()).hexdigest()
            return f"{prefix}:hash:{key_hash}"
        
        return key_data
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache with improved statistics."""
        if not self.enabled:
            return None
        
        try:
            # Try Redis first (if available)
            if self.redis_enabled and self.redis_client:
                value = await self.redis_client.get(key)
                if value is not None:
                    self.stats["hits"] += 1
                    return json.loads(value)
            
            # Fall back to memory cache
            result = self.memory_cache.get(key)
            if result is not None:
                self.stats["hits"] += 1
                return result
            
            self.stats["misses"] += 1
            return None
            
        except Exception as e:
            self.stats["errors"] += 1
            logger.warning("Cache get failed", key=key, error=str(e))
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with improved error handling."""
        if not self.enabled:
            return False
        
        ttl = ttl or self.config.cache.default_ttl
        
        try:
            # Store in Redis if available
            if self.redis_enabled and self.redis_client:
                await self.redis_client.setex(
                    key, 
                    ttl, 
                    json.dumps(value, default=str)
                )
            
            # Always store in memory cache as backup
            self.memory_cache[key] = value
            self.stats["sets"] += 1
            return True
            
        except Exception as e:
            self.stats["errors"] += 1
            logger.warning("Cache set failed", key=key, error=str(e))
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        try:
            # Delete from Redis (if available)
            if self.redis_enabled and self.redis_client:
                await self.redis_client.delete(key)
            
            # Delete from memory cache
            if key in self.memory_cache:
                del self.memory_cache[key]
            
            return True
            
        except Exception as e:
            logger.warning("Cache delete failed", key=key, error=str(e))
            return False
    
    async def clear(self, pattern: Optional[str] = None) -> bool:
        """Clear cache entries, optionally matching a pattern."""
        try:
            if pattern:
                # Clear pattern matches from Redis (if available)
                if self.redis_enabled and self.redis_client:
                    keys = await self.redis_client.keys(pattern)
                    if keys:
                        await self.redis_client.delete(*keys)
                
                # Clear pattern matches from memory cache
                keys_to_delete = [k for k in self.memory_cache.keys() if pattern in k]
                for key in keys_to_delete:
                    del self.memory_cache[key]
            else:
                # Clear all
                if self.redis_enabled and self.redis_client:
                    await self.redis_client.flushdb()
                self.memory_cache.clear()
            
            return True
            
        except Exception as e:
            logger.warning("Cache clear failed", pattern=pattern, error=str(e))
            return False
    
    def check_rate_limit(self, identifier: str, limit: Optional[int] = None) -> bool:
        """
        Check if identifier is within rate limit.
        Returns True if request is allowed, False if rate limited.
        """
        if not self.config.rate_limit.enabled:
            return True
        
        limit = limit or self.config.rate_limit.requests_per_minute
        current_time = time.time()
        window_start = current_time - 60  # 1 minute window
        
        # Initialize rate limit tracking for this identifier
        if identifier not in self.rate_limits:
            self.rate_limits[identifier] = {
                "requests": [],
                "last_cleanup": current_time
            }
        
        rate_data = self.rate_limits[identifier]
        
        # Clean up old requests (older than 1 minute)
        if current_time - rate_data["last_cleanup"] > 10:  # Cleanup every 10 seconds
            rate_data["requests"] = [
                req_time for req_time in rate_data["requests"] 
                if req_time > window_start
            ]
            rate_data["last_cleanup"] = current_time
        
        # Check if within limit
        recent_requests = len([
            req_time for req_time in rate_data["requests"] 
            if req_time > window_start
        ])
        
        if recent_requests >= limit:
            logger.warning("Rate limit exceeded", identifier=identifier, limit=limit)
            return False
        
        # Record this request
        rate_data["requests"].append(current_time)
        return True
    
    def cached(self, ttl: Optional[int] = None, key_prefix: str = "cached"):
        """
        Decorator for caching function results.
        
        Args:
            ttl: Time to live in seconds
            key_prefix: Prefix for cache key
        """
        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Generate cache key
                cache_key = self._generate_cache_key(
                    f"{key_prefix}:{func.__name__}",
                    args=str(args),
                    **kwargs
                )
                
                # Try to get from cache
                cached_result = await self.get(cache_key)
                if cached_result is not None:
                    logger.debug("Cache hit", function=func.__name__, key=cache_key)
                    return cached_result
                
                # Execute function
                logger.debug("Cache miss", function=func.__name__, key=cache_key)
                result = await func(*args, **kwargs)
                
                # Store in cache
                await self.set(cache_key, result, ttl)
                
                return result
            
            return wrapper
        return decorator
    
    def rate_limited(self, limit: Optional[int] = None, identifier_func: Optional[Callable] = None):
        """
        Decorator for rate limiting function calls.
        
        Args:
            limit: Requests per minute limit
            identifier_func: Function to generate identifier from args/kwargs
        """
        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Generate identifier
                if identifier_func:
                    identifier = identifier_func(*args, **kwargs)
                else:
                    identifier = f"{func.__name__}:default"
                
                # Check rate limit
                if not self.check_rate_limit(identifier, limit):
                    raise Exception(f"Rate limit exceeded for {identifier}")
                
                return await func(*args, **kwargs)
            
            return wrapper
        return decorator
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        stats = {
            "enabled": self.enabled,
            "memory_cache": {
                "size": len(self.memory_cache),
                "max_size": self.memory_cache.maxsize,
                "ttl": self.memory_cache.ttl
            },
            "redis": {
                "available": REDIS_AVAILABLE,
                "enabled": self.redis_enabled,
                "connected": self.redis_client is not None
            },
            "rate_limits": {
                "active_identifiers": len(self.rate_limits),
                "enabled": self.config.rate_limit.enabled
            },
            "cache_stats": self.stats
        }
        
        # Get Redis stats if available
        if self.redis_enabled and self.redis_client:
            try:
                redis_info = await self.redis_client.info("memory")
                stats["redis"]["memory_usage"] = redis_info.get("used_memory_human", "N/A")
                stats["redis"]["keys"] = await self.redis_client.dbsize()
            except Exception as e:
                logger.warning("Failed to get Redis stats", error=str(e))
        
        return stats

    async def warm_cache(self, key: str, warm_func: Callable, ttl: Optional[int] = None, interval: int = 3600):
        """
        Warm cache with periodic updates for frequently accessed data.
        
        Args:
            key: Cache key to warm
            warm_func: Async function to generate fresh data
            ttl: Cache TTL in seconds
            interval: Refresh interval in seconds
        """
        async def _warm_task():
            while True:
                try:
                    # Generate fresh data
                    fresh_data = await warm_func()
                    await self.set(key, fresh_data, ttl)
                    self.stats["warm_cache_hits"] += 1
                    logger.debug("Cache warmed", key=key)
                    
                    # Wait for next refresh
                    await asyncio.sleep(interval)
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.warning("Cache warming failed", key=key, error=str(e))
                    await asyncio.sleep(60)  # Wait 1 minute before retry
        
        # Cancel existing warming task if any
        if key in self.cache_warming_tasks:
            self.cache_warming_tasks[key].cancel()
        
        # Start new warming task
        self.cache_warming_tasks[key] = asyncio.create_task(_warm_task())

    async def get_hit_ratio(self) -> float:
        """Calculate cache hit ratio."""
        total_requests = self.stats["hits"] + self.stats["misses"]
        if total_requests == 0:
            return 0.0
        return self.stats["hits"] / total_requests

class RateLimitExceededError(Exception):
    """Raised when rate limit is exceeded."""
    pass