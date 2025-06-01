# Building a Universal Public Data MCP Server: Your Gateway to Real-Time APIs

*How I built a production-ready Model Context Protocol server that unifies 20+ real APIs across 6 categories with comprehensive demo tutorials*

![Universal Public Data MCP Server](https://github.com/inamdarmihir/universal-public-data-mcp-server/raw/main/docs/banner.png)

## 🚀 Introduction

In today's data-driven world, accessing multiple APIs for different types of information can be complex and fragmented. What if you could have a single, unified interface to access financial data, breaking news, weather information, GitHub trends, scientific research, and government statistics all in one place?

That's exactly what I built with the **Universal Public Data MCP Server** - a comprehensive Model Context Protocol (MCP) server that provides seamless access to 20+ real-world APIs through a single, production-ready interface.

## 🎯 What is MCP and Why Does It Matter?

Model Context Protocol (MCP) is a standardized way for AI applications to securely connect to external data sources and tools. Instead of building custom integrations for each API, MCP provides a unified interface that can be used by various AI models and applications.

## 🏗️ Architecture Overview

The Universal Public Data MCP Server is built with Python 3.8+ and follows enterprise-grade patterns:

```
universal-public-data-mcp-server/
├── src/
│   ├── adapters/           # API adapters for each category
│   │   ├── financial.py    # Yahoo Finance, CoinGecko
│   │   ├── news.py         # RSS feeds, sentiment analysis
│   │   ├── geographic.py   # Weather, air quality
│   │   ├── technology.py   # GitHub trends, domain info
│   │   ├── government.py   # Census, economic data
│   │   └── scientific.py   # NASA, research papers
│   ├── core/               # Core infrastructure
│   │   ├── cache.py        # Redis/Memory caching
│   │   ├── config.py       # Configuration management
│   │   └── rate_limiter.py # API rate limiting
│   └── server.py           # Main MCP server
├── demos/                  # Tutorial notebooks
└── docs/                   # Comprehensive documentation
```

## 🔧 Key Features

### 1. **Six Data Categories with 20+ Tools**

- **💰 Financial**: Real-time stock prices, cryptocurrency data, exchange rates
- **📰 News**: Breaking news, RSS feeds, sentiment analysis
- **🏛️ Government**: Census data, economic indicators, SEC filings
- **🌍 Geographic**: Weather data, air quality, disaster alerts
- **🔬 Scientific**: NASA data, research papers, climate information
- **💻 Technology**: GitHub trends, domain information, tech metrics

### 2. **Production-Ready Infrastructure**

- **Caching**: Redis and in-memory caching for performance
- **Rate Limiting**: Intelligent API rate limiting to prevent quota exhaustion
- **Error Handling**: Comprehensive error handling with retry logic
- **Async Operations**: Full async/await support for scalability
- **Configuration**: Environment-based configuration management

### 3. **Real API Integrations**

All data comes from live APIs - no mocks or placeholders:
- Yahoo Finance for stock data
- CoinGecko for cryptocurrency
- GitHub API for trending repositories
- wttr.in for weather data
- RSS feeds for breaking news
- And many more...

## 🛠️ Quick Start Guide

### Installation

```bash
# Clone the repository
git clone https://github.com/inamdarmihir/universal-public-data-mcp-server.git
cd universal-public-data-mcp-server

# Install dependencies
pip install -r requirements.txt

# Start the server
python src/server.py
```

### Basic Usage Example

```python
import asyncio
from src.adapters.financial import FinancialDataAdapter
from src.core.cache import CacheManager
from src.core.config import Config

async def get_stock_data():
    config = Config.load()
    cache_manager = CacheManager(config)
    
    async with FinancialDataAdapter(cache_manager) as adapter:
        # Get real-time Apple stock data
        apple_data = await adapter.get_stock_data("AAPL")
        print(f"Apple stock price: ${apple_data['current_price']:,.2f}")
        
        # Get Bitcoin price
        btc_data = await adapter.get_crypto_data("bitcoin")
        print(f"Bitcoin price: ${btc_data['current_price']:,.2f}")

# Run the example
asyncio.run(get_stock_data())
```

## 📚 Interactive Demo Tutorials

I've created four comprehensive Jupyter notebook tutorials that showcase the server's capabilities:

### 1. Quick Start Tutorial (`01_quick_start.ipynb`)
Perfect for beginners - connects to the MCP server and retrieves real-time Apple stock data:

```python
# Your first real API call
async def get_apple_stock():
    async with FinancialDataAdapter(cache_manager) as adapter:
        result = await adapter.get_stock_data("AAPL")
        return result

apple_data = await get_apple_stock()
print(f"💰 Current Price: ${apple_data['current_price']:,.2f}")
print(f"📈 52W High: ${apple_data['52w_high']:,.2f}")
print("✨ This is REAL data from Yahoo Finance API!")
```

### 2. Understanding Tools (`02_understanding_tools.ipynb`)
Demonstrates all 20+ tools across the six categories:

```python
# Financial tools demo
stocks = {}
for symbol in ['AAPL', 'GOOGL', 'MSFT']:
    data = await adapter.get_stock_data(symbol)
    stocks[symbol] = {
        'price': data['current_price'],
        'company': data['company_name']
    }

# News tools demo
news = await adapter.get_breaking_news('technology', limit=3)

# Weather tools demo
weather = await adapter.get_weather_data('London')

# GitHub tools demo
trends = await adapter.get_github_trends('daily', language='python')
```

### 3. Financial Analysis (`03_financial_analysis.ipynb`)
Advanced portfolio management and cryptocurrency analysis:

```python
# Define portfolio
PORTFOLIO = {
    'AAPL': {'shares': 100, 'name': 'Apple Inc.'},
    'GOOGL': {'shares': 50, 'name': 'Alphabet Inc.'},
    'MSFT': {'shares': 75, 'name': 'Microsoft Corp.'},
    'TSLA': {'shares': 30, 'name': 'Tesla Inc.'}
}

# Calculate portfolio value with live data
portfolio_data = {}
for symbol, info in PORTFOLIO.items():
    data = await adapter.get_stock_data(symbol)
    portfolio_data[symbol] = {
        'price': data['current_price'],
        'shares': info['shares'],
        'value': data['current_price'] * info['shares']
    }

total_value = sum([p['value'] for p in portfolio_data.values()])
print(f"📊 Total Portfolio Value: ${total_value:,.2f}")
```

### 4. Comprehensive Dashboard (`14_comprehensive_dashboard.ipynb`)
Multi-source dashboard combining all categories:

```python
# Collect data from multiple sources
async def collect_dashboard_data():
    data = {}
    
    # Financial data
    async with FinancialDataAdapter(cache_manager) as adapter:
        data['apple'] = await adapter.get_stock_data('AAPL')
        data['bitcoin'] = await adapter.get_crypto_data('bitcoin')
    
    # News data
    async with NewsDataAdapter(cache_manager) as adapter:
        data['news'] = await adapter.get_breaking_news('technology')
    
    # Weather data
    async with GeographicDataAdapter(cache_manager) as adapter:
        data['weather'] = await adapter.get_weather_data('New York')
    
    # GitHub data
    async with TechnologyDataAdapter(cache_manager) as adapter:
        data['github'] = await adapter.get_github_trends('daily')
    
    return data
```

## 🌟 Real-World Applications

This MCP server enables powerful applications:

### 1. **Investment Research Platform**
```python
# Real-time portfolio monitoring
portfolio_value = await calculate_portfolio_value()
market_sentiment = await analyze_news_sentiment()
economic_indicators = await get_economic_data()

# Make informed investment decisions
investment_signal = analyze_market_conditions(
    portfolio_value, market_sentiment, economic_indicators
)
```

### 2. **AI Training Data Pipeline**
```python
# Collect diverse, real-world data for AI training
training_data = {
    'financial_trends': await get_market_trends(),
    'news_sentiment': await analyze_breaking_news(),
    'weather_patterns': await get_climate_data(),
    'tech_innovations': await get_github_trends(),
    'government_policies': await get_policy_updates()
}
```

### 3. **Business Intelligence Dashboard**
```python
# Executive dashboard with real-time metrics
dashboard_metrics = {
    'market_performance': await get_sector_performance(),
    'competitor_analysis': await get_competitor_news(),
    'weather_impact': await get_weather_business_impact(),
    'innovation_tracking': await get_tech_developments()
}
```

## 🔒 Security and Best Practices

The server implements several security measures:

- **Environment Variables**: API keys stored securely
- **Rate Limiting**: Prevents API abuse
- **Input Validation**: Sanitizes all user inputs
- **Error Handling**: Graceful degradation on failures
- **Caching**: Reduces API calls and improves performance

## 📈 Performance Optimizations

### Caching Strategy
```python
# Intelligent caching with TTL
cache_ttl = {
    'stock_data': 60,      # 1 minute for financial data
    'weather': 1800,       # 30 minutes for weather
    'news': 300,           # 5 minutes for news
    'github_trends': 3600  # 1 hour for GitHub trends
}
```

### Async Operations
```python
# Concurrent API calls for better performance
async def get_market_overview():
    tasks = [
        adapter.get_stock_data("AAPL"),
        adapter.get_stock_data("GOOGL"),
        adapter.get_stock_data("MSFT"),
        adapter.get_crypto_data("bitcoin")
    ]
    results = await asyncio.gather(*tasks)
    return process_market_data(results)
```

## 🚀 Getting Started with the Demos

1. **Clone and Setup**:
```bash
git clone https://github.com/inamdarmihir/universal-public-data-mcp-server.git
cd universal-public-data-mcp-server
pip install -r requirements.txt
pip install -r demos/requirements.txt
```

2. **Start the Server**:
```bash
python src/server.py
```

3. **Launch Jupyter**:
```bash
jupyter notebook demos/
```

4. **Run the Tutorials**: Start with `01_quick_start.ipynb` and progress through all four notebooks.

## 🎯 Key Takeaways

Building this Universal Public Data MCP Server taught me several important lessons:

1. **Unified Interfaces Matter**: Having a single interface for multiple data sources dramatically simplifies development
2. **Real Data is Crucial**: Working with live APIs provides authentic experience and catches real-world issues
3. **Production Patterns**: Implementing caching, rate limiting, and error handling from the start saves time later
4. **Documentation is King**: Comprehensive tutorials and examples make the difference between adoption and abandonment

## 🔮 Future Enhancements

The server is designed for extensibility. Future additions could include:

- **More Data Sources**: Social media APIs, IoT sensors, blockchain data
- **Advanced Analytics**: Built-in data analysis and machine learning tools
- **Real-time Streaming**: WebSocket support for live data feeds
- **API Marketplace**: Community-contributed adapters

## 🤝 Contributing

The project is open source and welcomes contributions! Whether you want to:
- Add new API adapters
- Improve existing functionality
- Create additional tutorials
- Enhance documentation

Check out the [Contributing Guide](https://github.com/inamdarmihir/universal-public-data-mcp-server/blob/main/CONTRIBUTING.md) to get started.

## 📞 Connect and Learn More

- **GitHub Repository**: [universal-public-data-mcp-server](https://github.com/inamdarmihir/universal-public-data-mcp-server)
- **Live Demo Notebooks**: Available in the `demos/` directory
- **API Documentation**: Comprehensive docs in the `docs/` folder

Building this MCP server was an exciting journey that combined real-world API integrations, production-grade architecture, and comprehensive educational content. I hope it serves as both a useful tool and a learning resource for the developer community.

*What kind of data integrations would you build with this foundation? I'd love to hear your ideas and use cases!*

---

**Tags**: #MCP #API #Python #RealTimeData #OpenSource #Tutorial #DataIntegration #FinTech #DevTools

*Originally published on [Medium](https://medium.com/@your-username)* 