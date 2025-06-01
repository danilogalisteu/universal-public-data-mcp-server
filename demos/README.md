# Demo Tutorials & Examples

This folder contains hands-on Jupyter notebook tutorials demonstrating how to use the Universal Public Data MCP Server for real-world data analysis and AI applications.

## 📚 Available Tutorials

### 🚀 Getting Started
- **[01_quick_start.ipynb](01_quick_start.ipynb)** - Basic setup and first API calls
- **[02_understanding_tools.ipynb](02_understanding_tools.ipynb)** - Comprehensive overview of all 20+ tools

### 💰 Financial Analysis
- **[03_financial_analysis.ipynb](03_financial_analysis.ipynb)** - Stock analysis, crypto tracking, market sentiment
- **[04_investment_research.ipynb](04_investment_research.ipynb)** - Multi-source investment analysis workflow

### 🏛️ Economic Research
- **[05_economic_indicators.ipynb](05_economic_indicators.ipynb)** - GDP, unemployment, inflation analysis
- **[06_demographic_analysis.ipynb](06_demographic_analysis.ipynb)** - Census data and population studies

### 🔬 Scientific Data Mining
- **[07_nasa_space_data.ipynb](07_nasa_space_data.ipynb)** - NASA APIs, astronomy, and Earth science
- **[08_research_discovery.ipynb](08_research_discovery.ipynb)** - PubMed and ArXiv paper analysis

### 📰 Media Monitoring
- **[09_news_analysis.ipynb](09_news_analysis.ipynb)** - Breaking news and sentiment tracking
- **[10_trend_analysis.ipynb](10_trend_analysis.ipynb)** - Cross-source trend identification

### 🌍 Environmental Monitoring
- **[11_climate_weather.ipynb](11_climate_weather.ipynb)** - Weather data and climate analysis
- **[12_disaster_monitoring.ipynb](12_disaster_monitoring.ipynb)** - Natural disaster tracking and alerts

### 💻 Technology Insights
- **[13_github_trends.ipynb](13_github_trends.ipynb)** - Open source trends and development metrics
- **[14_comprehensive_dashboard.ipynb](14_comprehensive_dashboard.ipynb)** - Multi-source data dashboard

## 🛠️ Setup Instructions

### 1. Install Dependencies

```bash
# Core requirements
pip install jupyter pandas matplotlib seaborn plotly

# Optional: Enhanced visualization
pip install dash streamlit

# Optional: Advanced analysis
pip install scikit-learn numpy scipy
```

### 2. Start the MCP Server

```bash
# In project root directory
cd ..
python src/server.py
```

### 3. Launch Jupyter

```bash
# In demos directory
cd demos
jupyter notebook
```

## 📊 What You'll Learn

### Data Integration
- Connect to 20+ real public APIs
- Handle different data formats and structures
- Implement caching for performance optimization
- Manage API rate limits and error handling

### Analysis Techniques
- **Financial Analysis**: Portfolio tracking, risk assessment, market correlation
- **Economic Research**: Indicator analysis, trend forecasting, regional comparisons  
- **Scientific Discovery**: Paper analysis, research trend identification, space data visualization
- **Media Intelligence**: Sentiment analysis, news trend tracking, information synthesis
- **Environmental Monitoring**: Climate pattern analysis, disaster prediction, pollution tracking
- **Technology Insights**: Development trend analysis, repository metrics, domain research

### Visualization & Dashboards
- Create interactive charts with Plotly
- Build real-time dashboards with Streamlit/Dash
- Generate publication-ready plots with Matplotlib/Seaborn
- Design multi-source data visualizations

### Real-World Applications
- **Investment Research Platform**: Multi-source market analysis
- **Economic Policy Analysis**: Government data integration and visualization  
- **Research Intelligence**: Academic paper discovery and trend analysis
- **News Monitoring System**: Real-time media tracking and sentiment analysis
- **Environmental Dashboard**: Climate and disaster monitoring
- **Technology Trend Tracker**: Open source development insights

## 🎯 Tutorial Highlights

### Real Data, Real Results
Every tutorial uses live data from actual APIs:
- **No mock data** - All examples show real API responses
- **Live demonstrations** - See current market prices, breaking news, weather data
- **Production patterns** - Learn best practices for real-world deployment

