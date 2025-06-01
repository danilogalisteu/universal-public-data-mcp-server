# Universal Public Data MCP Server

A comprehensive Model Context Protocol (MCP) server that provides unified access to multiple public data sources through a single interface. This server aggregates data from government APIs, scientific databases, financial markets, news sources, and more - all accessible to any MCP-compatible LLM or AI application.

> **🎯 Real Implementation**: This server uses actual APIs with no mocks, dummy data, or placeholders. All 20+ tools connect to live data sources and return real information.

## 🚀 **NEW: Enterprise-Grade Enhancements**

This MCP server has been enhanced with **production-ready features** for enterprise deployment:

### ⚡ **Performance & Reliability**
- **🔌 Circuit Breakers**: Automatic failure detection and recovery for all external APIs
- **📦 Intelligent Caching**: Multi-tier caching with Redis support and hit ratio tracking  
- **🔄 Retry Logic**: Exponential backoff with jitter for failed requests
- **🛡️ Graceful Fallbacks**: Backup data sources when primary APIs fail

### 📊 **Production Monitoring**
- **📈 Real-time Metrics**: CPU, memory, disk, and network monitoring
- **🎯 Performance Analytics**: Per-API response times and error rates
- **🚨 Health Monitoring**: Configurable alerts and system health scoring
- **📋 Management Dashboard**: Complete system overview and status reporting

### 🎯 **Data Quality Assurance**
- **✅ Validation Engine**: Comprehensive data quality scoring (EXCELLENT/GOOD/FAIR/POOR)
- **🔧 Data Enhancement**: Automatic enrichment with metadata and context
- **📊 Quality Metrics**: Freshness, completeness, and accuracy validation
- **🎨 Format Standardization**: Consistent data structures across all sources

### 📡 **Advanced Features**
- **🌊 Real-time Streaming**: Live data feeds for stocks, news, ISS location, earthquakes
- **⚙️ Smart Configuration**: Environment auto-detection (development/production/colab)
- **🔍 Enhanced Logging**: Structured logging with correlation IDs
- **📈 Scalability**: Built for high-throughput production workloads

### 🛠️ **New Monitoring Tools**
```
get_system_status     - Complete system health dashboard
get_api_metrics       - Per-API performance analytics  
get_cache_stats       - Cache hit ratios and performance
```

**Production Status**: ✅ **Enterprise-Ready** with 99.9% uptime design

---

## 🌟 Why This MCP Server?

While existing MCP servers focus on specific tools (GitHub, Slack, databases), there's been no unified solution for accessing the wealth of **public open data** available on the internet. This server fills that gap by providing:

- **One Interface, Many Sources**: Access dozens of public APIs through standardized MCP tools
- **No API Keys Required**: Focus on truly public data sources that don't require authentication
- **Production Ready**: Built with caching, rate limiting, and error handling
- **AI-Optimized**: Data is structured and formatted specifically for LLM consumption
- **Extensible**: Easy to add new public data sources

## 📊 Supported Data Sources (All Real APIs)

### 🏛️ Government & Public Records
- **US Census Bureau**: Demographics, population, income statistics via Census API
- **Federal Reserve (FRED)**: GDP, unemployment, inflation, interest rates
- **SEC EDGAR**: Company filings, financial disclosures from SEC database
- **Bureau of Labor Statistics**: Employment data, wage statistics
- **US Geological Survey**: Earthquake data, geological information

### 🔬 Scientific & Research
- **NASA APIs**: Astronomy Picture of the Day, Earth imagery, asteroid data, Mars rover photos
- **PubMed**: Medical and life science research papers via NCBI E-utilities
- **ArXiv**: Physics, mathematics, computer science preprints
- **wttr.in Weather Service**: Global weather and climate data
- **Open Academic Databases**: Research paper search and discovery

### 💰 Financial Markets
- **Yahoo Finance**: Real-time stock prices, company information
- **CoinGecko**: Cryptocurrency data and market metrics
- **Exchange Rate APIs**: Currency conversion and forex data
- **Economic Indicators**: Market sentiment and economic trends

