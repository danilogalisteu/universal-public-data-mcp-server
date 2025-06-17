#!/usr/bin/env python3
"""
Universal Public Data MCP Server

A comprehensive Model Context Protocol server that provides unified access
to multiple public data sources including government data, scientific databases,
financial markets, news sources, and more.
"""

import asyncio
import json
import logging
import sys
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

# Set proper encoding for Windows console
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import structlog
from mcp.server import Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

from adapters.government import GovernmentDataAdapter
from adapters.scientific import ScientificDataAdapter
from adapters.financial import FinancialDataAdapter
from adapters.news import NewsDataAdapter
from adapters.geographic import GeographicDataAdapter
from adapters.technology import TechnologyDataAdapter
from core.cache import CacheManager
from core.config import Config

# Try to import enhanced monitoring - fallback gracefully if not available
try:
    from core.monitoring import MetricsCollector, HealthMonitor, DashboardGenerator
    monitoring_available = True
except ImportError:
    monitoring_available = False
    # Create simple fallback classes
    class MetricsCollector:
        def record_request(self, api_name, duration, success): pass
        def get_api_metrics(self): return {}
    
    class HealthMonitor:
        def __init__(self, metrics_collector=None): 
            self.metrics_collector = metrics_collector
        async def check_health(self): return {"status": "ok"}
    
    class DashboardGenerator:
        def __init__(self, metrics_collector, health_monitor): 
            self.metrics = metrics_collector
            self.health = health_monitor
        async def generate_dashboard(self): return {"status": "monitoring not available"}

# Configure logging to stderr for MCP compatibility  
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    stream=sys.stderr
)

logger = logging.getLogger(__name__)

# Create the MCP server instance
server = Server("universal-public-data")

class UniversalPublicDataServer:
    """Main MCP server class that provides access to multiple public data sources."""
    
    def __init__(self):
        """Initialize the MCP server with lazy-loaded adapters for fast startup."""
        logger.info("Starting Universal Public Data MCP Server initialization...")
        
        # Load configuration
        self.config = Config.load()
        logger.info("Configuration loaded successfully")
        
        # Initialize cache manager (lightweight)
        self.cache = CacheManager(self.config)
        logger.info("Cache manager initialized")
        
        # Initialize monitoring components (lightweight)
        self.metrics = MetricsCollector()
        self.health_monitor = HealthMonitor(self.metrics)
        self.dashboard_generator = DashboardGenerator(self.metrics, self.health_monitor)
        logger.info("Monitoring components initialized")
        
        # Initialize adapters lazily (don't create HTTP clients yet)
        self._adapters_initialized = False
        self.government = None
        self.scientific = None
        self.financial = None
        self.news = None
        self.geographic = None
        self.technology = None
        
        logger.info("Universal Public Data MCP Server initialized successfully", 
                   extra={"monitoring_available": monitoring_available})

    def _ensure_adapters_initialized(self):
        """Initialize adapters only when first needed (lazy initialization)."""
        if not self._adapters_initialized:
            logger.info("Initializing data adapters...")
            self.government = GovernmentDataAdapter(self.cache)
            self.scientific = ScientificDataAdapter(self.cache)
            self.financial = FinancialDataAdapter(self.cache)
            self.news = NewsDataAdapter(self.cache)
            self.geographic = GeographicDataAdapter(self.cache)
            self.technology = TechnologyDataAdapter(self.cache)
            self._adapters_initialized = True
            logger.info("All data adapters initialized")

# Create the server instance
server_instance = UniversalPublicDataServer()

