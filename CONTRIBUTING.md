# Contributing to Universal Public Data MCP Server

We welcome contributions from the community! This guide will help you get started with contributing to the most comprehensive public data MCP server available.

## 🎯 Project Vision

Our mission is to democratize access to public data for AI applications by providing a unified, production-ready interface to 20+ real data sources. We believe in:

- **Real Data Only**: No mocks, dummies, or placeholders - ever
- **Public APIs**: Focus on freely accessible data sources
- **AI-Optimized**: Data formatted specifically for LLM consumption
- **Production Quality**: Professional-grade code with comprehensive testing
- **Developer Experience**: Clear documentation and easy extensibility

## 🚀 Quick Start for Contributors

### 1. Development Environment Setup

```bash
# Fork and clone the repository
git clone https://github.com/YOUR_USERNAME/universal-public-data-mcp-server.git
cd universal-public-data-mcp-server

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e .
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Verify installation
python scripts/test_server.py
```

### 2. Understanding the Architecture

```
src/
├── adapters/           # Data source adapters (main extension point)
│   ├── financial.py    # Yahoo Finance, CoinGecko, exchange rates
│   ├── government.py   # Census, FRED, SEC filings
│   ├── scientific.py   # NASA, PubMed, ArXiv, weather
│   ├── news.py         # RSS feeds, breaking news, sentiment
│   ├── geographic.py   # Weather, air quality, disaster alerts  
│   └── technology.py   # GitHub trends, domain info
├── core/               # Core infrastructure
│   ├── cache.py        # Caching system with TTL and Redis support
│   ├── config.py       # Configuration management
│   └── __init__.py     # Core exports
└── server.py           # Main MCP server with tool registration
```

### 3. Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific adapter tests
pytest tests/test_financial.py -v

# Run with coverage
pytest --cov=src tests/

# Test individual tools manually
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
        print(f'✅ Test passed: {result.get(\"current_price\")}')

asyncio.run(test())
"
```

## 🔧 Types of Contributions

### 🌟 High-Priority Contributions

#### 1. New Data Source Adapters
We're actively seeking adapters for:

- **International Economic Data**
  - World Bank Open Data
  - IMF Data Services
  - OECD Statistics
  - European Central Bank

- **Academic & Research**
  - Institutional repositories
  - Patent databases (USPTO, EPO)
  - Academic conference proceedings
  - Research collaboration networks

- **Cultural & Arts**
  - Museum APIs (Smithsonian, MoMA)
  - Library systems (Library of Congress)
  - Cultural heritage databases
  - Public art registries

- **Sports & Recreation**
  - Sports statistics APIs
  - Olympic data
  - Public recreation facilities
  - Fitness and health metrics

- **Transportation & Infrastructure**
  - Public transportation APIs
  - Traffic data (city APIs)
  - Airport and flight information
  - Infrastructure monitoring

- **Healthcare & Social**
  - Public health statistics
  - Hospital ratings and information
  - Social services directories
  - Public safety data

#### 2. Tool Enhancements
- Add more parameters to existing tools
- Improve error handling and validation
- Enhance data formatting for AI consumption
- Add caching optimization

#### 3. Infrastructure Improvements
- Performance optimizations
- Enhanced monitoring and metrics
- Docker deployment configurations
- CI/CD pipeline improvements

### 🛠️ Contributing Code

#### Adding a New Data Source Adapter

**Step 1: Create the Adapter**

```python
# src/adapters/my_new_source.py
from typing import Dict, Any, List, Optional
import aiohttp
import logging
from datetime import datetime

from ..core.cache import CacheManager

logger = logging.getLogger(__name__)

