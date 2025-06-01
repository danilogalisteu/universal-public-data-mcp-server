# Universal Public Data MCP Server

A comprehensive Model Context Protocol (MCP) server that provides unified access to multiple public data sources through a single interface. This server aggregates data from government APIs, scientific databases, financial markets, news sources, and more - all accessible to any MCP-compatible LLM or AI application.

## 🌟 Why This MCP Server?

While existing MCP servers focus on specific tools (GitHub, Slack, databases), there's been no unified solution for accessing the wealth of **public open data** available on the internet. This server fills that gap by providing:

- **One Interface, Many Sources**: Access dozens of public APIs through standardized MCP tools
- **No API Keys Required**: Focus on truly public data sources that don't require authentication
- **Production Ready**: Built with caching, rate limiting, and error handling
- **AI-Optimized**: Data is structured and formatted specifically for LLM consumption
- **Extensible**: Easy to add new public data sources

## 📊 Supported Data Sources

### Government & Public Records
- US Census Bureau data
- Bureau of Labor Statistics (unemployment, inflation)
- Federal Reserve economic data (FRED)
- SEC filings and company data
- US Geological Survey data

### Scientific & Research
- NASA APIs (astronomy, earth science, satellite imagery)
- NOAA weather and climate data
- PubMed research papers
- ArXiv scientific papers
- Open academic datasets

### Financial Markets
- Real-time stock prices (Alpha Vantage free tier)
- Cryptocurrency data (CoinGecko)
- Currency exchange rates
- Economic indicators
- Market sentiment data

### News & Media
- RSS feed aggregation
- Breaking news alerts
- Social media trends (public APIs)
- Press releases
- Media sentiment analysis

### Geographic & Environmental
- OpenStreetMap data
- Global weather data
- Air quality measurements
- Natural disaster alerts
- Geographic statistics

### Technology & Internet
- Domain WHOIS data
- Internet traffic statistics
- GitHub trending repositories
- Technology trend analysis
- Open source project metrics

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/your-org/universal-public-data-mcp
cd universal-public-data-mcp

# Install dependencies
pip install -r requirements.txt

# Run the server
python src/server.py
```

### Configuration for MCP Clients

#### Claude Desktop
Add to your MCP settings:

```json
{
  "mcpServers": {
    "public-data": {
      "command": "python",
      "args": ["src/server.py"],
      "cwd": "/path/to/universal-public-data-mcp"
    }
  }
}
```

#### Cursor/Windsurf
Add to your MCP configuration:

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

> **⚠️ Important**: Replace the `cwd` path with your actual project directory:
> - Windows: Use double backslashes `\\` (e.g., `"C:\\Users\\mihir\\OneDrive\\Documents\\New folder"`)
> - macOS/Linux: Use forward slashes `/` (e.g., `"/home/username/projects/universal-public-data-mcp-server"`)
> - Ensure `python` is in your PATH or use the full path to your Python interpreter

## 🔧 Available Tools

### Government Data Tools
- `get_census_data` - Access US Census demographics
- `get_economic_indicators` - Federal Reserve economic data
- `get_labor_statistics` - Employment and wage data
- `search_sec_filings` - Public company filings

### Scientific Data Tools
- `get_nasa_data` - NASA APIs for space and earth science
- `search_research_papers` - Academic paper search
- `get_climate_data` - NOAA climate and weather data
- `get_geological_data` - USGS earthquake and geological info

### Financial Tools
- `get_stock_data` - Real-time stock prices and info
- `get_crypto_data` - Cryptocurrency prices and metrics
- `get_exchange_rates` - Currency conversion rates
- `get_market_sentiment` - Market sentiment indicators

### News & Media Tools
- `get_breaking_news` - Latest news from multiple sources
- `search_news` - Search news articles by topic
- `get_rss_feeds` - Access RSS feeds from major outlets
- `analyze_media_sentiment` - Sentiment analysis of news

### Geographic Tools
- `get_location_data` - Geographic information for locations
- `get_weather_data` - Current and forecast weather
- `get_air_quality` - Air quality measurements
- `get_disaster_alerts` - Natural disaster information

### Technology Tools
- `get_domain_info` - WHOIS and domain information
- `get_github_trends` - Trending repositories and topics
- `get_tech_metrics` - Internet and technology statistics
- `analyze_tech_trends` - Technology trend analysis

## 💡 Example Usage

### Getting Economic Data
```python
# Through MCP, you could ask:
# "What's the current unemployment rate in the US?"
# This would trigger: get_labor_statistics(metric="unemployment_rate")
```

### Research Analysis
```python
# "Find recent papers about climate change impacts"
# This would trigger: search_research_papers(query="climate change impacts", recent=True)
```

### Market Analysis
```python
# "What's Tesla's stock performance today?"
# This would trigger: get_stock_data(symbol="TSLA", timeframe="1d")
```

### News Monitoring
```python
# "Get breaking news about artificial intelligence"
# This would trigger: search_news(query="artificial intelligence", category="breaking")
```

## 🏗️ Architecture

```
MCP Client (LLM/IDE)
        ↓
Universal Public Data MCP Server
        ↓
┌─────────────────────────────────┐
│  Data Source Adapters           │
├─────────────────────────────────┤
│ • Government APIs               │
│ • Scientific Databases         │
│ • Financial Data Providers     │
│ • News & Media APIs            │
│ • Geographic Services          │
│ • Technology Metrics          │
└─────────────────────────────────┘
        ↓
    Public APIs & Data Sources
```

## 🛡️ Features

### Caching & Performance
- Intelligent caching to respect rate limits
- Background data refresh for frequently accessed data
- Response time optimization for LLM usage

### Error Handling
- Graceful degradation when APIs are unavailable
- Comprehensive error messages
- Fallback data sources

### Data Quality
- Data validation and cleaning
- Consistent formatting across sources
- Metadata about data freshness and reliability

### Privacy & Ethics
- Only accesses publicly available data
- No personal information collection
- Respects robots.txt and API terms of service

## 🔍 Advanced Features

### Smart Data Fusion
Combines data from multiple sources for richer insights:
- Cross-reference economic data with news sentiment
- Correlate weather data with agricultural reports
- Link scientific discoveries with market reactions

### Trend Analysis
Built-in trend detection and analysis:
- Identify emerging topics in news
- Track changes in economic indicators
- Monitor scientific research trends

### Custom Queries
Flexible query system that allows:
- Complex multi-source data requests
- Time-based analysis
- Geographic filtering
- Topic-based clustering

## 🤝 Contributing

We welcome contributions! This MCP server is designed to be the definitive public data access layer for AI applications.

### Adding New Data Sources
1. Create an adapter in `src/adapters/`
2. Register tools in `src/tools/`
3. Add tests in `tests/`
4. Update documentation

### Priority Data Sources Needed
- International economic data (World Bank, IMF)
- Academic institutional data
- Open patent databases
- Cultural and arts databases
- Sports statistics APIs
- Public transportation data

## 📚 Documentation

- [Full API Documentation](docs/api.md)
- [Adding Data Sources](docs/adding-sources.md)
- [Deployment Guide](docs/deployment.md)
- [Performance Tuning](docs/performance.md)

## 🔗 Related Projects

- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Claude MCP Examples](https://github.com/anthropics/anthropic-quickstarts)

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🌐 Community

- **Discord**: [Join our MCP community](https://discord.gg/mcp-public-data)
- **Issues**: [Report bugs or request features](https://github.com/your-org/universal-public-data-mcp/issues)
- **Discussions**: [Community discussions](https://github.com/your-org/universal-public-data-mcp/discussions)

---

**Made with ❤️ for the AI and open data community** 