# Register tools with the global server
@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """List all available tools."""
    logger.info("Tools list requested")
    tools = []
    
    # Government tools
    tools.extend([
        types.Tool(
            name="get_census_data",
            description="Get demographic data from US Census Bureau",
            inputSchema={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "State, county, or city name"
                    },
                    "metric": {
                        "type": "string",
                        "description": "Census metric (population, income, education, etc.)",
                        "enum": ["population", "median_income", "education", "housing", "demographics"]
                    },
                    "year": {
                        "type": "integer",
                        "description": "Year for data (default: latest available)"
                    }
                },
                "required": ["location", "metric"]
            }
        ),
        types.Tool(
            name="get_economic_indicators",
            description="Get economic data from Federal Reserve (FRED)",
            inputSchema={
                "type": "object",
                "properties": {
                    "indicator": {
                        "type": "string",
                        "description": "Economic indicator",
                        "enum": ["gdp", "inflation", "unemployment", "interest_rates", "consumer_spending"]
                    },
                    "timeframe": {
                        "type": "string",
                        "description": "Time period",
                        "enum": ["1m", "3m", "6m", "1y", "5y"]
                    }
                },
                "required": ["indicator"]
            }
        ),
        types.Tool(
            name="search_sec_filings",
            description="Search SEC filings for public companies",
            inputSchema={
                "type": "object",
                "properties": {
                    "company": {
                        "type": "string",
                        "description": "Company name or ticker symbol"
                    },
                    "filing_type": {
                        "type": "string",
                        "description": "Type of SEC filing",
                        "enum": ["10-K", "10-Q", "8-K", "DEF 14A", "S-1"]
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of results to return",
                        "default": 10
                    }
                },
                "required": ["company"]
            }
        )
    ])
    
    # Scientific tools
    tools.extend([
        types.Tool(
            name="get_nasa_data",
            description="Access NASA APIs for space and earth science data",
            inputSchema={
                "type": "object",
                "properties": {
                    "dataset": {
                        "type": "string",
                        "description": "NASA dataset",
                        "enum": ["apod", "earth", "mars_rover", "asteroids", "exoplanets", "solar_flares"]
                    },
                    "date": {
                        "type": "string",
                        "description": "Date for data (YYYY-MM-DD format)"
                    },
                    "location": {
                        "type": "object",
                        "description": "Geographic coordinates for Earth data",
                        "properties": {
                            "lat": {"type": "number"},
                            "lon": {"type": "number"}
                        }
                    }
                },
                "required": ["dataset"]
            }
        ),
        types.Tool(
            name="search_research_papers",
            description="Search academic papers from PubMed and ArXiv",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for papers"
                    },
                    "source": {
                        "type": "string",
                        "description": "Paper database",
                        "enum": ["pubmed", "arxiv", "both"],
                        "default": "both"
                    },
                    "recent": {
                        "type": "boolean",
                        "description": "Only return recent papers (last 6 months)",
                        "default": False
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of papers to return",
                        "default": 10
                    }
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="get_climate_data",
            description="Get climate and weather data from NOAA",
            inputSchema={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City, state, or coordinates"
                    },
                    "metric": {
                        "type": "string",
                        "description": "Climate metric",
                        "enum": ["temperature", "precipitation", "humidity", "pressure", "wind"]
                    },
                    "timeframe": {
                        "type": "string",
                        "description": "Time period",
                        "enum": ["current", "forecast", "historical"],
                        "default": "current"
                    }
                },
                "required": ["location", "metric"]
            }
        )
    ])
    
    # Financial tools
    tools.extend([
        types.Tool(
            name="get_stock_data",
            description="Get real-time stock data and financial metrics",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock ticker symbol (e.g., AAPL, TSLA)"
                    },
                    "timeframe": {
                        "type": "string",
                        "description": "Time period for data",
                        "enum": ["1d", "5d", "1mo", "3mo", "6mo", "1y", "5y"],
                        "default": "1d"
                    },
                    "metrics": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["price", "volume", "market_cap", "pe_ratio", "dividend_yield", "52w_high", "52w_low"]
                        },
                        "description": "Specific metrics to return"
                    }
                },
                "required": ["symbol"]
            }
        ),
        types.Tool(
            name="get_crypto_data",
            description="Get cryptocurrency prices and market data",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Crypto symbol (e.g., BTC, ETH)"
                    },
                    "currency": {
                        "type": "string",
                        "description": "Base currency for prices",
                        "default": "USD"
                    },
                    "include_market_data": {
                        "type": "boolean",
                        "description": "Include market cap, volume, etc.",
                        "default": True
                    }
                },
                "required": ["symbol"]
            }
        ),
        types.Tool(
            name="get_exchange_rates",
            description="Get current currency exchange rates",
            inputSchema={
                "type": "object",
                "properties": {
                    "from_currency": {
                        "type": "string",
                        "description": "Source currency code (e.g., USD)"
                    },
                    "to_currency": {
                        "type": "string",
                        "description": "Target currency code (e.g., EUR)"
                    },
                    "amount": {
                        "type": "number",
                        "description": "Amount to convert",
                        "default": 1
                    }
                },
                "required": ["from_currency", "to_currency"]
            }
        )
    ])
    
    # News and media tools
    tools.extend([
        types.Tool(
            name="get_breaking_news",
            description="Get latest breaking news from multiple sources",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "News category",
                        "enum": ["general", "business", "technology", "science", "health", "sports"],
                        "default": "general"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of articles to return",
                        "default": 10
                    },
                    "language": {
                        "type": "string",
                        "description": "Language for news",
                        "default": "en"
                    }
                }
            }
        ),
        types.Tool(
            name="search_news",
            description="Search news articles by topic or keyword",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for news articles"
                    },
                    "timeframe": {
                        "type": "string",
                        "description": "Time period for search",
                        "enum": ["1h", "6h", "24h", "3d", "1w", "1m"],
                        "default": "24h"
                    },
                    "sources": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Specific news sources to search"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of articles to return",
                        "default": 15
                    }
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="analyze_media_sentiment",
            description="Analyze sentiment of news articles about a topic",
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "Topic to analyze sentiment for"
                    },
                    "timeframe": {
                        "type": "string",
                        "description": "Time period for analysis",
                        "enum": ["24h", "3d", "1w", "1m"],
                        "default": "24h"
                    }
                },
                "required": ["topic"]
            }
        )
    ])
    
    # Geographic and environmental tools
    tools.extend([
        types.Tool(
            name="get_weather_data",
            description="Get current weather and forecasts",
            inputSchema={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City, state, or coordinates"
                    },
                    "type": {
                        "type": "string",
                        "description": "Type of weather data",
                        "enum": ["current", "forecast", "historical"],
                        "default": "current"
                    },
                    "units": {
                        "type": "string",
                        "description": "Temperature units",
                        "enum": ["metric", "imperial"],
                        "default": "metric"
                    }
                },
                "required": ["location"]
            }
        ),
        types.Tool(
            name="get_air_quality",
            description="Get air quality measurements for a location",
            inputSchema={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City, state, or coordinates"
                    },
                    "pollutants": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["pm25", "pm10", "o3", "no2", "so2", "co"]
                        },
                        "description": "Specific pollutants to check"
                    }
                },
                "required": ["location"]
            }
        ),
        types.Tool(
            name="get_disaster_alerts",
            description="Get natural disaster alerts and warnings",
            inputSchema={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "State, region, or country"
                    },
                    "disaster_types": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["earthquake", "hurricane", "tornado", "flood", "wildfire", "tsunami"]
                        },
                        "description": "Types of disasters to check for"
                    }
                },
                "required": ["location"]
            }
        )
    ])
    
    # Technology tools
    tools.extend([
        types.Tool(
            name="get_github_trends",
            description="Get trending repositories and topics on GitHub",
            inputSchema={
                "type": "object",
                "properties": {
                    "timeframe": {
                        "type": "string",
                        "description": "Trending timeframe",
                        "enum": ["daily", "weekly", "monthly"],
                        "default": "daily"
                    },
                    "language": {
                        "type": "string",
                        "description": "Programming language filter"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of repositories to return",
                        "default": 25
                    }
                }
            }
        ),
        types.Tool(
            name="get_domain_info",
            description="Get WHOIS and domain information",
            inputSchema={
                "type": "object",
                "properties": {
                    "domain": {
                        "type": "string",
                        "description": "Domain name to lookup"
                    },
                    "include_dns": {
                        "type": "boolean",
                        "description": "Include DNS record information",
                        "default": False
                    }
                },
                "required": ["domain"]
            }
        ),
        types.Tool(
            name="analyze_tech_trends",
            description="Analyze technology trends and adoption metrics",
            inputSchema={
                "type": "object",
                "properties": {
                    "technology": {
                        "type": "string",
                        "description": "Technology or framework to analyze"
                    },
                    "metrics": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["github_stars", "npm_downloads", "job_postings", "stackoverflow_questions", "google_trends"]
                        },
                        "description": "Metrics to include in analysis"
                    },
                    "timeframe": {
                        "type": "string",
                        "description": "Analysis timeframe",
                        "enum": ["1m", "3m", "6m", "1y", "2y"],
                        "default": "6m"
                    }
                },
                "required": ["technology"]
            }
        )
    ])
    
    # System monitoring tools
    tools.extend([
        types.Tool(
            name="get_system_status",
            description="Get comprehensive system health and performance metrics",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            },
        ),
        types.Tool(
            name="get_api_metrics",
            description="Get detailed metrics for API performance and usage",
            inputSchema={
                "type": "object",
                "properties": {
                    "api_name": {
                        "type": "string",
                        "description": "Specific API to get metrics for (optional)"
                    }
                },
                "required": []
            },
        ),
        types.Tool(
            name="get_cache_stats",
            description="Get cache performance statistics and hit ratios",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            },
        ),
    ])
    
    return tools