class MyNewSourceAdapter:
    """
    Adapter for accessing My New Data Source API.
    
    Provides unified access to [describe data types] through [API name].
    All data is sourced from real APIs with no mock implementations.
    """
    
    def __init__(self, cache_manager: CacheManager):
        self.cache_manager = cache_manager
        self.base_url = "https://api.mynewsource.com/v1"
        self.session = None
        
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={
                "User-Agent": "Universal-Public-Data-MCP-Server/1.0",
                "Accept": "application/json"
            }
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def get_my_data(
        self, 
        param1: str, 
        param2: Optional[str] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Retrieve data from My New Source API.
        
        Args:
            param1: Required parameter description
            param2: Optional parameter description  
            limit: Number of results to return (1-50)
            
        Returns:
            Dict containing:
            - data: List of data items
            - metadata: Request metadata
            - source: Data source attribution
            - timestamp: Request timestamp
            
        Raises:
            aiohttp.ClientError: Network/API errors
            ValueError: Invalid parameter values
        """
        # Validate parameters
        if not param1 or not param1.strip():
            raise ValueError("param1 is required and cannot be empty")
            
        if limit < 1 or limit > 50:
            raise ValueError("limit must be between 1 and 50")
        
        # Check cache first
        cache_key = f"my_new_source:get_my_data:{param1}:{param2}:{limit}"
        cached_data = await self.cache_manager.get(cache_key)
        if cached_data:
            logger.info(f"Cache hit for get_my_data: {param1}")
            return cached_data
        
        try:
            # Build request parameters
            params = {
                "param1": param1,
                "limit": limit
            }
            if param2:
                params["param2"] = param2
            
            # Make API request
            url = f"{self.base_url}/data"
            logger.info(f"Fetching data from My New Source API: {url}")
            
            async with self.session.get(url, params=params) as response:
                if response.status == 429:
                    logger.warning("Rate limit exceeded for My New Source API")
                    raise aiohttp.ClientError("Rate limit exceeded")
                    
                if response.status != 200:
                    logger.error(f"API error {response.status}: {await response.text()}")
                    raise aiohttp.ClientError(f"API returned status {response.status}")
                
                api_data = await response.json()
                
                # Transform data to standard format
                result = {
                    "param1": param1,
                    "param2": param2,
                    "limit": limit,
                    "data_found": len(api_data.get("items", [])),
                    "data": [
                        {
                            "id": item.get("id"),
                            "title": item.get("title"),
                            "description": item.get("description"),
                            "value": item.get("value"),
                            "metadata": item.get("metadata", {})
                        }
                        for item in api_data.get("items", [])
                    ],
                    "source": "My New Source API",
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }
                
                # Cache the result
                await self.cache_manager.set(cache_key, result, ttl=300)  # 5 minutes
                
                logger.info(f"Successfully retrieved {len(result['data'])} items from My New Source")
                return result
                
        except aiohttp.ClientError as e:
            logger.error(f"Network error accessing My New Source API: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in get_my_data: {e}")
            raise aiohttp.ClientError(f"Failed to fetch data: {str(e)}")
```

**Step 2: Register Tools in Main Server**

```python
# In src/server.py, add your adapter import:
from .adapters.my_new_source import MyNewSourceAdapter

# In the __init__ method, add your adapter:
self.my_new_source_adapter = MyNewSourceAdapter(self.cache_manager)

# In the list_tools method, add your tools:
@self.server.list_tools()
async def handle_list_tools() -> list[Tool]:
    tools = [
        # ... existing tools ...
        Tool(
            name="get_my_data",
            description="Retrieve data from My New Source API",
            inputSchema={
                "type": "object",
                "properties": {
                    "param1": {
                        "type": "string",
                        "description": "Required parameter description"
                    },
                    "param2": {
                        "type": "string", 
                        "description": "Optional parameter description"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of results (1-50)",
                        "minimum": 1,
                        "maximum": 50,
                        "default": 10
                    }
                },
                "required": ["param1"]
            }
        )
    ]
    return tools

# In the call_tool method, add your tool handler:
@self.server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    try:
        if name == "get_my_data":
            async with self.my_new_source_adapter as adapter:
                result = await adapter.get_my_data(
                    param1=arguments["param1"],
                    param2=arguments.get("param2"),
                    limit=arguments.get("limit", 10)
                )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        # ... existing tool handlers ...
```

**Step 3: Add Tests**

```python
# tests/test_my_new_source.py
import pytest
import asyncio
from unittest.mock import Mock, patch
import aiohttp

from src.adapters.my_new_source import MyNewSourceAdapter
from src.core.cache import CacheManager
from src.core.config import Config

class TestMyNewSourceAdapter:
    
    @pytest.fixture
    def cache_manager(self):
        config = Config()
        return CacheManager(config)
    
    @pytest.fixture
    def adapter(self, cache_manager):
        return MyNewSourceAdapter(cache_manager)
    
    @pytest.mark.asyncio
    async def test_get_my_data_success(self, adapter):
        """Test successful data retrieval."""
        # Mock successful API response
        mock_response_data = {
            "items": [
                {
                    "id": "123",
                    "title": "Test Item",
                    "description": "Test description", 
                    "value": 42.0,
                    "metadata": {"category": "test"}
                }
            ]
        }
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = Mock()
            mock_response.status = 200
            mock_response.json = asyncio.coroutine(lambda: mock_response_data)
            mock_get.return_value.__aenter__.return_value = mock_response
            
            async with adapter as a:
                result = await a.get_my_data("test_param")
                
            assert result["param1"] == "test_param"
            assert result["data_found"] == 1
            assert len(result["data"]) == 1
            assert result["data"][0]["title"] == "Test Item"
            assert result["source"] == "My New Source API"
    
    @pytest.mark.asyncio 
    async def test_get_my_data_invalid_params(self, adapter):
        """Test parameter validation."""
        async with adapter as a:
            # Test empty param1
            with pytest.raises(ValueError, match="param1 is required"):
                await a.get_my_data("")
            
            # Test invalid limit
            with pytest.raises(ValueError, match="limit must be between 1 and 50"):
                await a.get_my_data("test", limit=0)
    
    @pytest.mark.asyncio
    async def test_get_my_data_api_error(self, adapter):
        """Test API error handling."""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = Mock()
            mock_response.status = 500
            mock_response.text = asyncio.coroutine(lambda: "Internal Server Error")
            mock_get.return_value.__aenter__.return_value = mock_response
            
            async with adapter as a:
                with pytest.raises(aiohttp.ClientError):
                    await a.get_my_data("test_param")
    
    @pytest.mark.asyncio
    async def test_get_my_data_rate_limit(self, adapter):
        """Test rate limiting handling.""" 
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = Mock()
            mock_response.status = 429
            mock_get.return_value.__aenter__.return_value = mock_response
            
            async with adapter as a:
                with pytest.raises(aiohttp.ClientError, match="Rate limit exceeded"):
                    await a.get_my_data("test_param")
```

**Step 4: Update Documentation**

Add your new tools to:
- `README.md` - Add to supported data sources
- `API_REFERENCE.md` - Add complete tool documentation
- `CHANGELOG.md` - Document the new feature

**Step 5: Submit Pull Request**

```bash
# Create feature branch
git checkout -b feature/add-my-new-source

# Add your changes
git add .
git commit -m "feat: Add My New Source adapter with get_my_data tool

- Implements real API integration for [data type]
- Adds comprehensive error handling and validation  
- Includes full test coverage
- Updates documentation with API reference"

# Push and create PR
git push origin feature/add-my-new-source
```

## 📋 Code Standards

### Python Style Guide

We follow PEP 8 with some specific conventions:

```python
# Use descriptive variable names
async def get_stock_data(symbol: str, period: str = "1d") -> Dict[str, Any]:
    """Get stock data from Yahoo Finance API."""
    
# Always include type hints
cache_key: str = f"stock:{symbol}:{period}"
cached_result: Optional[Dict[str, Any]] = await self.cache.get(cache_key)

# Use meaningful docstrings
async def get_exchange_rates(
    self, 
    from_currency: str, 
    to_currency: str, 
    amount: float = 1.0
) -> Dict[str, Any]:
    """
    Get real-time currency exchange rates.
    
    Args:
        from_currency: Source currency code (e.g., "USD")
        to_currency: Target currency code (e.g., "EUR") 
        amount: Amount to convert (default: 1.0)
        
    Returns:
        Dict containing conversion rate and calculation
        
    Raises:
        ValueError: Invalid currency codes
        aiohttp.ClientError: API request failures
    """
```

### Error Handling Pattern

```python
async def api_method(self, param: str) -> Dict[str, Any]:
    """Standard error handling pattern."""
    
    # 1. Validate parameters
    if not param or not param.strip():
        raise ValueError("param is required and cannot be empty")
    
    # 2. Check cache
    cache_key = f"adapter:method:{param}"
    cached_data = await self.cache_manager.get(cache_key)
    if cached_data:
        return cached_data
    
    try:
        # 3. Make API request
        async with self.session.get(url, params=params) as response:
            if response.status == 429:
                logger.warning("Rate limit exceeded")
                raise aiohttp.ClientError("Rate limit exceeded")
                
            if response.status != 200:
                logger.error(f"API error {response.status}")
                raise aiohttp.ClientError(f"API returned status {response.status}")
            
            data = await response.json()
            
        # 4. Transform to standard format
        result = {
            "param": param,
            "data": transform_data(data),
            "source": "API Name",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        # 5. Cache result
        await self.cache_manager.set(cache_key, result, ttl=300)
        return result
        
    except aiohttp.ClientError:
        # Re-raise network errors as-is
        raise
    except Exception as e:
        # Wrap unexpected errors
        logger.error(f"Unexpected error: {e}")
        raise aiohttp.ClientError(f"Failed to fetch data: {str(e)}")
```

### Testing Requirements

Every adapter must have:

1. **Unit Tests** - Test all methods with mocked responses
2. **Integration Tests** - Test with real APIs (CI only)
3. **Error Case Tests** - Test error handling paths
4. **Parameter Validation Tests** - Test input validation

```python
# Required test structure
class TestMyAdapter:
    
    @pytest.fixture
    def adapter(self):
        # Setup adapter with mock cache
    
    @pytest.mark.asyncio
    async def test_method_success(self):
        # Test successful API call
        
    @pytest.mark.asyncio  
    async def test_method_validation(self):
        # Test parameter validation
        
    @pytest.mark.asyncio
    async def test_method_api_error(self):
        # Test API error handling
        
    @pytest.mark.asyncio
    async def test_method_rate_limit(self):
        # Test rate limiting
```

## 📚 Documentation Standards

### API Reference Format

For every new tool, add complete documentation to `API_REFERENCE.md`:

```markdown
### `tool_name`

Brief description of what the tool does and data source.

**Parameters:**
- `param1` (string, required): Description with examples
- `param2` (integer, optional): Description with range/default
  - Default: `10`
  - Range: 1-50

**Response Format:**
```json
{
  "param1": "example_value",
  "data": [...],
  "source": "API Name",
  "timestamp": "2024-01-15T15:30:00Z"
}
```

**Example Usage:**
```python
# Example call
result = await tool_name("example")
```
```

### Commit Message Format

Use conventional commits:

```bash
# New features
feat: Add World Bank adapter with economic indicators
feat(news): Add sentiment analysis for breaking news

# Bug fixes  
fix: Handle missing data in NASA APOD responses
fix(cache): Resolve Redis connection timeout issues

# Documentation
docs: Add comprehensive API reference for financial tools
docs(readme): Update installation guide for Windows

# Tests
test: Add integration tests for government data adapter
test(financial): Add error handling test cases

# Performance improvements
perf: Optimize cache key generation for better hit rates
perf(news): Reduce RSS feed parsing memory usage

# Refactoring
refactor: Extract common API error handling logic
refactor(core): Simplify configuration loading
```

## 🔍 Review Process

### Pull Request Checklist

Before submitting a PR, ensure:

- [ ] **Code Quality**
  - [ ] Follows Python style guidelines
  - [ ] Includes comprehensive type hints
  - [ ] Has descriptive variable/function names
  - [ ] Includes proper error handling

- [ ] **Testing**
  - [ ] All tests pass locally
  - [ ] New code has >90% test coverage
  - [ ] Includes both unit and integration tests
  - [ ] Tests cover error cases

- [ ] **Documentation**
  - [ ] API reference updated
  - [ ] README updated if new data source
  - [ ] Changelog entry added
  - [ ] Code includes docstrings

- [ ] **Real Data Validation**
  - [ ] Connects to real APIs (no mocks)
  - [ ] Returns actual data in demo
  - [ ] Handles API rate limits gracefully
  - [ ] Includes proper attribution

- [ ] **Performance**
  - [ ] Uses async/await properly
  - [ ] Implements caching where appropriate
  - [ ] Response times under 2 seconds
  - [ ] Memory usage reasonable

### Review Criteria

Reviewers will check:

1. **Functionality** - Does it work as intended?
2. **Code Quality** - Is it well-written and maintainable?
3. **Testing** - Is it thoroughly tested?
4. **Documentation** - Is it properly documented?
5. **Performance** - Does it perform well?
6. **Real Data** - Does it use actual APIs?

## 🏆 Recognition

Contributors will be recognized in:

- **README.md** contributors section
- **GitHub releases** mention
- **Project documentation** acknowledgments

Major contributors may be invited to become maintainers.

## 📞 Getting Help

- **GitHub Issues** - Ask questions, report bugs
- **GitHub Discussions** - Design discussions, ideas
- **Discord** - Real-time chat (coming soon)

## 📄 License

By contributing, you agree that your contributions will be licensed under the same MIT License that covers the project.

---

**Thank you for contributing to the Universal Public Data MCP Server!** 

Together, we're democratizing access to public data for AI applications. 🚀 