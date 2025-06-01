"""
Resilience utilities for Universal Public Data MCP Server.
Includes circuit breakers, retry logic, and fallback mechanisms.
"""

import asyncio
import time
from typing import Any, Dict, Optional, Callable, List
from datetime import datetime, timedelta
from enum import Enum
from functools import wraps

import structlog

logger = structlog.get_logger(__name__)

class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Blocking requests
    HALF_OPEN = "half_open"  # Testing if service recovered

class CircuitBreaker:
    """
    Circuit breaker pattern implementation for API resilience.
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
        
    def call(self, func: Callable):
        """Decorator to apply circuit breaker to a function."""
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitState.HALF_OPEN
                    logger.info("Circuit breaker half-open, attempting reset")
                else:
                    raise Exception("Circuit breaker is OPEN - service unavailable")
            
            try:
                result = await func(*args, **kwargs)
                self._on_success()
                return result
                
            except self.expected_exception as e:
                self._on_failure()
                raise e
        
        return wrapper
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        return (
            self.last_failure_time and
            time.time() - self.last_failure_time >= self.recovery_timeout
        )
    
    def _on_success(self):
        """Handle successful request."""
        self.failure_count = 0
        self.state = CircuitState.CLOSED
        logger.debug("Circuit breaker reset to CLOSED")
    
    def _on_failure(self):
        """Handle failed request."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning("Circuit breaker OPEN", 
                         failure_count=self.failure_count,
                         threshold=self.failure_threshold)

class RetryPolicy:
    """
    Retry policy with exponential backoff and jitter.
    """
    
    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
    
    def retry(self, exceptions: tuple = (Exception,)):
        """Decorator to apply retry policy to a function."""
        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                last_exception = None
                
                for attempt in range(self.max_attempts):
                    try:
                        return await func(*args, **kwargs)
                    
                    except exceptions as e:
                        last_exception = e
                        
                        if attempt == self.max_attempts - 1:
                            # Last attempt failed
                            logger.error("All retry attempts failed", 
                                       function=func.__name__,
                                       attempts=self.max_attempts,
                                       error=str(e))
                            raise e
                        
                        # Calculate delay for next attempt
                        delay = min(
                            self.base_delay * (self.exponential_base ** attempt),
                            self.max_delay
                        )
                        
                        if self.jitter:
                            import random
                            delay *= (0.5 + random.random() * 0.5)  # Add jitter
                        
                        logger.warning("Retry attempt failed, retrying", 
                                     function=func.__name__,
                                     attempt=attempt + 1,
                                     delay=delay,
                                     error=str(e))
                        
                        await asyncio.sleep(delay)
                
                raise last_exception
            
            return wrapper
        return decorator

class FallbackManager:
    """
    Manages fallback mechanisms for API failures.
    """
    
    def __init__(self):
        self.fallback_functions: Dict[str, List[Callable]] = {}
    
    def register_fallback(self, service_name: str, fallback_func: Callable):
        """Register a fallback function for a service."""
        if service_name not in self.fallback_functions:
            self.fallback_functions[service_name] = []
        self.fallback_functions[service_name].append(fallback_func)
    
    async def execute_with_fallback(
        self,
        service_name: str,
        primary_func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """Execute function with fallback options."""
        try:
            return await primary_func(*args, **kwargs)
        
        except Exception as primary_error:
            logger.warning("Primary service failed, trying fallbacks",
                         service=service_name,
                         error=str(primary_error))
            
            fallbacks = self.fallback_functions.get(service_name, [])
            
            for i, fallback_func in enumerate(fallbacks):
                try:
                    result = await fallback_func(*args, **kwargs)
                    logger.info("Fallback succeeded",
                              service=service_name,
                              fallback_index=i)
                    return result
                
                except Exception as fallback_error:
                    logger.warning("Fallback failed",
                                 service=service_name,
                                 fallback_index=i,
                                 error=str(fallback_error))
                    continue
            
            # All fallbacks failed
            logger.error("All fallbacks failed",
                       service=service_name,
                       primary_error=str(primary_error))
            raise primary_error

class HealthChecker:
    """
    Health checking for external services.
    """
    
    def __init__(self):
        self.service_health: Dict[str, Dict[str, Any]] = {}
    
    async def check_service_health(
        self,
        service_name: str,
        health_check_func: Callable
    ) -> Dict[str, Any]:
        """Check health of a service."""
        start_time = time.time()
        
        try:
            await health_check_func()
            
            health_data = {
                "status": "healthy",
                "response_time": time.time() - start_time,
                "last_check": datetime.now().isoformat(),
                "error": None
            }
            
        except Exception as e:
            health_data = {
                "status": "unhealthy",
                "response_time": time.time() - start_time,
                "last_check": datetime.now().isoformat(),
                "error": str(e)
            }
        
        self.service_health[service_name] = health_data
        return health_data
    
    def get_overall_health(self) -> Dict[str, Any]:
        """Get overall system health."""
        if not self.service_health:
            return {"status": "unknown", "services": {}}
        
        healthy_services = sum(
            1 for health in self.service_health.values()
            if health["status"] == "healthy"
        )
        
        total_services = len(self.service_health)
        health_percentage = (healthy_services / total_services) * 100
        
        overall_status = "healthy" if health_percentage >= 80 else "degraded" if health_percentage >= 50 else "unhealthy"
        
        return {
            "status": overall_status,
            "health_percentage": health_percentage,
            "healthy_services": healthy_services,
            "total_services": total_services,
            "services": self.service_health
        }

# Global instances
circuit_breakers: Dict[str, CircuitBreaker] = {}
fallback_manager = FallbackManager()
health_checker = HealthChecker()

def get_circuit_breaker(service_name: str) -> CircuitBreaker:
    """Get or create circuit breaker for service."""
    if service_name not in circuit_breakers:
        circuit_breakers[service_name] = CircuitBreaker()
    return circuit_breakers[service_name]

# Common retry policies
DEFAULT_RETRY = RetryPolicy(max_attempts=3, base_delay=1.0)
AGGRESSIVE_RETRY = RetryPolicy(max_attempts=5, base_delay=0.5, max_delay=30.0)
CONSERVATIVE_RETRY = RetryPolicy(max_attempts=2, base_delay=2.0) 