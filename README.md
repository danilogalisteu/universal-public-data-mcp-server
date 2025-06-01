# Universal Public Data MCP Server

A production-ready Model Context Protocol (MCP) server providing unified access to multiple public data sources. Designed for enterprise deployment with comprehensive monitoring, caching, and resilience features.

## Features

### Enterprise-Grade Reliability
- **Circuit Breakers**: Automatic failure detection and recovery
- **Intelligent Caching**: Multi-tier caching with Redis support
- **Retry Logic**: Exponential backoff for failed requests
- **Health Monitoring**: Real-time system health and performance metrics

### Data Sources
- **Government**: US Census, Federal Reserve, SEC filings, USGS
- **Scientific**: NASA APIs, PubMed, ArXiv, NOAA weather
- **Financial**: Yahoo Finance, CoinGecko, exchange rates  
- **News**: RSS feeds from major sources, sentiment analysis
- **Geographic**: Weather data, air quality, disaster alerts
- **Technology**: GitHub trends, domain information

### Quality Assurance
- **Data Validation**: Comprehensive quality scoring
- **Format Standardization**: Consistent data structures
- **Real-time Streaming**: Live data feeds for dynamic content

## Installation

```bash
git clone https://github.com/inamdarmihir/universal-public-data-mcp-server.git
cd universal-public-data-mcp-server

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
python demo.py  # Verify installation
```

## MCP Client Configuration

### Cursor IDE
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

### Claude Desktop
Config location: `~/.config/claude/claude_desktop_config.json`
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

## Available Tools

| Category | Tools | Description |
|----------|-------|-------------|
| **Financial** | `get_stock_data`, `get_crypto_data`, `get_exchange_rates` | Real-time market data |
| **Government** | `get_census_data`, `get_economic_indicators`, `search_sec_filings` | Official government statistics |
| **Scientific** | `get_nasa_data`, `search_research_papers`, `get_climate_data` | Research and space data |
| **News** | `get_breaking_news`, `search_news`, `analyze_media_sentiment` | News aggregation and analysis |
| **Geographic** | `get_weather_data`, `get_air_quality`, `get_disaster_alerts` | Location-based information |
| **Technology** | `get_github_trends`, `get_domain_info`, `analyze_tech_trends` | Tech metrics and trends |
| **Monitoring** | `get_system_status`, `get_api_metrics`, `get_cache_stats` | System performance |

## Configuration

```yaml
# config.yaml (optional)
server:
  debug: false
  log_level: INFO

cache:
  enabled: true
  default_ttl: 300
  redis_enabled: false

rate_limit:
  enabled: true
  requests_per_minute: 60

api_keys:  # Optional for enhanced limits
  nasa: ""
  github: ""
```

## Production Deployment

### High-Performance Setup
```yaml
cache:
  enabled: true
  redis_enabled: true
  redis_url: "redis://localhost:6379/0"
  default_ttl: 3600

rate_limit:
  requests_per_minute: 300
```

### Docker
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src/ ./src/
CMD ["python", "src/server.py"]
```

## Development

### Project Structure
```
src/
├── adapters/          # Data source implementations
├── core/             # Core functionality
│   ├── cache.py      # Caching system
│   ├── monitoring.py # System monitoring  
│   ├── resilience.py # Circuit breakers
│   └── quality.py    # Data validation
└── server.py         # MCP server main
```

### Adding Data Sources
1. Create adapter in `src/adapters/`
2. Register tools in `src/server.py`
3. Add tests in `tests/`

### Testing
```bash
python -m pytest tests/ -v
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) for details.

---

**Links**: [Repository](https://github.com/inamdarmihir/universal-public-data-mcp-server) | [Issues](https://github.com/inamdarmihir/universal-public-data-mcp-server/issues) | [MCP Specification](https://spec.modelcontextprotocol.io/) 