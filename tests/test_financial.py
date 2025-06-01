"""
Tests for the financial data adapter.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock

from src.adapters.financial import FinancialDataAdapter
from src.core.cache import CacheManager
from src.core.config import Config

@pytest.fixture
async def financial_adapter():
    """Create a financial adapter instance for testing."""
    config = Config()
    cache = CacheManager(config)
    adapter = FinancialDataAdapter(cache)
    
    yield adapter
    
    # Cleanup
    await adapter.client.aclose()

@pytest.mark.asyncio
async def test_clean_symbol():
    """Test symbol cleaning functionality."""
    assert FinancialDataAdapter._clean_symbol("  aapl  ") == "AAPL"
    assert FinancialDataAdapter._clean_symbol("tsla") == "TSLA"
    assert FinancialDataAdapter._clean_symbol("BTC-USD") == "BTC-USD"

@pytest.mark.asyncio
async def test_get_stock_data_structure(financial_adapter):
    """Test that get_stock_data returns proper structure."""
    result = await financial_adapter.get_stock_data("AAPL")
    
    # Should always return a dict
    assert isinstance(result, dict)
    
    # Should have required fields
    assert "symbol" in result
    assert "timestamp" in result
    
    # If successful, should have stock data
    if "error" not in result:
        assert "company_name" in result
        assert "current_price" in result

@pytest.mark.asyncio
async def test_get_crypto_data_structure(financial_adapter):
    """Test that get_crypto_data returns proper structure."""
    result = await financial_adapter.get_crypto_data("bitcoin")
    
    # Should always return a dict
    assert isinstance(result, dict)
    
    # Should have required fields
    assert "symbol" in result or "error" in result
    assert "timestamp" in result

@pytest.mark.asyncio 
async def test_get_exchange_rates_structure(financial_adapter):
    """Test that get_exchange_rates returns proper structure."""
    result = await financial_adapter.get_exchange_rates("USD", "EUR")
    
    # Should always return a dict
    assert isinstance(result, dict)
    
    # Should have required fields
    assert "timestamp" in result
    
    # If successful, should have exchange data
    if "error" not in result:
        assert "from_currency" in result
        assert "to_currency" in result
        assert "rate" in result

# Integration tests (require network access)
@pytest.mark.integration
@pytest.mark.asyncio
async def test_real_stock_data(financial_adapter):
    """Test with real stock data (requires network)."""
    result = await financial_adapter.get_stock_data("AAPL", timeframe="1d")
    
    # Should get real data or a reasonable error
    assert isinstance(result, dict)
    assert result["symbol"] == "AAPL"

if __name__ == "__main__":
    pytest.main([__file__]) 