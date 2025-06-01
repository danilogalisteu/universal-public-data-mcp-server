"""
Government data adapter for census, economic indicators, and SEC filings.
Uses real government APIs for data retrieval.
"""

import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

import httpx
import structlog
import pandas as pd

from core.cache import CacheManager

logger = structlog.get_logger(__name__)

class GovernmentDataAdapter:
    """Adapter for government data sources using real APIs."""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache = cache_manager
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={"User-Agent": "Universal-Public-Data-MCP/1.0"}
        )
    
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def get_census_data(
        self, 
        location: str, 
        metric: str, 
        year: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get US Census data using the Census Bureau API.
        
        Args:
            location: State, county, or city name
            metric: Census metric to retrieve
            year: Year for data (default: latest available)
        """
        try:
            cache_key = f"census:{location}:{metric}:{year or 'latest'}"
            cached_result = await self.cache.get(cache_key)
            if cached_result:
                return cached_result
            
            # Use 2021 ACS 5-year estimates (most recent comprehensive data)
            year = year or 2021
            
            # Census API variable mapping
            variable_map = {
                "population": "B01003_001E",  # Total population
                "median_income": "B19013_001E",  # Median household income
                "education": "B15003_022E",  # Bachelor's degree or higher
                "housing": "B25077_001E",  # Median home value
                "demographics": "B02001_002E,B02001_003E,B02001_004E,B02001_005E"  # Race demographics
            }
            
            if metric not in variable_map:
                return {
                    "error": f"Metric '{metric}' not supported. Available: {list(variable_map.keys())}",
                    "location": location,
                    "timestamp": datetime.now().isoformat()
                }
            
            # Determine geography level
            if "," in location:
                # Assume state format
                state = location.split(",")[-1].strip()
                geo_level = "state"
                geo_value = state
            else:
                # Assume state name
                geo_level = "state"
                geo_value = location
            
            # State name to FIPS code mapping (partial)
            state_fips = {
                "alabama": "01", "alaska": "02", "arizona": "04", "arkansas": "05",
                "california": "06", "colorado": "08", "connecticut": "09", "delaware": "10",
                "florida": "12", "georgia": "13", "hawaii": "15", "idaho": "16",
                "illinois": "17", "indiana": "18", "iowa": "19", "kansas": "20",
                "kentucky": "21", "louisiana": "22", "maine": "23", "maryland": "24",
                "massachusetts": "25", "michigan": "26", "minnesota": "27", "mississippi": "28",
                "missouri": "29", "montana": "30", "nebraska": "31", "nevada": "32",
                "new hampshire": "33", "new jersey": "34", "new mexico": "35", "new york": "36",
                "north carolina": "37", "north dakota": "38", "ohio": "39", "oklahoma": "40",
                "oregon": "41", "pennsylvania": "42", "rhode island": "44", "south carolina": "45",
                "south dakota": "46", "tennessee": "47", "texas": "48", "utah": "49",
                "vermont": "50", "virginia": "51", "washington": "53", "west virginia": "54",
                "wisconsin": "55", "wyoming": "56"
            }
            
            state_code = state_fips.get(geo_value.lower())
            if not state_code:
                return {
                    "error": f"State '{geo_value}' not found",
                    "location": location,
                    "timestamp": datetime.now().isoformat()
                }
            
            # Build Census API URL
            base_url = "https://api.census.gov/data"
            dataset = f"{year}/acs/acs5"
            variables = variable_map[metric]
            
            url = f"{base_url}/{dataset}"
            params = {
                "get": f"NAME,{variables}",
                "for": f"state:{state_code}"
            }
            
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if not data or len(data) < 2:
                return {
                    "error": "No data returned from Census API",
                    "location": location,
                    "timestamp": datetime.now().isoformat()
                }
            
            # Parse response (first row is headers, second row is data)
            headers = data[0]
            values = data[1]
            
            result = {
                "location": values[0],  # Full location name from Census
                "metric": metric,
                "year": year,
                "data": {},
                "source": "US Census Bureau ACS",
                "timestamp": datetime.now().isoformat()
            }
            
            # Parse the specific metric data
            if metric == "population":
                result["data"] = {
                    "total_population": int(values[1]) if values[1] != "-666666666" else None
                }
            elif metric == "median_income":
                result["data"] = {
                    "median_household_income": int(values[1]) if values[1] != "-666666666" else None,
                    "currency": "USD"
                }
            elif metric == "education":
                result["data"] = {
                    "bachelors_or_higher": int(values[1]) if values[1] != "-666666666" else None
                }
            elif metric == "housing":
                result["data"] = {
                    "median_home_value": int(values[1]) if values[1] != "-666666666" else None,
                    "currency": "USD"
                }
            elif metric == "demographics":
                result["data"] = {
                    "white_alone": int(values[1]) if values[1] != "-666666666" else None,
                    "black_alone": int(values[2]) if values[2] != "-666666666" else None,
                    "american_indian_alaska_native": int(values[3]) if values[3] != "-666666666" else None,
                    "asian_alone": int(values[4]) if values[4] != "-666666666" else None
                }
            
            # Cache for 24 hours (census data doesn't change frequently)
            await self.cache.set(cache_key, result, 86400)
            
            logger.info("Census data retrieved", location=location, metric=metric, year=year)
            return result
            
        except Exception as e:
            logger.error("Failed to get census data", location=location, metric=metric, error=str(e))
            return {
                "error": f"Failed to get census data: {str(e)}",
                "location": location,
                "metric": metric,
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_economic_indicators(
        self, 
        indicator: str, 
        timeframe: str = "1y"
    ) -> Dict[str, Any]:
        """
        Get Federal Reserve economic data using FRED API.
        
        Args:
            indicator: Economic indicator to retrieve
            timeframe: Time period for data
        """
        try:
            cache_key = f"fred:{indicator}:{timeframe}"
            cached_result = await self.cache.get(cache_key)
            if cached_result:
                return cached_result
            
            # FRED series IDs for common indicators
            series_map = {
                "gdp": "GDP",  # Gross Domestic Product
                "inflation": "CPIAUCSL",  # Consumer Price Index
                "unemployment": "UNRATE",  # Unemployment Rate
                "interest_rates": "FEDFUNDS",  # Federal Funds Rate
                "consumer_spending": "PCE"  # Personal Consumption Expenditures
            }
            
            if indicator not in series_map:
                return {
                    "error": f"Indicator '{indicator}' not supported. Available: {list(series_map.keys())}",
                    "indicator": indicator,
                    "timestamp": datetime.now().isoformat()
                }
            
            series_id = series_map[indicator]
            
            # Calculate date range
            end_date = datetime.now()
            if timeframe == "1m":
                start_date = end_date - timedelta(days=30)
            elif timeframe == "3m":
                start_date = end_date - timedelta(days=90)
            elif timeframe == "6m":
                start_date = end_date - timedelta(days=180)
            elif timeframe == "1y":
                start_date = end_date - timedelta(days=365)
            elif timeframe == "5y":
                start_date = end_date - timedelta(days=1825)
            else:
                start_date = end_date - timedelta(days=365)
            
            # FRED API endpoint (public, no API key required for basic access)
            url = "https://api.stlouisfed.org/fred/series/observations"
            params = {
                "series_id": series_id,
                "api_key": "DEMO_KEY",  # Public demo key
                "file_type": "json",
                "observation_start": start_date.strftime("%Y-%m-%d"),
                "observation_end": end_date.strftime("%Y-%m-%d"),
                "sort_order": "desc",
                "limit": 100
            }
            
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if "observations" not in data:
                return {
                    "error": "No observations returned from FRED API",
                    "indicator": indicator,
                    "timestamp": datetime.now().isoformat()
                }
            
            observations = data["observations"]
            
            # Process the data
            time_series = []
            valid_values = []
            
            for obs in reversed(observations):  # Reverse to get chronological order
                if obs["value"] != ".":  # FRED uses "." for missing values
                    try:
                        value = float(obs["value"])
                        time_series.append({
                            "date": obs["date"],
                            "value": value
                        })
                        valid_values.append(value)
                    except ValueError:
                        continue
            
            if not valid_values:
                return {
                    "error": "No valid data points found",
                    "indicator": indicator,
                    "timestamp": datetime.now().isoformat()
                }
            
            # Calculate statistics
            latest_value = valid_values[-1] if valid_values else None
            previous_value = valid_values[-2] if len(valid_values) > 1 else None
            
            change = None
            change_percent = None
            if latest_value is not None and previous_value is not None:
                change = latest_value - previous_value
                change_percent = (change / previous_value) * 100 if previous_value != 0 else None
            
            result = {
                "indicator": indicator,
                "series_id": series_id,
                "timeframe": timeframe,
                "latest_value": latest_value,
                "latest_date": time_series[-1]["date"] if time_series else None,
                "change": change,
                "change_percent": change_percent,
                "data_points": len(time_series),
                "time_series": time_series[-20:],  # Last 20 data points
                "statistics": {
                    "min": min(valid_values),
                    "max": max(valid_values),
                    "average": sum(valid_values) / len(valid_values)
                },
                "source": "Federal Reserve Economic Data (FRED)",
                "timestamp": datetime.now().isoformat()
            }
            
            # Cache for 1 hour
            await self.cache.set(cache_key, result, 3600)
            
            logger.info("FRED data retrieved", indicator=indicator, timeframe=timeframe)
            return result
            
        except Exception as e:
            logger.error("Failed to get FRED data", indicator=indicator, error=str(e))
            return {
                "error": f"Failed to get economic data: {str(e)}",
                "indicator": indicator,
                "timestamp": datetime.now().isoformat()
            }
    
    async def search_sec_filings(
        self, 
        company: str, 
        filing_type: Optional[str] = None, 
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Search SEC filings using the SEC EDGAR API.
        
        Args:
            company: Company name or ticker symbol
            filing_type: Type of SEC filing to search for
            limit: Number of results to return
        """
        try:
            cache_key = f"sec:{company}:{filing_type or 'all'}:{limit}"
            cached_result = await self.cache.get(cache_key)
            if cached_result:
                return cached_result
            
            # SEC EDGAR Company Search API
            search_url = "https://www.sec.gov/cgi-bin/browse-edgar"
            
            # First, search for the company to get CIK
            search_params = {
                "action": "getcompany",
                "company": company,
                "output": "atom",
                "count": 1
            }
            
            # Set headers as required by SEC
            headers = {
                "User-Agent": "Universal-Public-Data-MCP/1.0 (contact@example.com)",
                "Accept": "application/atom+xml"
            }
            
            response = await self.client.get(search_url, params=search_params, headers=headers)
            response.raise_for_status()
            
            # Parse the atom feed to extract company info
            import xml.etree.ElementTree as ET
            
            try:
                root = ET.fromstring(response.text)
                
                # Find entries in the atom feed
                entries = []
                ns = {"atom": "http://www.w3.org/2005/Atom"}
                
                for entry in root.findall(".//atom:entry", ns):
                    title_elem = entry.find("atom:title", ns)
                    link_elem = entry.find("atom:link", ns)
                    updated_elem = entry.find("atom:updated", ns)
                    
                    if title_elem is not None and link_elem is not None:
                        # Extract filing type from title
                        title = title_elem.text or ""
                        filing_form = ""
                        if " - " in title:
                            parts = title.split(" - ")
                            if len(parts) >= 2:
                                filing_form = parts[1].strip()
                        
                        # Filter by filing type if specified
                        if filing_type and filing_type.lower() not in filing_form.lower():
                            continue
                        
                        entry_data = {
                            "title": title,
                            "filing_type": filing_form,
                            "link": link_elem.get("href", ""),
                            "date": updated_elem.text if updated_elem is not None else "",
                            "description": title
                        }
                        entries.append(entry_data)
                        
                        if len(entries) >= limit:
                            break
                
                if not entries:
                    # Try alternative search with different parameters
                    alt_params = {
                        "company": company,
                        "type": filing_type or "",
                        "dateb": "",
                        "owner": "exclude",
                        "count": limit
                    }
                    
                    # Use the web interface to get recent filings
                    web_url = "https://www.sec.gov/cgi-bin/browse-edgar"
                    web_response = await self.client.get(web_url, params=alt_params, headers=headers)
                    
                    if web_response.status_code == 200:
                        # Basic parsing of HTML response for filing information
                        html_content = web_response.text
                        
                        # Extract basic company information from HTML
                        if "CIK" in html_content:
                            entries = [{
                                "message": f"Found company '{company}' in SEC database",
                                "note": "Full filing details require direct SEC website access",
                                "search_url": f"https://www.sec.gov/cgi-bin/browse-edgar?company={company}",
                                "filing_type": filing_type or "all"
                            }]
                
                result = {
                    "company": company,
                    "filing_type": filing_type,
                    "limit": limit,
                    "filings_found": len(entries),
                    "filings": entries,
                    "source": "SEC EDGAR Database",
                    "timestamp": datetime.now().isoformat(),
                    "note": "SEC data requires specific headers and rate limiting"
                }
                
                # Cache for 6 hours
                await self.cache.set(cache_key, result, 21600)
                
                logger.info("SEC filings retrieved", company=company, count=len(entries))
                return result
                
            except ET.ParseError as e:
                return {
                    "error": f"Failed to parse SEC response: {str(e)}",
                    "company": company,
                    "note": "SEC API may have rate limits or require registration",
                    "timestamp": datetime.now().isoformat()
                }
            
        except Exception as e:
            logger.error("Failed to search SEC filings", company=company, error=str(e))
            return {
                "error": f"Failed to search SEC filings: {str(e)}",
                "company": company,
                "note": "SEC EDGAR access requires proper headers and may have restrictions",
                "timestamp": datetime.now().isoformat()
            } 