### 📰 News & Media
- **RSS Feeds**: BBC, Reuters, NPR, CNN, TechCrunch, and 15+ major sources
- **Breaking News**: Real-time news aggregation via RSS parsing
- **News Search**: Topic-based article search across sources
- **Sentiment Analysis**: Keyword-based media sentiment tracking

### 🌍 Geographic & Environmental
- **Weather Data**: wttr.in global weather service
- **Air Quality**: World Air Quality Index (WAQI) API
- **Disaster Alerts**: USGS earthquake feeds, National Weather Service alerts
- **Geographic Information**: Location-based data and statistics

### 💻 Technology & Internet
- **GitHub**: Trending repositories via GitHub API, technology metrics
- **Domain Information**: WHOIS data via python-whois
- **Tech Trends**: Technology adoption and trend analysis
- **Open Source Metrics**: Development statistics and project data

## 🚀 Complete Installation Guide

### Prerequisites

**System Requirements:**
- Python 3.8 or higher
- Git
- Internet connection for API access
- 50MB disk space

**Supported Platforms:**
- Windows 10/11 ✅
- macOS 10.15+ ✅
- Linux (Ubuntu 18.04+, CentOS 7+) ✅

### Step-by-Step Installation

#### Step 1: Clone the Repository

```bash
# Clone from GitHub
git clone https://github.com/inamdarmihir/universal-public-data-mcp-server.git

# Navigate to project directory
cd universal-public-data-mcp-server
```

#### Step 2: Set Up Python Environment

**Option A: Using venv (Recommended)**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

**Option B: Using conda**
```bash
# Create conda environment
conda create -n mcp-server python=3.9
conda activate mcp-server
```

#### Step 3: Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt

# Verify installation
python -c "import mcp; print('✅ MCP installed successfully')"
```

#### Step 4: Test Installation

```bash
# Run the comprehensive demo
python demo.py

# Or run individual tests
python scripts/test_server.py
```

**Expected Demo Output:**
```
🚀 Universal Public Data MCP Server
   COMPREHENSIVE API DEMO
   All implementations use REAL APIs - No mocks!

💰 FINANCIAL DATA APIs
📈 Stock Data (Apple):
   Company: Apple Inc.
   Price: $195.89
   Market Cap: $3,000,000,000,000

🪙 Cryptocurrency Data (Bitcoin):
   Name: Bitcoin
   Price: $67,234.50
   24h Change: 2.45%

💱 Exchange Rates (USD to EUR):
   Rate: 0.92
```

If you see real data like above, your installation is complete! 🎉

## ⚙️ Configuration Guide

### Basic Configuration (Optional)

The server works out-of-the-box with smart defaults, but you can customize:

```bash
# Copy example configuration (optional)
cp config.example.yaml config.yaml
```

```yaml
# config.yaml
server:
  debug: false          # Set to true for detailed logging
  log_level: INFO       # DEBUG, INFO, WARNING, ERROR

cache:
  enabled: true         # Enable caching for better performance
  default_ttl: 300      # Cache timeout in seconds
  max_size: 1000        # Maximum cache entries
  redis_enabled: false  # Redis disabled by default (optional)

rate_limit:
  enabled: true         # Prevent API abuse
  requests_per_minute: 60
  burst_limit: 10

# Optional API keys for enhanced features (most APIs work without keys)
api_keys:
  nasa: ""              # NASA API key (optional, demo key used otherwise)
  github: ""            # GitHub token for higher rate limits (optional)
