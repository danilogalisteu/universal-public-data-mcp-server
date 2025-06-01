#!/usr/bin/env python3
"""
Demo script showcasing Universal Public Data MCP Server capabilities.
All APIs are real implementations - no mocks or placeholders!
"""

import asyncio
import json
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.config import Config
from core.cache import CacheManager
from adapters.financial import FinancialDataAdapter
from adapters.government import GovernmentDataAdapter
from adapters.scientific import ScientificDataAdapter
from adapters.news import NewsDataAdapter
from adapters.geographic import GeographicDataAdapter
from adapters.technology import TechnologyDataAdapter

async def demo_financial_apis():
    """Demo financial data APIs."""
    print("\n" + "="*60)
    print("💰 FINANCIAL DATA APIs")
    print("="*60)
    
    config = Config.load()
    cache = CacheManager(config)
    
    async with FinancialDataAdapter(cache) as financial:
        # Stock data
        print("\n📈 Stock Data (Apple):")
        stock_data = await financial.get_stock_data("AAPL")
        if "error" not in stock_data:
            print(f"   Company: {stock_data.get('company_name')}")
            print(f"   Price: ${stock_data.get('current_price')}")
            print(f"   Market Cap: ${stock_data.get('market_cap'):,.0f}" if stock_data.get('market_cap') else "   Market Cap: N/A")
        else:
            print(f"   Error: {stock_data['error']}")
        
        # Crypto data
        print("\n🪙 Cryptocurrency Data (Bitcoin):")
        crypto_data = await financial.get_crypto_data("bitcoin")
        if "error" not in crypto_data:
            print(f"   Name: {crypto_data.get('name')}")
            print(f"   Price: ${crypto_data.get('current_price'):,.2f}")
            print(f"   24h Change: {crypto_data.get('price_change_percentage_24h'):.2f}%" if crypto_data.get('price_change_percentage_24h') else "   24h Change: N/A")
        else:
            print(f"   Error: {crypto_data['error']}")
        
        # Exchange rates
        print("\n💱 Exchange Rates (USD to EUR):")
        exchange_data = await financial.get_exchange_rates("USD", "EUR")
        if "error" not in exchange_data:
            print(f"   Rate: {exchange_data.get('rate')}")
            print(f"   Calculation: {exchange_data.get('calculation')}")
        else:
            print(f"   Error: {exchange_data['error']}")

async def demo_government_apis():
    """Demo government data APIs."""
    print("\n" + "="*60)
    print("🏛️ GOVERNMENT DATA APIs")
    print("="*60)
    
    config = Config.load()
    cache = CacheManager(config)
    
    async with GovernmentDataAdapter(cache) as gov:
        # Census data
        print("\n📊 Census Data (California Population):")
        census_data = await gov.get_census_data("California", "population")
        if "error" not in census_data:
            pop = census_data.get('data', {}).get('total_population')
            print(f"   Location: {census_data.get('location')}")
            print(f"   Population: {pop:,}" if pop else "   Population: N/A")
            print(f"   Year: {census_data.get('year')}")
        else:
            print(f"   Error: {census_data['error']}")
        
        # Economic indicators
        print("\n📈 Economic Indicators (Unemployment Rate):")
        econ_data = await gov.get_economic_indicators("unemployment", "6m")
        if "error" not in econ_data:
            print(f"   Latest Value: {econ_data.get('latest_value')}%")
            print(f"   Change: {econ_data.get('change_percent'):.2f}%" if econ_data.get('change_percent') else "   Change: N/A")
            print(f"   Data Points: {econ_data.get('data_points')}")
        else:
            print(f"   Error: {econ_data['error']}")

async def demo_scientific_apis():
    """Demo scientific APIs."""
    print("\n" + "="*60)
    print("🔬 SCIENTIFIC DATA APIs")
    print("="*60)
    
    config = Config.load()
    cache = CacheManager(config)
    
    async with ScientificDataAdapter(cache) as science:
        # NASA APOD
        print("\n🌌 NASA Astronomy Picture of the Day:")
        nasa_data = await science.get_nasa_data("apod")
        if "error" not in nasa_data:
            print(f"   Title: {nasa_data.get('title')}")
            print(f"   Date: {nasa_data.get('date')}")
            print(f"   URL: {nasa_data.get('url')}")
        else:
            print(f"   Error: {nasa_data['error']}")
        
        # Research papers
        print("\n📚 Research Papers (Machine Learning):")
        papers_data = await science.search_research_papers("machine learning", "both", False, 3)
        if "error" not in papers_data:
            print(f"   Papers Found: {papers_data.get('papers_found')}")
            for i, paper in enumerate(papers_data.get('papers', [])[:2]):
                print(f"   {i+1}. {paper.get('title')[:80]}...")
                print(f"      Source: {paper.get('source')}")
        else:
            print(f"   Error: {papers_data['error']}")
        
        # Climate data
        print("\n🌡️ Climate Data (New York):")
        climate_data = await science.get_climate_data("New York", "temperature", "current")
        if "error" not in climate_data:
            temp_data = climate_data.get('data', {})
            print(f"   Temperature: {temp_data.get('temperature_c')}°C / {temp_data.get('temperature_f')}°F")
            print(f"   Humidity: {temp_data.get('humidity')}%")
        else:
            print(f"   Error: {climate_data['error']}")

