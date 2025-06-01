#!/usr/bin/env python3
"""
Test script for Universal Public Data MCP Server
"""

import asyncio
import json
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from server import UniversalPublicDataServer

async def test_server():
    """Test the MCP server functionality."""
    print("🚀 Testing Universal Public Data MCP Server...")
    
    try:
        # Create server instance
        server_instance = UniversalPublicDataServer()
        print("✅ Server instance created successfully")
        
        # Test financial adapter
        print("\n💰 Testing Financial Data...")
        result = await server_instance.financial.get_stock_data("AAPL", timeframe="1d")
        print(f"Stock data result keys: {list(result.keys())}")
        
        if "error" not in result:
            print(f"✅ Successfully retrieved data for {result.get('symbol', 'Unknown')}")
            if "current_price" in result:
                print(f"   Current price: ${result['current_price']}")
        else:
            print(f"⚠️  Error in stock data: {result['error']}")
        
        # Test crypto data
        print("\n🪙 Testing Crypto Data...")
        crypto_result = await server_instance.financial.get_crypto_data("bitcoin")
        print(f"Crypto data result keys: {list(crypto_result.keys())}")
        
        if "error" not in crypto_result:
            print(f"✅ Successfully retrieved crypto data for {crypto_result.get('symbol', 'Unknown')}")
            if "current_price" in crypto_result:
                print(f"   Current price: ${crypto_result['current_price']}")
        else:
            print(f"⚠️  Error in crypto data: {crypto_result['error']}")
        
        # Test exchange rates
        print("\n💱 Testing Exchange Rates...")
        exchange_result = await server_instance.financial.get_exchange_rates("USD", "EUR")
        print(f"Exchange rate result keys: {list(exchange_result.keys())}")
        
        if "error" not in exchange_result:
            print(f"✅ Successfully retrieved exchange rate")
            print(f"   {exchange_result.get('calculation', 'N/A')}")
        else:
            print(f"⚠️  Error in exchange rates: {exchange_result['error']}")
        
        # Test GitHub trends
        print("\n💻 Testing GitHub Trends...")
        github_result = await server_instance.technology.get_github_trends("daily", limit=5)
        print(f"GitHub trends result keys: {list(github_result.keys())}")
        
        if "error" not in github_result:
            print(f"✅ Successfully retrieved GitHub trends")
            print(f"   Found {len(github_result.get('repositories', []))} trending repositories")
        else:
            print(f"⚠️  Error in GitHub trends: {github_result['error']}")
        
        # Test cache stats
        print("\n📊 Testing Cache Statistics...")
        cache_stats = await server_instance.cache.get_cache_stats()
        print(f"Cache stats: {json.dumps(cache_stats, indent=2)}")
        
        print("\n✅ All tests completed!")
        
        # Cleanup
        await server_instance.financial.client.aclose()
        await server_instance.technology.client.aclose()
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Universal Public Data MCP Server Test")
    print("====================================")
    asyncio.run(test_server()) 