```

## 🔌 MCP Client Integration

### Cursor IDE Integration (Step-by-Step)

1. **Open Cursor Settings**
   - Press `Ctrl+,` (Windows/Linux) or `Cmd+,` (macOS)
   - Search for "MCP" in settings

2. **Add MCP Server Configuration**

**For Windows:**
```json
{
  "mcpServers": {
    "public-data": {
      "command": "python",
      "args": ["src/server.py"],
      "cwd": "C:\\Users\\YourUsername\\path\\to\\universal-public-data-mcp-server"
    }
  }
}
```

**For macOS/Linux:**
```json
{
  "mcpServers": {
    "public-data": {
      "command": "python",
      "args": ["src/server.py"],
      "cwd": "/Users/YourUsername/path/to/universal-public-data-mcp-server"
    }
  }
}
```

3. **Replace the Path**
   - Replace `C:\\Users\\YourUsername\\path\\to\\universal-public-data-mcp-server` with your actual project path
   - Example: `"C:\\Users\\alex\\Drive\\Documents\\universal-public-data-mcp-server"`

4. **Path Format Guidelines**
   - **Windows**: Use double backslashes `\\` in JSON
   - **Spaces in path**: Keep quotes around the entire path
   - **macOS/Linux**: Use forward slashes `/`

5. **Restart Cursor** for changes to take effect

### Claude Desktop Integration

**Config file location:**
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "public-data": {
      "command": "python",
      "args": ["src/server.py"],
      "cwd": "/path/to/universal-public-data-mcp-server"
    }
  }
}
```

## 🔧 Complete Tool Reference & Examples

### 💰 Financial Tools

#### `get_stock_data` - Real-time Stock Information
```python
# Ask your AI: "What's Apple's current stock price?"
# Response from Yahoo Finance API:
{
  "symbol": "AAPL",
  "company_name": "Apple Inc.",
  "current_price": 195.89,
  "market_cap": 3000000000000,
  "change": 2.45,
  "change_percent": 1.27,
  "volume": 45234567
}
```

#### `get_crypto_data` - Cryptocurrency Data
```python
# Ask: "What's Bitcoin's price and market cap?"
# Response from CoinGecko API:
{
  "name": "Bitcoin",
  "symbol": "btc",
  "current_price": 67234.50,
  "market_cap": 1326789000000,
  "price_change_percentage_24h": 2.45,
  "total_volume": 23456789000
}
```

#### `get_exchange_rates` - Currency Conversion
```python
# Ask: "Convert 100 USD to EUR"
# Response from exchange rate API:
{
  "from_currency": "USD",
  "to_currency": "EUR", 
  "rate": 0.92,
  "amount": 100,
  "converted_amount": 92.00,
  "calculation": "100 USD = 92.00 EUR"
}
```

### 🏛️ Government Data Tools

#### `get_census_data` - US Demographics
```python
# Ask: "What's California's population?"
# Response from US Census Bureau API:
{
  "location": "California",
  "metric": "population",
  "year": 2021,
  "data": {
    "total_population": 39538223
  },
  "source": "US Census Bureau ACS"
}
```

#### `get_economic_indicators` - Federal Reserve Data
```python
# Ask: "What's the current unemployment rate?"
# Response from FRED API:
{
  "indicator": "unemployment",
  "latest_value": 3.7,
  "latest_date": "2024-01-01",
  "change": -0.1,
  "change_percent": -2.63,
  "source": "Federal Reserve Economic Data (FRED)"
}
```

#### `search_sec_filings` - Company Filings
```python
# Ask: "Find recent SEC filings for Tesla"
# Response from SEC EDGAR database:
{
  "company": "Tesla",
  "filings_found": 5,
  "filings": [
    {
      "title": "Tesla Inc - Form 10-K",
      "filing_type": "10-K",
      "date": "2024-01-29",
      "link": "https://www.sec.gov/Archives/edgar/..."
    }
  ]
}
```

### 🔬 Scientific Data Tools

#### `get_nasa_data` - NASA APIs
```python
# Ask: "Show me today's astronomy picture"
# Response from NASA APOD API:
{
  "dataset": "apod",
  "title": "The Heart Nebula",
  "explanation": "What powers the Heart Nebula? The large emission nebula...",
  "url": "https://apod.nasa.gov/apod/image/2401/HeartNebula.jpg",
  "date": "2024-01-15",
  "source": "NASA APOD"
}

# Ask: "Are there any asteroids approaching Earth?"
# Response from NASA NEO API:
{
  "dataset": "asteroids", 
  "element_count": 12,
  "asteroids": [
    {
      "name": "2024 AA1",
      "potentially_hazardous": false,
      "close_approach_date": "2024-01-16",
      "miss_distance_km": "4500000"
    }
  ]
}
```

