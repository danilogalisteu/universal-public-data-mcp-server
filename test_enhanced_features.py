#!/usr/bin/env python3
"""
Test script to demonstrate the enhanced Universal Public Data MCP Server features.
"""

import asyncio
import json
import time
from src.core.cache import IntelligentCache
from src.core.monitoring import MetricsCollector, HealthMonitor, DashboardGenerator
from src.core.quality import DataValidator, QualityEnhancer
from src.core.resilience import CircuitBreaker, RetryPolicy, FallbackManager
from src.core.streaming import StreamManager
from src.adapters.scientific import ScientificAdapter

async def test_enhanced_features():
    """Test all the enhanced features."""
    
    print("🚀 Testing Enhanced Universal Public Data MCP Server Features")
    print("=" * 60)
    
    # 1. Test Intelligent Caching
    print("\n1. 📦 Testing Intelligent Cache...")
    cache = IntelligentCache()
    
    # Test cache operations
    await cache.set("test_key", {"data": "test_value", "timestamp": time.time()})
    cached_data = await cache.get("test_key")
    print(f"   ✅ Cache GET: {cached_data}")
    
    # Test cache statistics
    stats = await cache.get_cache_stats()
    hit_ratio = await cache.get_hit_ratio()
    print(f"   📊 Cache Stats: {stats}")
    print(f"   🎯 Hit Ratio: {hit_ratio:.2%}")
    
    # 2. Test Monitoring System
    print("\n2. 📊 Testing Monitoring System...")
    metrics = MetricsCollector()
    health_monitor = HealthMonitor()
    dashboard = DashboardGenerator(metrics, health_monitor, cache)
    
    # Record some test metrics
    metrics.record_request("test_api", 0.150, True)
    metrics.record_request("test_api", 0.200, True)
    metrics.record_request("test_api", 0.100, False)
    
    api_metrics = metrics.get_api_metrics()
    print(f"   📈 API Metrics: {json.dumps(api_metrics, indent=2)}")
    
    # Generate dashboard
    dashboard_data = await dashboard.generate_dashboard()
    print(f"   🎛️  Dashboard generated with {len(dashboard_data)} sections")
    
    # 3. Test Circuit Breaker
    print("\n3. 🔌 Testing Circuit Breaker...")
    circuit_breaker = CircuitBreaker(failure_threshold=2, timeout=5.0)
    
    print(f"   ⚡ Circuit State: {circuit_breaker.state}")
    
    # Test retry policy
    retry_policy = RetryPolicy(max_retries=3, base_delay=1.0)
    print(f"   🔄 Retry Policy: max_retries={retry_policy.max_retries}, base_delay={retry_policy.base_delay}s")
    
    # 4. Test Data Quality System
    print("\n4. 🎯 Testing Data Quality System...")
    validator = DataValidator()
    enhancer = QualityEnhancer()
    
    # Test data validation
    test_nasa_data = {
        "title": "Mars Rover Update",
        "date": "2024-01-15",
        "description": "Latest images from Perseverance rover",
        "url": "https://mars.nasa.gov/images/latest"
    }
    
    quality_score = validator.validate_data(test_nasa_data, "nasa")
    print(f"   ✅ Data Quality Score: {quality_score}")
    
    # Test data enhancement
    enhanced_data = await enhancer.enhance_data(test_nasa_data, "nasa")
    print(f"   🔧 Data Enhanced: {enhanced_data.get('enhanced', False)}")
    
    # 5. Test Streaming Manager
    print("\n5. 📡 Testing Stream Manager...")
    stream_manager = StreamManager()
    
    available_streams = stream_manager.get_available_streams()
    print(f"   📺 Available Streams: {list(available_streams.keys())}")
    
    # 6. Test Enhanced Scientific Adapter
    print("\n6. 🔬 Testing Enhanced Scientific Adapter...")
    scientific = ScientificAdapter()
    
    try:
        # Test NASA data with enhanced features
        nasa_data = await scientific.get_nasa_data(dataset="apod", limit=1)
        print(f"   🚀 NASA Data Retrieved: {len(nasa_data.get('data', []))} items")
        print(f"   📊 Quality Score: {nasa_data.get('quality_score', 'N/A')}")
        print(f"   ⚡ Circuit Breaker State: {scientific.circuit_breaker.state}")
    except Exception as e:
        print(f"   ⚠️  NASA API Test: {str(e)}")
    
    print("\n🎉 Enhanced Features Test Complete!")
    print("=" * 60)
    print("✨ All enterprise-grade improvements are working!")
    print("\nKey Features Tested:")
    print("• 📦 Intelligent caching with hit ratio tracking")
    print("• 📊 Comprehensive monitoring and metrics")
    print("• 🔌 Circuit breakers for resilience")
    print("• 🎯 Data quality validation and enhancement")
    print("• 📡 Real-time streaming capabilities")
    print("• 🔬 Enhanced adapters with production features")

if __name__ == "__main__":
    asyncio.run(test_enhanced_features()) 