# 📚 Universal Public Data MCP Server - Demo Tutorial

Welcome to the comprehensive demo tutorial for the Universal Public Data MCP Server! This hands-on tutorial demonstrates how to access real-time data from multiple APIs through a unified interface.

## 🚀 What You'll Learn

This comprehensive tutorial covers:

- 💰 **Real-time financial data** from Yahoo Finance and CoinGecko
- 📰 **Breaking news feeds** from technology RSS sources
- 🌤️ **Weather data** from wttr.in API
- 📊 **Portfolio analysis** with live market data
- 🛠️ **Production patterns** for error handling and data processing

## 📋 Tutorial Overview

### 🎯 **Single Comprehensive Tutorial**

**`universal_mcp_demo.ipynb`** - Complete hands-on demonstration

This all-in-one tutorial includes:

1. **💰 Financial Data Demo**
   - Real-time Apple stock data from Yahoo Finance
   - Bitcoin cryptocurrency data from CoinGecko
   - Live market prices, volume, and market cap

2. **📊 Portfolio Analysis**
   - Multi-stock portfolio with AAPL, GOOGL, MSFT, TSLA
   - Live portfolio valuation and percentage allocation
   - Real-time price updates and total value calculation

3. **📰 Breaking News**
   - Technology news from TechCrunch and Ars Technica
   - RSS feed parsing and article extraction
   - Real-time news updates

4. **🌤️ Weather Data**
   - Current weather conditions for multiple cities
   - Temperature, humidity, wind speed, and visibility
   - Live weather data from wttr.in

## 🛠️ Getting Started

### Option 1: Google Colab (Recommended)
1. Upload `universal_mcp_demo.ipynb` to Google Colab
2. Run the cells in order
3. No setup required - all dependencies are installed automatically!

### Option 2: Local Setup
```bash
# Clone the repository
git clone https://github.com/inamdarmihir/universal-public-data-mcp-server.git
cd universal-public-data-mcp-server/demos

# Install dependencies
pip install -r requirements.txt

# Launch Jupyter
jupyter notebook universal_mcp_demo.ipynb
```

## 📦 Dependencies

The tutorial requires these packages (automatically installed in Colab):

```
yfinance>=0.2.0        # Yahoo Finance API
httpx>=0.25.0          # HTTP client for async requests
feedparser>=6.0.0      # RSS feed parsing
beautifulsoup4>=4.12.0 # HTML parsing
requests>=2.31.0       # HTTP requests
```

## 🌟 Key Features

### ✅ **Real Data, No Mocks**
- All data comes from live APIs
- Yahoo Finance for stock prices
- CoinGecko for cryptocurrency
- RSS feeds for breaking news
- wttr.in for weather conditions

### ✅ **Production-Ready Patterns**
- Error handling and graceful failures
- Timeout management for API calls
- Clean data formatting and display
- Modular function design

### ✅ **Educational Value**
- Step-by-step explanations
- Clear code comments
- Real-world use cases
- Best practices demonstration

## 🎯 Sample Output

When you run the tutorial, you'll see output like:

```
🍎 APPLE INC. (AAPL) - LIVE DATA
========================================
💰 Current Price: $230.45
📈 52W High: $237.23
📉 52W Low: $164.08
🏢 Market Cap: 3,500,234,567,890
📊 Volume: 45,678,901
🕐 Updated: 2024-01-15 14:23:45

✨ Real data from Yahoo Finance API!
```

## 🚀 About the Full MCP Server

This tutorial demonstrates a simplified version of the Universal Public Data MCP Server. The complete project includes:

### **6 Data Categories**
- **💰 Financial**: Yahoo Finance, CoinGecko, Exchange rates
- **📰 News**: RSS feeds, Breaking news, Sentiment analysis  
- **🏛️ Government**: Census data, Economic indicators, SEC filings
- **🌍 Geographic**: Weather, Air quality, Disaster alerts
- **🔬 Scientific**: NASA data, Research papers, Climate data
- **💻 Technology**: GitHub trends, Domain info, Tech metrics

### **Production Features**
- **Redis Caching**: High-performance data caching
- **Rate Limiting**: Intelligent API quota management
- **Error Handling**: Comprehensive error recovery
- **Async Operations**: Scalable concurrent processing
- **MCP Protocol**: Standardized interface for AI applications

### **20+ API Tools**
The full server provides 20+ specialized tools across all categories, each with:
- Production-grade error handling
- Intelligent caching strategies
- Rate limiting and quota management
- Comprehensive logging and monitoring

## 🛠️ Advanced Usage

### **Extending the Tutorial**

Want to add more APIs? The tutorial structure makes it easy:

```python
def get_new_api_data(param):
    """Template for adding new APIs"""
    try:
        # Your API call here
        response = requests.get(f"https://api.example.com/{param}")
        data = response.json()
        
        return {
            'formatted_data': data['field'],
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    except Exception as e:
        return {'error': str(e)}
```

### **Error Handling Pattern**

The tutorial demonstrates robust error handling:

```python
# Graceful error handling example
result = get_stock_data('AAPL')
if 'error' not in result:
    # Process successful data
    display_stock_info(result)
else:
    # Handle errors gracefully
    print(f"❌ Error: {result['error']}")
```

## 🤝 Contributing

Want to improve the tutorial? You can:

1. **Add New APIs**: Extend with additional data sources
2. **Improve Visualizations**: Add charts and graphs
3. **Enhance Error Handling**: More robust error management
4. **Add Caching**: Implement local caching strategies

## 📞 Support & Resources

- **GitHub Repository**: [universal-public-data-mcp-server](https://github.com/inamdarmihir/universal-public-data-mcp-server)
- **Issues & Questions**: Use GitHub Issues for support
- **Documentation**: Complete API docs in the `docs/` folder
- **Contributing Guide**: See `CONTRIBUTING.md` for guidelines

## 🎊 Start Learning!

Ready to explore real-time data? Open `universal_mcp_demo.ipynb` and start your journey with the Universal Public Data MCP Server!

**Happy coding and data exploring! 🚀**