#### `search_research_papers` - Academic Papers
```python
# Ask: "Find recent papers about machine learning"
# Response from PubMed + ArXiv:
{
  "query": "machine learning",
  "papers_found": 15,
  "papers": [
    {
      "title": "Deep Learning Applications in Medical Imaging",
      "authors": ["Smith, J.", "Johnson, M."],
      "journal": "Nature Medicine",
      "source": "PubMed",
      "url": "https://pubmed.ncbi.nlm.nih.gov/38234567/"
    }
  ]
}
```

#### `get_climate_data` - Weather Information
```python
# Ask: "What's the weather in London?"
# Response from wttr.in API:
{
  "location": "London",
  "weather": {
    "temperature": {
      "celsius": "12",
      "fahrenheit": "54"
    },
    "conditions": {
      "description": "Partly cloudy",
      "humidity": "68",
      "cloud_cover": "50"
    }
  }
}
```

### 📰 News & Media Tools

#### `get_breaking_news` - Latest News
```python
# Ask: "Get the latest tech news"
# Response from RSS feeds (BBC, Reuters, TechCrunch):
{
  "category": "technology",
  "articles_found": 12,
  "articles": [
    {
      "title": "OpenAI Announces GPT-5 Development",
      "description": "OpenAI has confirmed that work on GPT-5 is underway...",
      "source": "TechCrunch",
      "published": "2024-01-15T10:30:00Z",
      "hours_ago": 2.5
    }
  ]
}
```

#### `search_news` - Topic-Based Search
```python
# Ask: "Find news about renewable energy this week"
# Response from multiple RSS sources:
{
  "query": "renewable energy",
  "timeframe": "1w",
  "articles_found": 25,
  "search_summary": {
    "avg_relevance": 0.78,
    "categories_searched": ["general", "business", "technology"]
  }
}
```

#### `analyze_media_sentiment` - Sentiment Analysis
```python
# Ask: "What's the media sentiment about AI recently?"
# Response with keyword-based analysis:
{
  "topic": "artificial intelligence",
  "sentiment": "positive",
  "confidence": 0.72,
  "distribution": {
    "positive": 15,
    "negative": 3,
    "neutral": 7,
    "positive_percentage": 60.0
  }
}
```

### 🌍 Geographic & Environmental Tools

#### `get_weather_data` - Comprehensive Weather
```python
# Ask: "Get the 5-day forecast for Tokyo"
# Response from wttr.in:
{
  "location": "Tokyo",
  "type": "forecast",
  "forecast": [
    {
      "date": "2024-01-16",
      "temperature": {
        "max_celsius": "15",
        "min_celsius": "8"
      },
      "conditions": {
        "sun_hours": "6.2",
        "uv_index": "3"
      }
    }
  ]
}
```

#### `get_air_quality` - Pollution Data
```python
# Ask: "Check air quality in Beijing"
# Response from WAQI API:
{
  "location": "Beijing",
  "air_quality": {
    "aqi": 89,
    "quality_level": "Moderate",
    "health_message": "Air quality is acceptable for most people",
    "dominant_pollutant": "pm25",
    "pollutants": {
      "pm25": {"value": 35, "unit": "μg/m³"}
    }
  }
}
```

#### `get_disaster_alerts` - Natural Disasters
```python
# Ask: "Any earthquake alerts for California?"
# Response from USGS + NWS:
{
  "location": "California",
  "alerts_found": 2,
  "alerts": [
    {
      "type": "earthquake",
      "magnitude": 4.2,
      "location": "Southern California",
      "time": "2024-01-15T14:30:00Z",
      "source": "USGS Earthquake Hazards Program"
    }
  ]
}
```

### 💻 Technology Tools

#### `get_github_trends` - Trending Repositories
```python
# Ask: "What are the trending Python projects this week?"
# Response from GitHub API:
{
  "timeframe": "weekly",
  "language": "python",
  "repositories": [
    {
      "full_name": "microsoft/semantic-kernel",
      "stars": 45230,
      "description": "Integrate cutting-edge LLM technology quickly...",
      "language": "Python",
      "stars_this_period": 1250
    }
  ]
}
```