# Tool implementation
@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle tool calls by routing to appropriate adapters."""
    start_time = time.time()
    
    try:
        logger.info(f"Tool called: {name} with args: {arguments}")
        
        # Ensure adapters are initialized before first use (lazy loading)
        server_instance._ensure_adapters_initialized()
        
        result = None
        
        # Route monitoring tools (these don't need adapters)
        if name == "get_system_status":
            dashboard_data = await server_instance.dashboard_generator.generate_dashboard()
            server_instance.metrics.record_request("system_monitoring", time.time() - start_time, True)
            
            return [types.TextContent(
                type="text",
                text=json.dumps(dashboard_data, indent=2, default=str)
            )]
        
        elif name == "get_api_metrics":
            api_name = arguments.get("api_name")
            
            if api_name:
                api_metrics = server_instance.metrics.get_api_metrics()
                if api_name in api_metrics:
                    result = {api_name: api_metrics[api_name]}
                else:
                    result = {"error": f"No metrics found for API: {api_name}"}
            else:
                result = server_instance.metrics.get_api_metrics()
            
            result["timestamp"] = datetime.now().isoformat()
            server_instance.metrics.record_request("api_metrics", time.time() - start_time, True)
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2, default=str)
            )]
        
        elif name == "get_cache_stats":
            cache_stats = await server_instance.cache.get_cache_stats()
            hit_ratio = await server_instance.cache.get_hit_ratio()
            
            result = {
                "cache_stats": cache_stats,
                "hit_ratio": hit_ratio,
                "hit_ratio_percent": hit_ratio * 100,
                "timestamp": datetime.now().isoformat()
            }
            
            server_instance.metrics.record_request("cache_stats", time.time() - start_time, True)
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2, default=str)
            )]
        
        # Government data tools
        if name == "get_census_data":
            result = await server_instance.government.get_census_data(**arguments)
        elif name == "get_economic_indicators":
            result = await server_instance.government.get_economic_indicators(**arguments)
        elif name == "search_sec_filings":
            result = await server_instance.government.search_sec_filings(**arguments)
        
        # Scientific data tools
        elif name == "get_nasa_data":
            result = await server_instance.scientific.get_nasa_data(**arguments)
            server_instance.metrics.record_request("nasa", time.time() - start_time, "error" not in result)
        elif name == "search_research_papers":
            result = await server_instance.scientific.search_research_papers(**arguments)
        elif name == "get_climate_data":
            result = await server_instance.scientific.get_climate_data(**arguments)
        
        # Financial tools
        elif name == "get_stock_data":
            result = await server_instance.financial.get_stock_data(**arguments)
        elif name == "get_crypto_data":
            result = await server_instance.financial.get_crypto_data(**arguments)
        elif name == "get_exchange_rates":
            result = await server_instance.financial.get_exchange_rates(**arguments)
        
        # News and media tools
        elif name == "get_breaking_news":
            result = await server_instance.news.get_breaking_news(**arguments)
        elif name == "search_news":
            result = await server_instance.news.search_news(**arguments)
        elif name == "analyze_media_sentiment":
            result = await server_instance.news.analyze_media_sentiment(**arguments)
        
        # Geographic tools
        elif name == "get_weather_data":
            result = await server_instance.geographic.get_weather_data(**arguments)
        elif name == "get_air_quality":
            result = await server_instance.geographic.get_air_quality(**arguments)
        elif name == "get_disaster_alerts":
            result = await server_instance.geographic.get_disaster_alerts(**arguments)
        
        # Technology tools
        elif name == "get_github_trends":
            result = await server_instance.technology.get_github_trends(**arguments)
        elif name == "get_domain_info":
            result = await server_instance.technology.get_domain_info(**arguments)
        elif name == "analyze_tech_trends":
            result = await server_instance.technology.analyze_tech_trends(**arguments)
        
        else:
            raise ValueError(f"Unknown tool: {name}")
        
        logger.info(f"Tool {name} completed successfully")
        
        # Format result as JSON for LLM consumption
        return [types.TextContent(
            type="text",
            text=json.dumps(result, indent=2, default=str)
        )]
        
    except Exception as e:
        server_instance.metrics.record_request(name, time.time() - start_time, False)
        logger.error(f"Tool {name} execution failed: {e}", exc_info=True)
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "error": str(e),
                "tool": name,
                "arguments": arguments
            }, indent=2)
        )]

async def main():
    """Main entry point for the MCP server."""
    logger.info("Starting Universal Public Data MCP Server")
    
    try:
        # Run the server using the same pattern as the working minimal server
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            logger.info("Stdio server created, starting MCP server...")
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="universal-public-data",
                    server_version="1.0.0",
                    capabilities=types.ServerCapabilities(
                        tools=types.ToolsCapability(listChanged=False)
                    ),
                ),
            )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Server startup failed: {e}", exc_info=True)
        sys.exit(1)

def run():
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    run()