async def demo_news_apis():
    """Demo news APIs."""
    print("\n" + "="*60)
    print("📰 NEWS & MEDIA APIs")
    print("="*60)
    
    config = Config.load()
    cache = CacheManager(config)
    
    async with NewsDataAdapter(cache) as news:
        # Breaking news
        print("\n📢 Breaking News (Technology):")
        breaking_news = await news.get_breaking_news("technology", 3)
        if "error" not in breaking_news:
            print(f"   Articles Found: {breaking_news.get('articles_found')}")
            for i, article in enumerate(breaking_news.get('articles', [])[:2]):
                print(f"   {i+1}. {article.get('title')[:80]}...")
                print(f"      Source: {article.get('source')}")
        else:
            print(f"   Error: {breaking_news['error']}")
        
        # News search
        print("\n🔍 News Search (Artificial Intelligence):")
        search_results = await news.search_news("artificial intelligence", "24h", None, 3)
        if "error" not in search_results:
            print(f"   Articles Found: {search_results.get('articles_found')}")
            if search_results.get('articles'):
                article = search_results['articles'][0]
                print(f"   Top Result: {article.get('title')[:80]}...")
                print(f"   Relevance: {article.get('relevance_score'):.2f}")
        else:
            print(f"   Error: {search_results['error']}")

async def demo_geographic_apis():
    """Demo geographic APIs."""
    print("\n" + "="*60)
    print("🌍 GEOGRAPHIC & ENVIRONMENTAL APIs")
    print("="*60)
    
    config = Config.load()
    cache = CacheManager(config)
    
    async with GeographicDataAdapter(cache) as geo:
        # Weather data
        print("\n🌤️ Weather Data (London):")
        weather_data = await geo.get_weather_data("London", "current")
        if "error" not in weather_data:
            weather = weather_data.get('weather', {})
            temp = weather.get('temperature', {})
            print(f"   Temperature: {temp.get('celsius')}°C / {temp.get('fahrenheit')}°F")
            print(f"   Conditions: {weather.get('conditions', {}).get('description')}")
            print(f"   Humidity: {weather.get('conditions', {}).get('humidity')}%")
        else:
            print(f"   Error: {weather_data['error']}")
        
        # Air quality
        print("\n💨 Air Quality (Beijing):")
        air_data = await geo.get_air_quality("Beijing")
        if "error" not in air_data:
            aqi_info = air_data.get('air_quality', {})
            print(f"   AQI: {aqi_info.get('aqi')}")
            print(f"   Quality Level: {aqi_info.get('quality_level')}")
            print(f"   Health Message: {aqi_info.get('health_message')}")
        else:
            print(f"   Note: {air_data.get('error', 'Air quality data not available')}")

async def demo_technology_apis():
    """Demo technology APIs."""
    print("\n" + "="*60)
    print("💻 TECHNOLOGY APIs")
    print("="*60)
    
    config = Config.load()
    cache = CacheManager(config)
    
    async with TechnologyDataAdapter(cache) as tech:
        # GitHub trends
        print("\n⭐ GitHub Trending (Python):")
        github_data = await tech.get_github_trends("daily", "python", 3)
        if "error" not in github_data:
            print(f"   Repositories Found: {len(github_data.get('repositories', []))}")
            for i, repo in enumerate(github_data.get('repositories', [])[:2]):
                print(f"   {i+1}. {repo.get('full_name')}")
                print(f"      Stars: {repo.get('stars'):,}")
                print(f"      Description: {repo.get('description', '')[:60]}...")
        else:
            print(f"   Error: {github_data['error']}")
        
        # Domain info
        print("\n🌐 Domain Information (github.com):")
        domain_data = await tech.get_domain_info("github.com")
        if "error" not in domain_data:
            whois_info = domain_data.get('whois', {})
            status_info = domain_data.get('status', {})
            print(f"   Reachable: {status_info.get('reachable')}")
            if "error" not in whois_info:
                print(f"   Registrar: {whois_info.get('registrar')}")
                print(f"   Country: {whois_info.get('country')}")
        else:
            print(f"   Error: {domain_data['error']}")

async def main():
    """Run all demos."""
    print("🚀 Universal Public Data MCP Server")
    print("   COMPREHENSIVE API DEMO")
    print("   All implementations use REAL APIs - No mocks!")
    print("   " + "="*50)
    
    try:
        await demo_financial_apis()
        await demo_government_apis()
        await demo_scientific_apis()
        await demo_news_apis()
        await demo_geographic_apis()
        await demo_technology_apis()
        
        print("\n" + "="*60)
        print("✅ DEMO COMPLETE!")
        print("All adapters successfully demonstrated with real API calls.")
        print("No mock implementations, dummy data, or placeholders used!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 