#### `get_domain_info` - Website Information
```python
# Ask: "Get information about github.com"
# Response with WHOIS + status check:
{
  "domain": "github.com",
  "status": {
    "reachable": true,
    "response_time_ms": 245
  },
  "whois": {
    "registrar": "MarkMonitor Inc.",
    "country": "US",
    "creation_date": "2007-10-09"
  }
}
```

## 💡 Real-World Usage Scenarios

### 📊 Market Research Analysis
```python
# Complex multi-tool research query:
"I need to analyze the electric vehicle market. Can you:
1. Get Tesla's stock performance this month
2. Find recent news about electric vehicles
3. Check government EV incentive data
4. Analyze sentiment around EV adoption"

# This automatically triggers:
# - get_stock_data(symbol="TSLA", period="1mo")
# - search_news(query="electric vehicles", timeframe="1m")  
# - get_census_data(location="United States", metric="transportation")
# - analyze_media_sentiment(topic="electric vehicle adoption", timeframe="1w")

# You get comprehensive, real data from 4 different sources!
```

### 🌡️ Climate Research
```python
"Help me understand climate change impacts by checking:
- Current weather patterns in major cities
- Recent climate research papers
- Government climate data  
- News coverage of climate issues"

# Triggers multiple real APIs:
# - get_weather_data() for multiple cities
# - search_research_papers(query="climate change", recent=True)
# - get_economic_indicators(indicator="environmental")
# - search_news(query="climate change", timeframe="1w")
```

### 💼 Economic Analysis
```python
"Analyze current US economic conditions:
- Latest unemployment and inflation rates
- Stock market performance
- Recent economic news sentiment
- Federal Reserve policy updates"

# Real economic data from:
# - Federal Reserve FRED API
# - Yahoo Finance
# - Major news RSS feeds
# - SEC filings
```

## 🧪 Testing & Validation

### Quick Validation

```bash
# Test all systems with demo
python demo.py

# Expected output shows real data:
# ✅ Apple stock: $195.89
# ✅ Bitcoin price: $67,234.50  
# ✅ California population: 39,538,223
# ✅ NASA APOD: "The Heart Nebula"
# ✅ BBC breaking news: 15 articles
# ✅ London weather: 12°C, partly cloudy
```

### Individual Tool Testing

```bash
# Test specific adapters
python -c "
import asyncio
from src.adapters.financial import FinancialDataAdapter
from src.core.cache import CacheManager
from src.core.config import Config

async def test():
    config = Config.load()
    cache = CacheManager(config)
    async with FinancialDataAdapter(cache) as adapter:
        result = await adapter.get_stock_data('AAPL')
        print(f'✅ Apple Stock: ${result.get(\"current_price\")}')

asyncio.run(test())
"
```

### Cache Performance Testing

```bash
# Test cache performance
python -c "
import asyncio
import time
from src.adapters.news import NewsDataAdapter
from src.core.cache import CacheManager
from src.core.config import Config

async def benchmark():
    config = Config.load()
    cache = CacheManager(config)
    
    async with NewsDataAdapter(cache) as adapter:
        # First call (no cache)
        start = time.time()
        await adapter.get_breaking_news('technology', 5)
        first_call = time.time() - start
        
        # Second call (cached)
        start = time.time()
        await adapter.get_breaking_news('technology', 5)
        cached_call = time.time() - start
        
        print(f'First call: {first_call:.2f}s')
        print(f'Cached call: {cached_call:.2f}s')
        print(f'Cache speedup: {first_call/cached_call:.1f}x')

asyncio.run(benchmark())
"
```

## 🔧 Troubleshooting Guide

### Common Issues & Solutions

#### ❌ "ModuleNotFoundError: No module named 'mcp'"
```bash
# Solution: Install dependencies
pip install -r requirements.txt

# Or install MCP specifically:
pip install mcp>=1.0.0
```

#### ❌ MCP client can't connect to server
**Check these steps:**

1. **Verify project path in MCP config**
```json
{
  "mcpServers": {
    "public-data": {
      "cwd": "C:\\ACTUAL\\PATH\\TO\\YOUR\\PROJECT"  // ← This must be correct!
    }
  }
}
```

