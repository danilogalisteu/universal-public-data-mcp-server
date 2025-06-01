"""
Financial data adapter for stock prices, cryptocurrency, and exchange rates.
Uses public APIs that don't require authentication for basic functionality.
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

import httpx
import structlog
import yfinance as yf

from core.cache import CacheManager

logger = structlog.get_logger(__name__)

class FinancialDataAdapter:
    """Adapter for financial market data from multiple sources."""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache = cache_manager
        self.client = httpx.AsyncClient(timeout=30.0)
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    @staticmethod
    def _clean_symbol(symbol: str) -> str:
        """Clean and normalize stock/crypto symbol."""
        return symbol.upper().strip()
    
    async def get_stock_data(
        self, 
        symbol: str, 
        timeframe: str = "1d", 
        metrics: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get stock data using yfinance (Yahoo Finance).
        
        Args:
            symbol: Stock ticker symbol
            timeframe: Time period for data
            metrics: Specific metrics to return
        """
        symbol = self._clean_symbol(symbol)
        
        try:
            # Use cache decorator
            cache_key = f"stock:{symbol}:{timeframe}:{':'.join(metrics or [])}"
            cached_result = await self.cache.get(cache_key)
            if cached_result:
                return cached_result
            
            # Get stock data using yfinance
            stock = yf.Ticker(symbol)
            
            # Get basic info
            info = stock.info
            
            # Get historical data based on timeframe
            period_map = {
                "1d": "1d",
                "5d": "5d", 
                "1mo": "1mo",
                "3mo": "3mo",
                "6mo": "6mo",
                "1y": "1y",
                "5y": "5y"
            }
            
            period = period_map.get(timeframe, "1d")
            hist_data = stock.history(period=period)
            
            result = {
                "symbol": symbol,
                "company_name": info.get("longName", "N/A"),
                "currency": info.get("currency", "USD"),
                "exchange": info.get("exchange", "N/A"),
                "current_price": info.get("currentPrice", hist_data['Close'].iloc[-1] if not hist_data.empty else None),
                "market_cap": info.get("marketCap"),
                "pe_ratio": info.get("forwardPE"),
                "dividend_yield": info.get("dividendYield"),
                "52w_high": info.get("fiftyTwoWeekHigh"),
                "52w_low": info.get("fiftyTwoWeekLow"),
                "volume": info.get("volume"),
                "avg_volume": info.get("averageVolume"),
                "beta": info.get("beta"),
                "sector": info.get("sector"),
                "industry": info.get("industry"),
                "timestamp": datetime.now().isoformat(),
                "timeframe": timeframe
            }
            
            # Add historical data if available
            if not hist_data.empty:
                result["historical_data"] = {
                    "dates": hist_data.index.strftime('%Y-%m-%d').tolist(),
                    "open": hist_data['Open'].tolist(),
                    "high": hist_data['High'].tolist(),
                    "low": hist_data['Low'].tolist(),
                    "close": hist_data['Close'].tolist(),
                    "volume": hist_data['Volume'].tolist()
                }
                
                # Calculate performance metrics
                if len(hist_data) > 1:
                    price_change = hist_data['Close'].iloc[-1] - hist_data['Close'].iloc[0]
                    price_change_pct = (price_change / hist_data['Close'].iloc[0]) * 100
                    result["performance"] = {
                        "change": float(price_change),
                        "change_percent": float(price_change_pct),
                        "period": timeframe
                    }
            
            # Filter metrics if specified
            if metrics:
                filtered_result = {"symbol": symbol, "timestamp": result["timestamp"]}
                for metric in metrics:
                    if metric in result:
                        filtered_result[metric] = result[metric]
                result = filtered_result
            
            # Cache result for 5 minutes
            await self.cache.set(cache_key, result, 300)
            
            logger.info("Stock data retrieved", symbol=symbol, timeframe=timeframe)
            return result
            
        except Exception as e:
            logger.error("Failed to get stock data", symbol=symbol, error=str(e))
            return {
                "error": f"Failed to get stock data for {symbol}: {str(e)}",
                "symbol": symbol,
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_crypto_data(
        self, 
        symbol: str, 
        currency: str = "USD", 
        include_market_data: bool = True
    ) -> Dict[str, Any]:
        """
        Get cryptocurrency data from CoinGecko API.
        
        Args:
            symbol: Crypto symbol (e.g., BTC, ETH)
            currency: Base currency for pricing
            include_market_data: Include market cap, volume, etc.
        """
        symbol = symbol.lower().strip()
        currency = currency.lower().strip()
        
        try:
            cache_key = f"crypto:{symbol}:{currency}:{include_market_data}"
            cached_result = await self.cache.get(cache_key)
            if cached_result:
                return cached_result
            
            # CoinGecko API (free, no API key required)
            base_url = "https://api.coingecko.com/api/v3"
            
            # First, get the coin ID from symbol
            coins_url = f"{base_url}/coins/list"
            response = await self.client.get(coins_url)
            response.raise_for_status()
            
            coins = response.json()
            coin_id = None
            
            for coin in coins:
                if coin['symbol'].lower() == symbol:
                    coin_id = coin['id']
                    break
            
            if not coin_id:
                return {
                    "error": f"Cryptocurrency symbol '{symbol}' not found",
                    "symbol": symbol,
                    "timestamp": datetime.now().isoformat()
                }
            
            # Get detailed coin data
            coin_url = f"{base_url}/coins/{coin_id}"
            params = {
                "localization": "false",
                "tickers": "false",
                "market_data": "true",
                "community_data": "false",
                "developer_data": "false",
                "sparkline": "false"
            }
            
            response = await self.client.get(coin_url, params=params)
            response.raise_for_status()
            
            coin_data = response.json()
            market_data = coin_data.get('market_data', {})
            
            result = {
                "id": coin_id,
                "symbol": symbol.upper(),
                "name": coin_data.get('name'),
                "current_price": market_data.get('current_price', {}).get(currency),
                "currency": currency.upper(),
                "last_updated": market_data.get('last_updated'),
                "timestamp": datetime.now().isoformat()
            }
            
            if include_market_data:
                result.update({
                    "market_cap": market_data.get('market_cap', {}).get(currency),
                    "market_cap_rank": market_data.get('market_cap_rank'),
                    "total_volume": market_data.get('total_volume', {}).get(currency),
                    "price_change_24h": market_data.get('price_change_24h'),
                    "price_change_percentage_24h": market_data.get('price_change_percentage_24h'),
                    "price_change_percentage_7d": market_data.get('price_change_percentage_7d'),
                    "price_change_percentage_30d": market_data.get('price_change_percentage_30d'),
                    "high_24h": market_data.get('high_24h', {}).get(currency),
                    "low_24h": market_data.get('low_24h', {}).get(currency),
                    "ath": market_data.get('ath', {}).get(currency),
                    "ath_date": market_data.get('ath_date', {}).get(currency),
                    "atl": market_data.get('atl', {}).get(currency),
                    "atl_date": market_data.get('atl_date', {}).get(currency),
                    "circulating_supply": market_data.get('circulating_supply'),
                    "total_supply": market_data.get('total_supply'),
                    "max_supply": market_data.get('max_supply')
                })
            
            # Cache result for 2 minutes (crypto prices change frequently)
            await self.cache.set(cache_key, result, 120)
            
            logger.info("Crypto data retrieved", symbol=symbol, currency=currency)
            return result
            
        except Exception as e:
            logger.error("Failed to get crypto data", symbol=symbol, error=str(e))
            return {
                "error": f"Failed to get crypto data for {symbol}: {str(e)}",
                "symbol": symbol,
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_exchange_rates(
        self, 
        from_currency: str, 
        to_currency: str, 
        amount: float = 1.0
    ) -> Dict[str, Any]:
        """
        Get currency exchange rates using a free API.
        
        Args:
            from_currency: Source currency code
            to_currency: Target currency code
            amount: Amount to convert
        """
        from_currency = from_currency.upper().strip()
        to_currency = to_currency.upper().strip()
        
        try:
            cache_key = f"exchange:{from_currency}:{to_currency}"
            cached_result = await self.cache.get(cache_key)
            
            if cached_result:
                # Calculate with current amount
                rate = cached_result['rate']
                converted_amount = amount * rate
                
                return {
                    **cached_result,
                    "amount": amount,
                    "converted_amount": converted_amount,
                    "calculation": f"{amount} {from_currency} = {converted_amount:.2f} {to_currency}"
                }
            
            # Use exchangerate-api.com (free, no API key required)
            url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
            
            response = await self.client.get(url)
            response.raise_for_status()
            
            data = response.json()
            
            if to_currency not in data['rates']:
                return {
                    "error": f"Currency '{to_currency}' not supported",
                    "from_currency": from_currency,
                    "to_currency": to_currency,
                    "timestamp": datetime.now().isoformat()
                }
            
            rate = data['rates'][to_currency]
            converted_amount = amount * rate
            
            result = {
                "from_currency": from_currency,
                "to_currency": to_currency,
                "rate": rate,
                "amount": amount,
                "converted_amount": converted_amount,
                "calculation": f"{amount} {from_currency} = {converted_amount:.2f} {to_currency}",
                "last_updated": data.get('time_last_updated'),
                "timestamp": datetime.now().isoformat()
            }
            
            # Cache the rate for 10 minutes
            rate_data = {
                "from_currency": from_currency,
                "to_currency": to_currency,
                "rate": rate,
                "last_updated": data.get('time_last_updated'),
                "timestamp": result["timestamp"]
            }
            await self.cache.set(cache_key, rate_data, 600)
            
            logger.info("Exchange rate retrieved", 
                       from_currency=from_currency, 
                       to_currency=to_currency, 
                       rate=rate)
            return result
            
        except Exception as e:
            logger.error("Failed to get exchange rate", 
                        from_currency=from_currency, 
                        to_currency=to_currency, 
                        error=str(e))
            return {
                "error": f"Failed to get exchange rate from {from_currency} to {to_currency}: {str(e)}",
                "from_currency": from_currency,
                "to_currency": to_currency,
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_market_sentiment(self, timeframe: str = "24h") -> Dict[str, Any]:
        """
        Get basic market sentiment indicators.
        
        Args:
            timeframe: Time period for analysis
        """
        try:
            cache_key = f"market_sentiment:{timeframe}"
            cached_result = await self.cache.get(cache_key)
            if cached_result:
                return cached_result
            
            # Get data for major indices/cryptos as sentiment indicators
            sentiment_data = await asyncio.gather(
                self.get_crypto_data("bitcoin", include_market_data=True),
                self.get_crypto_data("ethereum", include_market_data=True),
                self.get_stock_data("^GSPC"),  # S&P 500
                self.get_stock_data("^VIX"),   # VIX (volatility index)
                return_exceptions=True
            )
            
            bitcoin_data, ethereum_data, sp500_data, vix_data = sentiment_data
            
            result = {
                "timeframe": timeframe,
                "indicators": {},
                "timestamp": datetime.now().isoformat()
            }
            
            # Analyze Bitcoin sentiment
            if isinstance(bitcoin_data, dict) and "error" not in bitcoin_data:
                btc_change = bitcoin_data.get("price_change_percentage_24h", 0)
                result["indicators"]["bitcoin"] = {
                    "price_change_24h": btc_change,
                    "sentiment": "bullish" if btc_change > 2 else "bearish" if btc_change < -2 else "neutral"
                }
            
            # Analyze Ethereum sentiment  
            if isinstance(ethereum_data, dict) and "error" not in ethereum_data:
                eth_change = ethereum_data.get("price_change_percentage_24h", 0)
                result["indicators"]["ethereum"] = {
                    "price_change_24h": eth_change,
                    "sentiment": "bullish" if eth_change > 2 else "bearish" if eth_change < -2 else "neutral"
                }
            
            # Analyze S&P 500 sentiment
            if isinstance(sp500_data, dict) and "error" not in sp500_data:
                performance = sp500_data.get("performance", {})
                change_pct = performance.get("change_percent", 0)
                result["indicators"]["sp500"] = {
                    "price_change": change_pct,
                    "sentiment": "bullish" if change_pct > 1 else "bearish" if change_pct < -1 else "neutral"
                }
            
            # Analyze VIX (fear index)
            if isinstance(vix_data, dict) and "error" not in vix_data:
                vix_price = vix_data.get("current_price", 20)
                result["indicators"]["vix"] = {
                    "value": vix_price,
                    "sentiment": "fearful" if vix_price > 30 else "greedy" if vix_price < 15 else "neutral"
                }
            
            # Overall sentiment
            sentiments = [
                indicator.get("sentiment", "neutral") 
                for indicator in result["indicators"].values()
            ]
            
            bullish_count = sentiments.count("bullish") + sentiments.count("greedy")
            bearish_count = sentiments.count("bearish") + sentiments.count("fearful")
            
            if bullish_count > bearish_count:
                overall_sentiment = "bullish"
            elif bearish_count > bullish_count:
                overall_sentiment = "bearish"
            else:
                overall_sentiment = "neutral"
            
            result["overall_sentiment"] = overall_sentiment
            result["confidence"] = abs(bullish_count - bearish_count) / len(sentiments) if sentiments else 0
            
            # Cache for 15 minutes
            await self.cache.set(cache_key, result, 900)
            
            logger.info("Market sentiment analyzed", sentiment=overall_sentiment)
            return result
            
        except Exception as e:
            logger.error("Failed to get market sentiment", error=str(e))
            return {
                "error": f"Failed to analyze market sentiment: {str(e)}",
                "timestamp": datetime.now().isoformat()
            } 