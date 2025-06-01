"""
Monitoring and metrics collection for Universal Public Data MCP Server.
"""

import asyncio
import time
import psutil
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict, deque
from dataclasses import dataclass

import structlog

logger = structlog.get_logger(__name__)

@dataclass
class MetricPoint:
    """Single metric data point."""
    timestamp: datetime
    value: float
    tags: Dict[str, str]

class MetricsCollector:
    """Collects and aggregates system metrics."""
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_history))
        self.start_time = datetime.now()
        
        # Performance counters
        self.request_count = 0
        self.error_count = 0
        self.total_response_time = 0.0
        
        # API-specific metrics
        self.api_metrics = defaultdict(lambda: {
            "requests": 0,
            "errors": 0,
            "total_time": 0.0,
            "last_request": None
        })
    
    def record_metric(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Record a metric value."""
        point = MetricPoint(
            timestamp=datetime.now(),
            value=value,
            tags=tags or {}
        )
        self.metrics[name].append(point)
    
    def record_request(self, api_name: str, response_time: float, success: bool = True):
        """Record API request metrics."""
        self.request_count += 1
        self.total_response_time += response_time
        
        api_stats = self.api_metrics[api_name]
        api_stats["requests"] += 1
        api_stats["total_time"] += response_time
        api_stats["last_request"] = datetime.now()
        
        if not success:
            self.error_count += 1
            api_stats["errors"] += 1
        
        # Record detailed metrics
        self.record_metric(f"api.{api_name}.response_time", response_time)
        self.record_metric(f"api.{api_name}.requests", 1)
        if not success:
            self.record_metric(f"api.{api_name}.errors", 1)
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics."""
        # CPU and memory usage
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Network I/O
        network = psutil.net_io_counters()
        
        uptime = datetime.now() - self.start_time
        
        return {
            "uptime_seconds": uptime.total_seconds(),
            "cpu_percent": cpu_percent,
            "memory": {
                "total": memory.total,
                "available": memory.available,
                "percent": memory.percent,
                "used": memory.used
            },
            "disk": {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": (disk.used / disk.total) * 100
            },
            "network": {
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv,
                "packets_sent": network.packets_sent,
                "packets_recv": network.packets_recv
            }
        }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        avg_response_time = (
            self.total_response_time / self.request_count 
            if self.request_count > 0 else 0
        )
        
        error_rate = (
            (self.error_count / self.request_count) * 100 
            if self.request_count > 0 else 0
        )
        
        # Calculate requests per minute
        uptime_minutes = (datetime.now() - self.start_time).total_seconds() / 60
        requests_per_minute = self.request_count / uptime_minutes if uptime_minutes > 0 else 0
        
        return {
            "total_requests": self.request_count,
            "total_errors": self.error_count,
            "error_rate_percent": error_rate,
            "avg_response_time_ms": avg_response_time * 1000,
            "requests_per_minute": requests_per_minute
        }
    
    def get_api_metrics(self) -> Dict[str, Any]:
        """Get per-API metrics."""
        api_summary = {}
        
        for api_name, stats in self.api_metrics.items():
            avg_time = (
                stats["total_time"] / stats["requests"] 
                if stats["requests"] > 0 else 0
            )
            
            error_rate = (
                (stats["errors"] / stats["requests"]) * 100 
                if stats["requests"] > 0 else 0
            )
            
            api_summary[api_name] = {
                "requests": stats["requests"],
                "errors": stats["errors"],
                "error_rate_percent": error_rate,
                "avg_response_time_ms": avg_time * 1000,
                "last_request": stats["last_request"].isoformat() if stats["last_request"] else None
            }
        
        return api_summary
    
    def get_metric_history(self, metric_name: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get historical data for a metric."""
        if metric_name not in self.metrics:
            return []
        
        points = list(self.metrics[metric_name])[-limit:]
        return [
            {
                "timestamp": point.timestamp.isoformat(),
                "value": point.value,
                "tags": point.tags
            }
            for point in points
        ]

class HealthMonitor:
    """Monitors system health and service availability."""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics = metrics_collector
        self.health_checks = {}
        self.alert_thresholds = {
            "cpu_percent": 80.0,
            "memory_percent": 85.0,
            "disk_percent": 90.0,
            "error_rate_percent": 5.0,
            "avg_response_time_ms": 5000.0
        }
        self.alerts = deque(maxlen=100)
    
    def register_health_check(self, name: str, check_func, interval: int = 60):
        """Register a periodic health check."""
        self.health_checks[name] = {
            "function": check_func,
            "interval": interval,
            "last_check": None,
            "status": "unknown",
            "message": None
        }
    
    async def run_health_checks(self):
        """Run all registered health checks."""
        current_time = datetime.now()
        
        for name, check_info in self.health_checks.items():
            # Check if it's time to run this health check
            if (check_info["last_check"] is None or 
                (current_time - check_info["last_check"]).total_seconds() >= check_info["interval"]):
                
                try:
                    result = await check_info["function"]()
                    check_info["status"] = "healthy" if result else "unhealthy"
                    check_info["message"] = result.get("message", "") if isinstance(result, dict) else None
                    check_info["last_check"] = current_time
                    
                except Exception as e:
                    check_info["status"] = "error"
                    check_info["message"] = str(e)
                    check_info["last_check"] = current_time
                    logger.error("Health check failed", check=name, error=str(e))
    
    def check_system_health(self) -> Dict[str, Any]:
        """Check overall system health against thresholds."""
        system_metrics = self.metrics.get_system_metrics()
        performance_metrics = self.metrics.get_performance_metrics()
        
        alerts = []
        health_score = 100.0
        
        # Check CPU usage
        if system_metrics["cpu_percent"] > self.alert_thresholds["cpu_percent"]:
            alerts.append({
                "type": "cpu_high",
                "message": f"CPU usage high: {system_metrics['cpu_percent']:.1f}%",
                "severity": "warning"
            })
            health_score -= 10
        
        # Check memory usage
        if system_metrics["memory"]["percent"] > self.alert_thresholds["memory_percent"]:
            alerts.append({
                "type": "memory_high",
                "message": f"Memory usage high: {system_metrics['memory']['percent']:.1f}%",
                "severity": "warning"
            })
            health_score -= 15
        
        # Check disk usage
        if system_metrics["disk"]["percent"] > self.alert_thresholds["disk_percent"]:
            alerts.append({
                "type": "disk_high",
                "message": f"Disk usage high: {system_metrics['disk']['percent']:.1f}%",
                "severity": "critical"
            })
            health_score -= 20
        
        # Check error rate
        if performance_metrics["error_rate_percent"] > self.alert_thresholds["error_rate_percent"]:
            alerts.append({
                "type": "error_rate_high",
                "message": f"Error rate high: {performance_metrics['error_rate_percent']:.1f}%",
                "severity": "critical"
            })
            health_score -= 25
        
        # Check response time
        if performance_metrics["avg_response_time_ms"] > self.alert_thresholds["avg_response_time_ms"]:
            alerts.append({
                "type": "response_time_high",
                "message": f"Response time high: {performance_metrics['avg_response_time_ms']:.0f}ms",
                "severity": "warning"
            })
            health_score -= 10
        
        # Store new alerts
        for alert in alerts:
            alert["timestamp"] = datetime.now().isoformat()
            self.alerts.append(alert)
        
        # Determine overall status
        if health_score >= 90:
            status = "healthy"
        elif health_score >= 70:
            status = "degraded"
        else:
            status = "unhealthy"
        
        return {
            "status": status,
            "health_score": max(0, health_score),
            "alerts": alerts,
            "health_checks": {
                name: {
                    "status": info["status"],
                    "last_check": info["last_check"].isoformat() if info["last_check"] else None,
                    "message": info["message"]
                }
                for name, info in self.health_checks.items()
            }
        }
    
    def get_recent_alerts(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent alerts."""
        return list(self.alerts)[-limit:]

class DashboardGenerator:
    """Generates monitoring dashboard data."""
    
    def __init__(self, metrics_collector: MetricsCollector, health_monitor: HealthMonitor):
        self.metrics = metrics_collector
        self.health = health_monitor
    
    async def generate_dashboard(self) -> Dict[str, Any]:
        """Generate complete dashboard data."""
        # Run health checks
        await self.health.run_health_checks()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "system": self.metrics.get_system_metrics(),
            "performance": self.metrics.get_performance_metrics(),
            "apis": self.metrics.get_api_metrics(),
            "health": self.health.check_system_health(),
            "recent_alerts": self.health.get_recent_alerts(),
            "uptime": {
                "start_time": self.metrics.start_time.isoformat(),
                "uptime_seconds": (datetime.now() - self.metrics.start_time).total_seconds()
            }
        }

# Global monitoring instances
metrics_collector = MetricsCollector()
health_monitor = HealthMonitor(metrics_collector)
dashboard_generator = DashboardGenerator(metrics_collector, health_monitor) 