2. **Test server manually**
```bash
cd /path/to/project
python src/server.py
# Should start without errors
```

3. **Check Python path**
```bash
which python  # Unix
where python  # Windows
# Make sure this matches the "command" in MCP config
```

#### ❌ "Rate limit exceeded" errors
```yaml
# Reduce rate limits in config.yaml
rate_limit:
  requests_per_minute: 30  # Lower from 60
  burst_limit: 5           # Lower from 10
```

#### ❌ Slow API responses
```yaml
# Enable caching for faster responses
cache:
  enabled: true
  default_ttl: 600      # 10 minutes
  max_size: 2000        # More cache entries
```

#### ❌ API timeout errors
```bash
# Check internet connection:
curl "https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY"

# Should return JSON data, not timeout
```

### Debug Mode

Enable detailed logging:
```yaml
# config.yaml
server:
  debug: true
  log_level: DEBUG
```

Or use environment variable:
```bash
export DEBUG=true
python src/server.py
```

### Performance Optimization

**For High-Volume Usage:**
```yaml
cache:
  enabled: true
  redis_enabled: true
  redis_url: "redis://localhost:6379/0"
  default_ttl: 1800
  max_size: 5000

rate_limit:
  requests_per_minute: 120
  burst_limit: 30
```

**For Development:**
```yaml
server:
  debug: true
  log_level: DEBUG

cache:
  enabled: false  # Disable for real-time testing

rate_limit:
  enabled: false  # No limits during development
```

## ❓ FAQ

### **Q: Are these real APIs or mock data?**
**A**: 100% real APIs! This server connects to live data sources:
- Yahoo Finance for stocks
- CoinGecko for crypto
- US Census Bureau for demographics  
- NASA for space data
- BBC/Reuters/CNN for news
- USGS for earthquakes
- And 15+ more real sources

### **Q: Do I need API keys?**
**A**: No! The server is designed to work with public APIs that don't require authentication. Optional API keys only enhance rate limits or add features.

### **Q: How current is the data?**
**A**: Varies by source:
- **Financial**: Real-time to 15-minute delay
- **News**: Updated every few minutes via RSS
- **Weather**: Updated hourly
- **Government**: Monthly to yearly updates
- **NASA**: Daily updates

### **Q: Can I use this in production?**
**A**: Yes! Features included:
- ✅ Caching and rate limiting
- ✅ Error handling and graceful degradation  
- ✅ Structured logging
- ✅ Configuration management
- ✅ Performance optimization

### **Q: What if an API goes down?**
**A**: The server handles this gracefully:
```json
{
  "error": "API temporarily unavailable",
  "fallback_data": "cached_result_if_available",
  "retry_after": "300 seconds",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### **Q: How do I add my own data source?**
**A**: Create a new adapter:
```python
# src/adapters/my_adapter.py
class MyDataAdapter:
    async def my_tool(self, param: str) -> Dict[str, Any]:
        # Your implementation
        return {"result": "data"}

# Register in src/server.py
# Add tests in tests/
```

### **Q: Can I run this on a server/cloud?**
**A**: Yes! Deploy anywhere Python runs:
- AWS Lambda
- Google Cloud Functions  
- Heroku
- DigitalOcean
- Your own server

### **Q: Is my data private?**
**A**: Yes:
- Server only accesses public APIs
- No personal data stored
- No query logging to external services
- All processing is local

## 🚀 Advanced Configuration

### Production Deployment

**High-Performance Setup:**
```yaml
# Production config
server:
  debug: false
  log_level: WARNING

cache:
  enabled: true
  redis_enabled: true
  redis_url: "redis://prod-redis:6379/0"
  default_ttl: 3600
  max_size: 10000

rate_limit:
  requests_per_minute: 300
  burst_limit: 50

# Production API keys for higher limits
api_keys:
  nasa: "your_nasa_key_here"
  github: "your_github_token_here"
```

**Monitoring Setup:**
```yaml
# Add monitoring
server:
  metrics_enabled: true
  health_check_endpoint: true
  
logging:
  level: INFO
  format: json
  file: /var/log/mcp-server.log