### Code Examples You Can Use
- **Copy-paste ready** - All code cells are self-contained
- **Error handling** - Robust error handling patterns
- **Performance optimized** - Caching and rate limiting examples
- **Production ready** - Code suitable for real applications

### Progressive Complexity
- **Beginner**: Simple API calls and basic data retrieval
- **Intermediate**: Multi-source analysis and data combination
- **Advanced**: Complex workflows, custom dashboards, ML integration

## 🚀 Quick Start

1. **Open `01_quick_start.ipynb`** for your first tutorial
2. **Run all cells** to see live data retrieval
3. **Modify parameters** to explore different data sources
4. **Check real-time results** - prices, news, weather will be current!

## 📋 Prerequisites

- **Python 3.8+** installed
- **MCP Server running** (see main README for setup)
- **Internet connection** for API access
- **Jupyter Notebook** or JupyterLab

## 🔧 Troubleshooting

### Common Issues

#### Jupyter can't connect to MCP server
```bash
# Check if server is running
curl http://localhost:3000/health

# Restart server if needed
python src/server.py
```

#### Missing dependencies
```bash
# Install missing packages
pip install package_name

# Or install all demo requirements
pip install -r demos/requirements.txt
```

#### API rate limits
```python
# Enable caching in config.yaml
cache:
  enabled: true
  default_ttl: 300
```

### Getting Help

- **Issues**: Check the main repository issues
- **Discussions**: Ask questions in GitHub Discussions  
- **Documentation**: Refer to API_REFERENCE.md for detailed tool specs

## 📈 Performance Tips

### Optimize for Large Datasets
```python
# Use caching for repeated requests
cache_key = f"analysis_{symbol}_{date}"
if cache_key in cache:
    return cache[cache_key]

# Batch API requests when possible
symbols = ["AAPL", "GOOGL", "MSFT"]
results = await get_multiple_stocks(symbols)
```

### Rate Limit Management
```python
# Implement delays between requests
import asyncio
await asyncio.sleep(0.1)  # 100ms delay

# Use server-side caching
# Data is cached automatically for 5 minutes
```

### Memory Optimization
```python
# Process data in chunks for large datasets
for chunk in pd.read_csv(file, chunksize=1000):
    process_chunk(chunk)

# Clear variables when done
del large_dataframe
import gc; gc.collect()
```

## 🎨 Visualization Gallery

### Interactive Charts
- **Financial**: Real-time stock price charts, portfolio dashboards
- **Economic**: GDP trends, unemployment maps, inflation indicators
- **Scientific**: Research paper networks, space object trajectories
- **Environmental**: Weather maps, air quality heatmaps, disaster timelines
- **Technology**: GitHub star histories, language trend analysis

### Dashboard Examples
- **Market Intelligence**: Multi-asset tracking with news sentiment
- **Economic Observatory**: Regional economic indicator comparison
- **Research Hub**: Academic paper discovery and citation analysis
- **News Central**: Real-time breaking news with sentiment analysis
- **Climate Monitor**: Global weather and environmental tracking

## 🌟 Featured Use Cases

### Investment Analysis Pipeline
```python
# Get stock data
stock_data = await get_stock_data("AAPL")

# Get related news sentiment  
news_sentiment = await analyze_media_sentiment("Apple Inc", "1w")

# Get economic context
economic_data = await get_economic_indicators("gdp", "1y")

# Combine for investment decision
investment_score = calculate_investment_score(stock_data, news_sentiment, economic_data)
```

### Research Discovery Engine
```python
# Search recent papers
papers = await search_research_papers("machine learning", recent=True)

# Get trending GitHub repos
github_trends = await get_github_trends("weekly", language="python")

# Analyze research trends
trends = correlate_research_and_development(papers, github_trends)
```

### Environmental Monitoring System
```python
# Get current weather
weather = await get_weather_data("California")

# Check air quality
air_quality = await get_air_quality("Los Angeles")

# Monitor disaster alerts
disasters = await get_disaster_alerts("California", ["earthquake", "wildfire"])

# Generate environmental report
report = generate_environmental_report(weather, air_quality, disasters)
```

---

**🎉 Start exploring real public data with these comprehensive tutorials!**

*Each notebook demonstrates production-ready patterns using live APIs - no mock data anywhere.* 