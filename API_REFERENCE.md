# API Reference

Complete reference for all MCP tools provided by the Universal Public Data MCP Server.

## Overview

This server provides 20+ MCP tools organized into 6 main categories, all connecting to real APIs with no mock data or placeholders.

## Tool Categories

- [Financial Data](#financial-data-tools) - 4 tools
- [Government Data](#government-data-tools) - 3 tools  
- [Scientific Data](#scientific-data-tools) - 3 tools
- [News & Media](#news--media-tools) - 3 tools
- [Geographic & Environmental](#geographic--environmental-tools) - 3 tools
- [Technology](#technology-tools) - 2 tools

---

## Financial Data Tools

### `get_stock_data`

Retrieve real-time stock market data from Yahoo Finance.

**Parameters:**
- `symbol` (string, required): Stock ticker symbol (e.g., "AAPL", "MSFT", "GOOGL")
- `period` (string, optional): Time period for historical data
  - Values: `"1d"`, `"5d"`, `"1mo"`, `"3mo"`, `"6mo"`, `"1y"`, `"2y"`, `"5y"`, `"10y"`, `"ytd"`, `"max"`
  - Default: `"1d"`
- `include_news` (boolean, optional): Include related news articles
  - Default: `false`

**Response Format:**
```json
{
  "symbol": "AAPL",
  "company_name": "Apple Inc.",
  "currency": "USD",
  "exchange": "NASDAQ",
  "current_price": 195.89,
  "market_cap": 3000000000000,
  "pe_ratio": 28.5,
  "dividend_yield": 0.52,
  "52w_high": 199.62,
  "52w_low": 164.08,
  "volume": 45234567,
  "avg_volume": 58234567,
  "beta": 1.25,
  "sector": "Technology",
  "industry": "Consumer Electronics",
  "timestamp": "2024-01-15T15:30:00Z",
  "timeframe": "1d",
  "historical_data": [
    {
      "date": "2024-01-15",
      "open": 194.27,
      "high": 196.50,
      "low": 193.89,
      "close": 195.89,
      "volume": 45234567
    }
  ]
}
```

**Example Usage:**
```python
# Get Apple stock data
result = await get_stock_data("AAPL")

# Get Tesla stock with 6-month history
result = await get_stock_data("TSLA", period="6mo", include_news=True)
```

### `get_crypto_data`

Retrieve cryptocurrency data from CoinGecko API.

**Parameters:**
- `symbol` (string, required): Cryptocurrency symbol or name (e.g., "bitcoin", "ethereum", "btc")
- `vs_currency` (string, optional): Target currency
  - Values: `"usd"`, `"eur"`, `"gbp"`, `"jpy"`, `"btc"`, etc.
  - Default: `"usd"`
- `include_market_cap` (boolean, optional): Include market cap data
  - Default: `true`

**Response Format:**
```json
{
  "id": "bitcoin",
  "symbol": "btc", 
  "name": "Bitcoin",
  "current_price": 67234.50,
  "currency": "usd",
  "last_updated": "2024-01-15T15:30:00Z",
  "timestamp": "2024-01-15T15:30:00Z",
  "market_cap": 1326789000000,
  "market_cap_rank": 1,
  "total_volume": 23456789000,
  "price_change_24h": 1654.32,
  "price_change_percentage_24h": 2.45,
  "price_change_percentage_7d": -1.23,
  "price_change_percentage_30d": 8.67,
  "high_24h": 68234.50,
  "low_24h": 65789.12,
  "ath": 69000,
  "ath_date": "2021-11-10T14:24:00Z",
  "atl": 67.81,
  "atl_date": "2013-07-06T00:00:00Z",
  "circulating_supply": 19500000,
  "total_supply": 19500000,
  "max_supply": 21000000
}
```

### `get_exchange_rates`

Get real-time currency exchange rates.

**Parameters:**
- `from_currency` (string, required): Source currency code (e.g., "USD", "EUR")
- `to_currency` (string, required): Target currency code (e.g., "EUR", "GBP")
- `amount` (float, optional): Amount to convert
  - Default: `1.0`

**Response Format:**
```json
{
  "from_currency": "USD",
  "to_currency": "EUR",
  "rate": 0.92,
  "amount": 100.0,
  "converted_amount": 92.00,
  "calculation": "100.00 USD = 92.00 EUR",
  "last_updated": "2024-01-15T15:30:00Z",
  "timestamp": "2024-01-15T15:30:00Z"
}
```

### `get_market_sentiment`

Analyze overall market sentiment indicators.

**Parameters:**
- `timeframe` (string, optional): Analysis period
  - Values: `"1d"`, `"1w"`, `"1m"`, `"3m"`
  - Default: `"1w"`
- `markets` (array, optional): Specific markets to analyze
  - Values: `["crypto", "stocks", "forex", "commodities"]`
  - Default: `["stocks", "crypto"]`

**Response Format:**
```json
{
  "timeframe": "1w",
  "markets": ["stocks", "crypto"],
  "overall_sentiment": "positive",
  "confidence": 0.72,
  "sentiment_score": 0.15,
  "indicators": {
    "fear_greed_index": 68,
    "volatility": "moderate",
    "volume_trend": "increasing"
  },
  "market_breakdown": {
    "stocks": {
      "sentiment": "positive",
      "score": 0.23,
      "top_movers": ["AAPL", "MSFT", "GOOGL"]
    },
    "crypto": {
      "sentiment": "neutral", 
      "score": 0.07,
      "top_movers": ["BTC", "ETH", "ADA"]
    }
  },
  "timestamp": "2024-01-15T15:30:00Z"
}
```

---

## Government Data Tools

### `get_census_data`

Access US Census Bureau demographic data.

**Parameters:**
- `location` (string, required): Geographic location (state, county, or city)
- `metric` (string, required): Type of census data
  - Values: `"population"`, `"median_income"`, `"education"`, `"housing"`, `"demographics"`
- `year` (integer, optional): Census year
  - Default: Latest available (2021)

**Response Format:**
```json
{
  "location": "California",
  "metric": "population", 
  "year": 2021,
  "data": {
    "total_population": 39538223
  },
  "source": "US Census Bureau ACS",
  "timestamp": "2024-01-15T15:30:00Z"
}
```

**Available Metrics:**

#### Population
```json
{
  "data": {
    "total_population": 39538223
  }
}
```

#### Median Income
```json
{
  "data": {
    "median_household_income": 75235,
    "currency": "USD"
  }
}
```

#### Education
```json
{
  "data": {
    "bachelors_or_higher": 8234567
  }
}
```

#### Housing
```json
{
  "data": {
    "median_home_value": 684800,
    "currency": "USD"
  }
}
```

#### Demographics
```json
{
  "data": {
    "white_alone": 14638000,
    "black_alone": 2267000,
    "american_indian_alaska_native": 723000,
    "asian_alone": 5979000
  }
}
```

### `get_economic_indicators`

Retrieve Federal Reserve economic data via FRED API.

**Parameters:**
- `indicator` (string, required): Economic indicator
  - Values: `"gdp"`, `"inflation"`, `"unemployment"`, `"interest_rates"`, `"consumer_spending"`
- `timeframe` (string, optional): Time period for data
  - Values: `"1m"`, `"3m"`, `"6m"`, `"1y"`, `"5y"`
  - Default: `"1y"`

**Response Format:**
```json
{
  "indicator": "unemployment",
  "series_id": "UNRATE",
  "timeframe": "1y",
  "latest_value": 3.7,
  "latest_date": "2024-01-01",
  "change": -0.1,
  "change_percent": -2.63,
  "data_points": 12,
  "time_series": [
    {
      "date": "2024-01-01",
      "value": 3.7
    },
    {
      "date": "2023-12-01", 
      "value": 3.8
    }
  ],
  "statistics": {
    "min": 3.4,
    "max": 4.2,
    "average": 3.75
  },
  "source": "Federal Reserve Economic Data (FRED)",
  "timestamp": "2024-01-15T15:30:00Z"
}
```

### `search_sec_filings`

Search SEC company filings in EDGAR database.

**Parameters:**
- `company` (string, required): Company name or ticker symbol
- `filing_type` (string, optional): SEC filing type (e.g., "10-K", "10-Q", "8-K")
- `limit` (integer, optional): Number of results to return
  - Default: `10`
  - Range: 1-50

**Response Format:**
```json
{
  "company": "Tesla Inc",
  "filing_type": "10-K",
  "limit": 10,
  "filings_found": 5,
  "filings": [
    {
      "title": "Tesla Inc - Form 10-K",
      "filing_type": "10-K",
      "date": "2024-01-29",
      "link": "https://www.sec.gov/Archives/edgar/data/1318605/000095017024006294/tsla-20231231.htm",
      "description": "Annual report"
    }
  ],
  "source": "SEC EDGAR Database",
  "timestamp": "2024-01-15T15:30:00Z"
}
```

---

## Scientific Data Tools

### `get_nasa_data`

Access NASA's extensive API collection.

**Parameters:**
- `dataset` (string, required): NASA dataset to query
  - Values: `"apod"`, `"earth"`, `"asteroids"`, `"mars_rover"`
- `date` (string, optional): Date in YYYY-MM-DD format
  - Default: Current date
- `location` (object, optional): Geographic coordinates for Earth data
  - Format: `{"lat": 40.7128, "lon": -74.0060}`

**Response Formats:**

#### APOD (Astronomy Picture of the Day)
```json
{
  "dataset": "apod",
  "title": "The Heart Nebula",
  "explanation": "What powers the Heart Nebula? The large emission nebula dubbed IC 1805...",
  "url": "https://apod.nasa.gov/apod/image/2401/HeartNebula_Hubble_960.jpg",
  "hdurl": "https://apod.nasa.gov/apod/image/2401/HeartNebula_Hubble_1920.jpg",
  "media_type": "image",
  "date": "2024-01-15",
  "source": "NASA APOD",
  "timestamp": "2024-01-15T15:30:00Z"
}
```

#### Earth Imagery
```json
{
  "dataset": "earth",
  "image_url": "https://api.nasa.gov/planetary/earth/imagery",
  "location": {
    "lat": 40.7128,
    "lon": -74.0060
  },
  "date": "2024-01-15",
  "source": "NASA Earth Imagery",
  "timestamp": "2024-01-15T15:30:00Z"
}
```

#### Asteroids (Near Earth Objects)
```json
{
  "dataset": "asteroids",
  "element_count": 12,
  "asteroids": [
    {
      "name": "(2024 AA1)",
      "id": "54400348",
      "potentially_hazardous": false,
      "estimated_diameter_km": {
        "estimated_diameter_min": 0.1234567,
        "estimated_diameter_max": 0.2765432
      },
      "close_approach_date": "2024-01-16",
      "miss_distance_km": "4567890.123456789"
    }
  ],
  "date": "2024-01-15",
  "source": "NASA Near Earth Object Web Service",
  "timestamp": "2024-01-15T15:30:00Z"
}
```

#### Mars Rover Photos
```json
{
  "dataset": "mars_rover",
  "photos": [
    {
      "id": 102693,
      "img_src": "https://mars.jpl.nasa.gov/msl-raw-images/proj/msl/redops/ods/surface/sol/01000/opgs/edr/fcam/FLB_486265257EDR_F0481570FHAZ00323M_.JPG",
      "earth_date": "2015-05-30",
      "camera": "Front Hazard Avoidance Camera",
      "rover": "Curiosity"
    }
  ],
  "sol": 1000,
  "source": "NASA Mars Rover Photos",
  "timestamp": "2024-01-15T15:30:00Z"
}
```

### `search_research_papers`

Search academic papers from PubMed and ArXiv.

**Parameters:**
- `query` (string, required): Search terms
- `source` (string, optional): Paper database
  - Values: `"pubmed"`, `"arxiv"`, `"both"`
  - Default: `"both"`
- `recent` (boolean, optional): Only return recent papers (last 6 months)
  - Default: `false`
- `limit` (integer, optional): Number of papers to return
  - Default: `10`
  - Range: 1-50

**Response Format:**
```json
{
  "query": "machine learning",
  "source": "both",
  "recent": false,
  "limit": 10,
  "papers_found": 15,
  "papers": [
    {
      "title": "Deep Learning Applications in Medical Imaging",
      "authors": ["Smith, J.", "Johnson, M.", "Wilson, K."],
      "journal": "Nature Medicine",
      "pub_date": "2024-01-10",
      "pmid": "38234567",
      "url": "https://pubmed.ncbi.nlm.nih.gov/38234567/",
      "source": "PubMed"
    },
    {
      "title": "Quantum Machine Learning Algorithms",
      "authors": ["Chen, L.", "Garcia, R."],
      "abstract": "We present a comprehensive review of quantum machine learning algorithms...",
      "published": "2024-01-12T10:30:00Z",
      "arxiv_id": "2401.12345",
      "url": "https://arxiv.org/abs/2401.12345",
      "source": "ArXiv"
    }
  ],
  "sources": "PubMed and ArXiv",
  "timestamp": "2024-01-15T15:30:00Z"
}
```

### `get_climate_data`

Retrieve weather and climate information.

**Parameters:**
- `location` (string, required): City, state, or coordinates
- `metric` (string, optional): Specific climate metric
  - Values: `"temperature"`, `"precipitation"`, `"pressure"`, `"wind"`, `"all"`
  - Default: `"all"`
- `timeframe` (string, optional): Time period
  - Values: `"current"`, `"forecast"`, `"historical"`
  - Default: `"current"`

**Response Formats:**

#### Current Weather
```json
{
  "location": "London",
  "metric": "all",
  "timeframe": "current",
  "weather": {
    "temperature": {
      "celsius": "12",
      "fahrenheit": "54",
      "feels_like_celsius": "10",
      "feels_like_fahrenheit": "50"
    },
    "conditions": {
      "description": "Partly cloudy",
      "humidity": "68",
      "cloud_cover": "50",
      "visibility_km": "10",
      "uv_index": "2"
    },
    "wind": {
      "speed_kmph": "15",
      "speed_mph": "9",
      "direction_degrees": "230",
      "direction_compass": "SW"
    },
    "atmospheric": {
      "pressure_mb": "1013",
      "pressure_inches": "29.91",
      "precipitation_mm": "0"
    }
  },
  "location_info": {
    "area_name": "London",
    "country": "United Kingdom",
    "region": "City of London, Greater London",
    "latitude": "51.517",
    "longitude": "-0.106"
  },
  "source": "wttr.in (Current Weather)",
  "timestamp": "2024-01-15T15:30:00Z"
}
```

#### Weather Forecast
```json
{
  "location": "Tokyo",
  "timeframe": "forecast",
  "forecast": [
    {
      "date": "2024-01-16",
      "temperature": {
        "max_celsius": "15",
        "max_fahrenheit": "59",
        "min_celsius": "8",
        "min_fahrenheit": "46",
        "avg_celsius": "11",
        "avg_fahrenheit": "52"
      },
      "conditions": {
        "total_snow_cm": "0",
        "sun_hours": "6.2",
        "uv_index": "3"
      },
      "hourly_forecast": [
        {
          "time": "0",
          "temperature_c": "9",
          "temperature_f": "48",
          "feels_like_c": "7",
          "feels_like_f": "45",
          "wind_speed_kmph": "12",
          "humidity": "72",
          "pressure": "1015",
          "precipitation_mm": "0",
          "cloud_cover": "60",
          "weather_desc": "Partly cloudy"
        }
      ]
    }
  ],
  "source": "wttr.in (Weather Forecast)",
  "timestamp": "2024-01-15T15:30:00Z"
}
```

---

## News & Media Tools

### `get_breaking_news`

Retrieve latest news from multiple RSS sources.

**Parameters:**
- `category` (string, optional): News category
  - Values: `"general"`, `"business"`, `"technology"`, `"science"`, `"health"`, `"sports"`
  - Default: `"general"`
- `limit` (integer, optional): Number of articles
  - Default: `10`
  - Range: 1-50
- `language` (string, optional): Language code
  - Values: `"en"`, `"es"`, `"fr"`, `"de"`
  - Default: `"en"`

**Response Format:**
```json
{
  "category": "technology",
  "limit": 10,
  "language": "en",
  "articles_found": 12,
  "articles": [
    {
      "title": "OpenAI Announces GPT-5 Development",
      "description": "OpenAI has confirmed that work on GPT-5 is underway with significant improvements...",
      "link": "https://techcrunch.com/2024/01/15/openai-gpt5-development/",
      "published": "2024-01-15T10:30:00Z",
      "published_timestamp": "2024-01-15T10:30:00Z",
      "hours_ago": 2.5,
      "source": "TechCrunch",
      "author": "Sarah Chen"
    }
  ],
  "sources": ["TechCrunch", "Ars Technica", "BBC Technology"],
  "timestamp": "2024-01-15T15:30:00Z"
}
```

### `search_news`

Search news articles by topic across RSS feeds.

**Parameters:**
- `query` (string, required): Search terms
- `timeframe` (string, optional): Time period
  - Values: `"1h"`, `"6h"`, `"24h"`, `"3d"`, `"1w"`, `"1m"`
  - Default: `"24h"`
- `sources` (array, optional): Specific news sources
- `limit` (integer, optional): Number of articles
  - Default: `15`
  - Range: 1-50

**Response Format:**
```json
{
  "query": "renewable energy",
  "timeframe": "1w",
  "sources": null,
  "limit": 15,
  "articles_found": 25,
  "articles": [
    {
      "title": "Solar Energy Capacity Reaches Record High",
      "description": "Global solar energy capacity has reached unprecedented levels...",
      "link": "https://reuters.com/business/energy/solar-capacity-record-2024-01-15/",
      "published": "2024-01-14T14:20:00Z",
      "source": "Reuters",
      "category": "business",
      "relevance_score": 0.89,
      "match_count": 3,
      "hours_ago": 18.2
    }
  ],
  "search_summary": {
    "total_matches": 25,
    "avg_relevance": 0.78,
    "categories_searched": ["general", "business", "technology", "science"]
  },
  "timestamp": "2024-01-15T15:30:00Z"
}
```

### `analyze_media_sentiment`

Analyze sentiment of news coverage about a topic.

**Parameters:**
- `topic` (string, required): Topic to analyze
- `timeframe` (string, optional): Analysis period
  - Values: `"1h"`, `"6h"`, `"24h"`, `"3d"`, `"1w"`, `"1m"`
  - Default: `"24h"`

**Response Format:**
```json
{
  "topic": "artificial intelligence",
  "timeframe": "1w",
  "sentiment": "positive",
  "sentiment_score": 0.15,
  "confidence": 0.72,
  "articles_analyzed": 45,
  "distribution": {
    "positive": 20,
    "negative": 8,
    "neutral": 17,
    "positive_percentage": 44.4,
    "negative_percentage": 17.8
  },
  "sample_articles": [
    {
      "title": "AI Breakthrough in Medical Diagnosis",
      "sentiment": "positive",
      "score": 0.67,
      "positive_words": 5,
      "negative_words": 1,
      "source": "BBC News"
    }
  ],
  "analysis_method": "keyword-based sentiment analysis",
  "timestamp": "2024-01-15T15:30:00Z"
}
```

---

## Geographic & Environmental Tools

### `get_weather_data`

Comprehensive weather information from global sources.

**Parameters:**
- `location` (string, required): City, state, or coordinates
- `type` (string, optional): Weather data type
  - Values: `"current"`, `"forecast"`, `"historical"`
  - Default: `"current"`
- `units` (string, optional): Temperature units
  - Values: `"metric"`, `"imperial"`
  - Default: `"metric"`

**Response Format:** (See `get_climate_data` for detailed format)

### `get_air_quality`

Air pollution and quality measurements.

**Parameters:**
- `location` (string, required): City or coordinates
- `pollutants` (array, optional): Specific pollutants to check
  - Values: `["pm25", "pm10", "o3", "no2", "so2", "co"]`

**Response Format:**
```json
{
  "location": "Beijing",
  "pollutants_requested": null,
  "air_quality": {
    "aqi": 89,
    "dominant_pollutant": "pm25",
    "station_name": "Beijing US Embassy",
    "coordinates": {
      "latitude": 39.9042,
      "longitude": 116.4074
    },
    "measurement_time": "2024-01-15T15:00:00Z",
    "pollutants": {
      "pm25": {
        "name": "PM2.5",
        "value": 35,
        "unit": "μg/m³"
      },
      "pm10": {
        "name": "PM10",
        "value": 58,
        "unit": "μg/m³"
      },
      "o3": {
        "name": "Ozone",
        "value": 67,
        "unit": "ppb"
      }
    },
    "quality_level": "Moderate",
    "health_message": "Air quality is acceptable for most people"
  },
  "source": "World Air Quality Index (WAQI)",
  "timestamp": "2024-01-15T15:30:00Z"
}
```

### `get_disaster_alerts`

Natural disaster monitoring and alerts.

**Parameters:**
- `location` (string, required): Geographic area (state, region, country)
- `disaster_types` (array, optional): Types of disasters to check
  - Values: `["earthquake", "hurricane", "tornado", "flood", "wildfire", "weather"]`

**Response Format:**
```json
{
  "location": "California",
  "disaster_types": ["earthquake"],
  "alerts_found": 2,
  "alerts": [
    {
      "type": "earthquake",
      "magnitude": 4.2,
      "location": "Southern California",
      "time": "2024-01-15T14:30:00Z",
      "coordinates": [-118.2437, 34.0522],
      "depth_km": 8.5,
      "significance": 312,
      "felt_reports": 1250,
      "alert_level": "green",
      "source": "USGS Earthquake Hazards Program",
      "url": "https://earthquake.usgs.gov/earthquakes/eventpage/ci40123456"
    },
    {
      "type": "weather",
      "event": "Winter Storm Warning",
      "headline": "Winter Storm Warning in effect for Sierra Nevada",
      "description": "Heavy snow expected above 6000 feet...",
      "areas": "Sierra Nevada Mountains",
      "severity": "moderate",
      "urgency": "expected",
      "certainty": "likely",
      "effective": "2024-01-15T18:00:00Z",
      "expires": "2024-01-17T06:00:00Z",
      "source": "National Weather Service",
      "sender": "NWS Reno Nevada"
    }
  ],
  "summary": {
    "total_alerts": 2,
    "alert_types": ["earthquake", "weather"],
    "highest_severity": "moderate"
  },
  "sources": ["USGS Earthquake Hazards Program", "National Weather Service"],
  "timestamp": "2024-01-15T15:30:00Z"
}
```

---

## Technology Tools

### `get_github_trends`

GitHub trending repositories and development metrics.

**Parameters:**
- `timeframe` (string, optional): Trending period
  - Values: `"daily"`, `"weekly"`, `"monthly"`
  - Default: `"daily"`
- `language` (string, optional): Programming language filter
  - Values: `"python"`, `"javascript"`, `"java"`, `"go"`, `"rust"`, etc.
- `limit` (integer, optional): Number of repositories
  - Default: `10`
  - Range: 1-50

**Response Format:**
```json
{
  "timeframe": "weekly",
  "language": "python",
  "total_count": 125,
  "repositories": [
    {
      "full_name": "microsoft/semantic-kernel",
      "name": "semantic-kernel",
      "owner": "microsoft",
      "stars": 45230,
      "stars_this_period": 1250,
      "forks": 8567,
      "language": "Python",
      "description": "Integrate cutting-edge LLM technology quickly and easily into your apps",
      "url": "https://github.com/microsoft/semantic-kernel",
      "created_at": "2023-02-15T10:30:00Z",
      "updated_at": "2024-01-15T14:20:00Z",
      "topics": ["ai", "llm", "semantic-kernel", "microsoft"],
      "license": "MIT"
    }
  ],
  "generated_at": "2024-01-15T15:30:00Z",
  "source": "GitHub Trending API",
  "timestamp": "2024-01-15T15:30:00Z"
}
```

### `get_domain_info`

Domain and website information including WHOIS data.

**Parameters:**
- `domain` (string, required): Domain name (e.g., "github.com")
- `include_whois` (boolean, optional): Include WHOIS data
  - Default: `true`
- `check_status` (boolean, optional): Check if domain is reachable
  - Default: `true`

**Response Format:**
```json
{
  "domain": "github.com",
  "status": {
    "reachable": true,
    "response_time_ms": 245,
    "status_code": 200
  },
  "whois": {
    "registrar": "MarkMonitor Inc.",
    "country": "US",
    "creation_date": "2007-10-09T18:20:50Z",
    "expiration_date": "2025-10-09T18:20:50Z",
    "updated_date": "2023-09-12T08:44:57Z",
    "name_servers": [
      "dns1.p08.nsone.net",
      "dns2.p08.nsone.net",
      "dns3.p08.nsone.net",
      "dns4.p08.nsone.net"
    ],
    "status": [
      "clientDeleteProhibited",
      "clientTransferProhibited",
      "clientUpdateProhibited"
    ]
  },
  "timestamp": "2024-01-15T15:30:00Z"
}
```

---

## Error Handling

All tools return structured error responses when issues occur:

```json
{
  "error": "Rate limit exceeded for this API",
  "error_code": "RATE_LIMITED",
  "retry_after": 60,
  "fallback_data": null,
  "timestamp": "2024-01-15T15:30:00Z",
  "tool": "get_stock_data",
  "parameters": {"symbol": "AAPL"}
}
```

Common error types:
- `API_UNAVAILABLE` - External API is temporarily down
- `RATE_LIMITED` - API rate limit exceeded
- `INVALID_PARAMETER` - Invalid parameter value
- `NOT_FOUND` - Requested data not found
- `TIMEOUT` - Request timed out
- `AUTHORIZATION_ERROR` - API key issues (when applicable)

## Rate Limits

Default rate limits (configurable):
- **60 requests per minute** per tool
- **10 burst requests** allowed
- **Intelligent caching** reduces actual API calls
- **Graceful degradation** when limits are reached

## Data Freshness

Data update frequencies:
- **Financial Data**: Real-time to 15-minute delay
- **News**: Updated every 5-15 minutes
- **Weather**: Updated hourly
- **Government Data**: Monthly to yearly updates
- **Scientific Data**: Daily to weekly updates
- **Technology Data**: Real-time to daily updates

---

*All tools connect to real APIs with no mock data or placeholders. Response times are typically under 1 second with caching enabled.* 