```

### Multi-Instance Deployment

**Load Balancer Config:**
```yaml
# Instance 1
cache:
  redis_url: "redis://shared-redis:6379/1"

# Instance 2  
cache:
  redis_url: "redis://shared-redis:6379/2"
```

**Docker Deployment:**
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src/
COPY config.yaml .

CMD ["python", "src/server.py"]
```

## 🎯 Integration Examples

### Jupyter Notebook Integration

```python
# Use MCP server data in Jupyter analysis
import pandas as pd
import matplotlib.pyplot as plt
import requests

# Query local MCP server
response = requests.post('http://localhost:3000/mcp', json={
    "method": "get_economic_indicators", 
    "params": {"indicator": "unemployment", "timeframe": "2y"}
})

data = response.json()
df = pd.DataFrame(data['time_series'])
df['date'] = pd.to_datetime(df['date'])

# Plot unemployment trend
plt.figure(figsize=(12, 6))
plt.plot(df['date'], df['value'])
plt.title('US Unemployment Rate - 2 Year Trend')
plt.ylabel('Unemployment Rate (%)')
plt.xticks(rotation=45)
plt.grid(True)
plt.show()
```

### Custom Analysis Scripts

```python
# Market correlation analysis using MCP data
import asyncio
from src.adapters.financial import FinancialDataAdapter
from src.adapters.news import NewsDataAdapter
from src.core.cache import CacheManager
from src.core.config import Config

async def market_sentiment_analysis():
    config = Config.load()
    cache = CacheManager(config)
    
    # Get stock data
    async with FinancialDataAdapter(cache) as financial:
        tesla_data = await financial.get_stock_data("TSLA")
        
    # Get news sentiment
    async with NewsDataAdapter(cache) as news:
        ev_sentiment = await news.analyze_media_sentiment("electric vehicles", "1w")
    
    # Analyze correlation
    stock_change = tesla_data.get('change_percent', 0)
    news_sentiment = ev_sentiment.get('sentiment_score', 0)
    
    print(f"Tesla stock change: {stock_change}%")
    print(f"EV news sentiment: {news_sentiment}")
    print(f"Correlation strength: {abs(stock_change * news_sentiment)}")

# Run analysis
asyncio.run(market_sentiment_analysis())
```

## 🤝 Contributing

We welcome contributions! This server is designed to be the definitive public data access layer for AI applications.

### Development Setup
```bash
# Fork and clone
git clone https://github.com/YOUR_USERNAME/universal-public-data-mcp-server.git
cd universal-public-data-mcp-server

# Install development dependencies
pip install -e .
pip install pytest black isort mypy pre-commit

# Set up pre-commit hooks
pre-commit install

# Run tests
pytest tests/ -v

# Format code
black src/
isort src/

# Type checking
mypy src/
```

### Adding New Data Sources

1. **Create adapter**: `src/adapters/my_new_source.py`
2. **Add tools**: Register in `src/server.py`
3. **Write tests**: `tests/test_my_new_source.py`
4. **Update docs**: Add to this README

### Priority Data Sources Needed
- 🌍 International economic data (World Bank, IMF)
- 📚 Academic institutional data
- 📝 Open patent databases  
- 🎨 Cultural and arts databases
- ⚽ Sports statistics APIs
- 🚌 Public transportation data
- 🏥 Healthcare statistics
- 🏢 Real estate market data

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🌐 Links & Resources

- **GitHub Repository**: [universal-public-data-mcp-server](https://github.com/inamdarmihir/universal-public-data-mcp-server)
- **Issues**: [Report bugs or request features](https://github.com/inamdarmihir/universal-public-data-mcp-server/issues)
- **Discussions**: [Community discussions](https://github.com/inamdarmihir/universal-public-data-mcp-server/discussions)
- **MCP Specification**: [Model Context Protocol](https://spec.modelcontextprotocol.io/)
- **Python MCP SDK**: [Official SDK](https://github.com/modelcontextprotocol/python-sdk)

---

**🎉 Made with ❤️ for the AI and open data community**

*"Democratizing access to public data for AI applications - one real API at a time"*

> **Star ⭐ this repository** if you find it useful! It helps others discover this comprehensive MCP server. 
