"""
Scientific data adapter for NASA APIs, research papers, and climate data.
Uses real scientific APIs for data retrieval.
"""

import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

import httpx
import structlog
import xml.etree.ElementTree as ET

from core.cache import CacheManager

logger = structlog.get_logger(__name__)

class ScientificDataAdapter:
    """Adapter for scientific data sources using real APIs."""
    
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
    
    async def get_nasa_data(
        self, 
        dataset: str, 
        date: Optional[str] = None, 
        location: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Get NASA data from various APIs.
        
        Args:
            dataset: NASA dataset to retrieve
            date: Date for data (YYYY-MM-DD format)
            location: Geographic coordinates for Earth data
        """
        try:
            cache_key = f"nasa:{dataset}:{date or 'latest'}:{location or 'global'}"
            cached_result = await self.cache.get(cache_key)
            if cached_result:
                return cached_result
            
            result = {
                "dataset": dataset,
                "timestamp": datetime.now().isoformat()
            }
            
            # NASA API endpoints (most are free without API key)
            if dataset == "apod":
                # Astronomy Picture of the Day
                url = "https://api.nasa.gov/planetary/apod"
                params = {"api_key": "DEMO_KEY"}
                if date:
                    params["date"] = date
                
                response = await self.client.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                result.update({
                    "title": data.get("title"),
                    "explanation": data.get("explanation"),
                    "url": data.get("url"),
                    "hdurl": data.get("hdurl"),
                    "media_type": data.get("media_type"),
                    "date": data.get("date"),
                    "source": "NASA APOD"
                })
                
            elif dataset == "earth":
                # NASA Earth Imagery
                if not location:
                    return {
                        "error": "Location (lat, lon) required for Earth imagery",
                        "dataset": dataset,
                        "timestamp": datetime.now().isoformat()
                    }
                
                url = "https://api.nasa.gov/planetary/earth/imagery"
                params = {
                    "lat": location["lat"],
                    "lon": location["lon"],
                    "api_key": "DEMO_KEY"
                }
                if date:
                    params["date"] = date
                
                response = await self.client.get(url, params=params)
                response.raise_for_status()
                
                # Earth imagery returns an image, so we get metadata
                result.update({
                    "image_url": response.url,
                    "location": location,
                    "date": date or "latest",
                    "source": "NASA Earth Imagery"
                })
                
            elif dataset == "asteroids":
                # Near Earth Object Web Service
                url = "https://api.nasa.gov/neo/rest/v1/feed"
                params = {"api_key": "DEMO_KEY"}
                
                if date:
                    params["start_date"] = date
                    params["end_date"] = date
                else:
                    # Get today's data
                    today = datetime.now().strftime("%Y-%m-%d")
                    params["start_date"] = today
                    params["end_date"] = today
                
                response = await self.client.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                asteroids = []
                
                for date_key, date_asteroids in data.get("near_earth_objects", {}).items():
                    for asteroid in date_asteroids:
                        asteroids.append({
                            "name": asteroid.get("name"),
                            "id": asteroid.get("id"),
                            "potentially_hazardous": asteroid.get("is_potentially_hazardous_asteroid"),
                            "estimated_diameter_km": asteroid.get("estimated_diameter", {}).get("kilometers", {}),
                            "close_approach_date": asteroid.get("close_approach_data", [{}])[0].get("close_approach_date"),
                            "miss_distance_km": asteroid.get("close_approach_data", [{}])[0].get("miss_distance", {}).get("kilometers")
                        })
                
                result.update({
                    "element_count": data.get("element_count", 0),
                    "asteroids": asteroids[:10],  # Limit to 10 for readability
                    "date": date or datetime.now().strftime("%Y-%m-%d"),
                    "source": "NASA Near Earth Object Web Service"
                })
                
            elif dataset == "mars_rover":
                # Mars Rover Photos
                url = "https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos"
                params = {
                    "api_key": "DEMO_KEY",
                    "sol": "1000"  # Martian day
                }
                
                response = await self.client.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                photos = []
                
                for photo in data.get("photos", [])[:5]:  # Limit to 5 photos
                    photos.append({
                        "id": photo.get("id"),
                        "img_src": photo.get("img_src"),
                        "earth_date": photo.get("earth_date"),
                        "camera": photo.get("camera", {}).get("full_name"),
                        "rover": photo.get("rover", {}).get("name")
                    })
                
                result.update({
                    "photos": photos,
                    "sol": 1000,
                    "source": "NASA Mars Rover Photos"
                })
                
            else:
                return {
                    "error": f"Dataset '{dataset}' not supported. Available: apod, earth, asteroids, mars_rover",
                    "dataset": dataset,
                    "timestamp": datetime.now().isoformat()
                }
            
            # Cache for 6 hours
            await self.cache.set(cache_key, result, 21600)
            
            logger.info("NASA data retrieved", dataset=dataset, date=date)
            return result
            
        except Exception as e:
            logger.error("Failed to get NASA data", dataset=dataset, error=str(e))
            return {
                "error": f"Failed to get NASA data: {str(e)}",
                "dataset": dataset,
                "timestamp": datetime.now().isoformat()
            }
    
    async def search_research_papers(
        self, 
        query: str, 
        source: str = "both", 
        recent: bool = False, 
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Search academic papers from PubMed and ArXiv.
        
        Args:
            query: Search query for papers
            source: Paper database (pubmed, arxiv, both)
            recent: Only return recent papers
            limit: Number of papers to return
        """
        try:
            cache_key = f"papers:{query}:{source}:{recent}:{limit}"
            cached_result = await self.cache.get(cache_key)
            if cached_result:
                return cached_result
            
            papers = []
            
            # Search PubMed
            if source in ["pubmed", "both"]:
                try:
                    # PubMed E-utilities API
                    search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
                    search_params = {
                        "db": "pubmed",
                        "term": query,
                        "retmax": limit if source == "pubmed" else limit // 2,
                        "retmode": "json",
                        "sort": "pub+date" if recent else "relevance"
                    }
                    
                    if recent:
                        # Last 6 months
                        date_filter = (datetime.now() - timedelta(days=180)).strftime("%Y/%m/%d")
                        search_params["mindate"] = date_filter
                    
                    search_response = await self.client.get(search_url, params=search_params)
                    search_response.raise_for_status()
                    
                    search_data = search_response.json()
                    pmids = search_data.get("esearchresult", {}).get("idlist", [])
                    
                    if pmids:
                        # Get paper details
                        fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
                        fetch_params = {
                            "db": "pubmed",
                            "id": ",".join(pmids),
                            "retmode": "json"
                        }
                        
                        fetch_response = await self.client.get(fetch_url, params=fetch_params)
                        fetch_response.raise_for_status()
                        
                        fetch_data = fetch_response.json()
                        
                        for pmid in pmids:
                            paper_data = fetch_data.get("result", {}).get(pmid, {})
                            if paper_data:
                                papers.append({
                                    "title": paper_data.get("title", ""),
                                    "authors": [author.get("name", "") for author in paper_data.get("authors", [])],
                                    "journal": paper_data.get("source", ""),
                                    "pub_date": paper_data.get("pubdate", ""),
                                    "pmid": pmid,
                                    "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                                    "source": "PubMed"
                                })
                    
                except Exception as e:
                    logger.warning("PubMed search failed", error=str(e))
            
            # Search ArXiv
            if source in ["arxiv", "both"]:
                try:
                    # ArXiv API
                    arxiv_url = "http://export.arxiv.org/api/query"
                    arxiv_limit = limit if source == "arxiv" else limit // 2
                    
                    arxiv_params = {
                        "search_query": f"all:{query}",
                        "start": 0,
                        "max_results": arxiv_limit,
                        "sortBy": "lastUpdatedDate" if recent else "relevance",
                        "sortOrder": "descending"
                    }
                    
                    arxiv_response = await self.client.get(arxiv_url, params=arxiv_params)
                    arxiv_response.raise_for_status()
                    
                    # Parse XML response
                    root = ET.fromstring(arxiv_response.text)
                    
                    # Namespace for ArXiv
                    ns = {
                        "atom": "http://www.w3.org/2005/Atom",
                        "arxiv": "http://arxiv.org/schemas/atom"
                    }
                    
                    for entry in root.findall("atom:entry", ns):
                        title_elem = entry.find("atom:title", ns)
                        summary_elem = entry.find("atom:summary", ns)
                        published_elem = entry.find("atom:published", ns)
                        id_elem = entry.find("atom:id", ns)
                        
                        authors = []
                        for author in entry.findall("atom:author", ns):
                            name_elem = author.find("atom:name", ns)
                            if name_elem is not None:
                                authors.append(name_elem.text)
                        
                        if title_elem is not None:
                            papers.append({
                                "title": title_elem.text.strip(),
                                "authors": authors,
                                "abstract": summary_elem.text.strip() if summary_elem is not None else "",
                                "published": published_elem.text if published_elem is not None else "",
                                "arxiv_id": id_elem.text.split("/")[-1] if id_elem is not None else "",
                                "url": id_elem.text if id_elem is not None else "",
                                "source": "ArXiv"
                            })
                    
                except Exception as e:
                    logger.warning("ArXiv search failed", error=str(e))
            
            result = {
                "query": query,
                "source": source,
                "recent": recent,
                "limit": limit,
                "papers_found": len(papers),
                "papers": papers[:limit],
                "sources": "PubMed and ArXiv" if source == "both" else source.title(),
                "timestamp": datetime.now().isoformat()
            }
            
            # Cache for 2 hours
            await self.cache.set(cache_key, result, 7200)
            
            logger.info("Research papers retrieved", query=query, count=len(papers))
            return result
            
        except Exception as e:
            logger.error("Failed to search research papers", query=query, error=str(e))
            return {
                "error": f"Failed to search research papers: {str(e)}",
                "query": query,
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_climate_data(
        self, 
        location: str, 
        metric: str, 
        timeframe: str = "current"
    ) -> Dict[str, Any]:
        """
        Get climate data from NOAA and other sources.
        
        Args:
            location: City, state, or coordinates
            metric: Climate metric to retrieve
            timeframe: Time period for data
        """
        try:
            cache_key = f"climate:{location}:{metric}:{timeframe}"
            cached_result = await self.cache.get(cache_key)
            if cached_result:
                return cached_result
            
            result = {
                "location": location,
                "metric": metric,
                "timeframe": timeframe,
                "timestamp": datetime.now().isoformat()
            }
            
            # For current weather, use a free weather API
            if timeframe == "current":
                # Use wttr.in - a free weather service
                url = f"https://wttr.in/{location}"
                params = {"format": "j1"}  # JSON format
                
                response = await self.client.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                current = data.get("current_condition", [{}])[0]
                
                if metric == "temperature":
                    result["data"] = {
                        "temperature_c": current.get("temp_C"),
                        "temperature_f": current.get("temp_F"),
                        "feels_like_c": current.get("FeelsLikeC"),
                        "feels_like_f": current.get("FeelsLikeF")
                    }
                elif metric == "precipitation":
                    result["data"] = {
                        "precipitation_mm": current.get("precipMM"),
                        "humidity": current.get("humidity"),
                        "cloud_cover": current.get("cloudcover")
                    }
                elif metric == "pressure":
                    result["data"] = {
                        "pressure_mb": current.get("pressure"),
                        "pressure_inches": current.get("pressureInches")
                    }
                elif metric == "wind":
                    result["data"] = {
                        "wind_speed_kmph": current.get("windspeedKmph"),
                        "wind_speed_mph": current.get("windspeedMiles"),
                        "wind_direction": current.get("winddirDegree"),
                        "wind_dir_compass": current.get("winddir16Point")
                    }
                else:
                    # Return all available data
                    result["data"] = {
                        "temperature_c": current.get("temp_C"),
                        "temperature_f": current.get("temp_F"),
                        "humidity": current.get("humidity"),
                        "pressure_mb": current.get("pressure"),
                        "wind_speed_kmph": current.get("windspeedKmph"),
                        "precipitation_mm": current.get("precipMM"),
                        "cloud_cover": current.get("cloudcover"),
                        "visibility_km": current.get("visibility"),
                        "uv_index": current.get("uvIndex")
                    }
                
                result["source"] = "wttr.in (Weather Data)"
                
            elif timeframe == "forecast":
                # Get forecast data
                url = f"https://wttr.in/{location}"
                params = {"format": "j1"}
                
                response = await self.client.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                forecast = data.get("weather", [])
                
                forecast_data = []
                for day in forecast[:5]:  # 5-day forecast
                    forecast_data.append({
                        "date": day.get("date"),
                        "max_temp_c": day.get("maxtempC"),
                        "max_temp_f": day.get("maxtempF"),
                        "min_temp_c": day.get("mintempC"),
                        "min_temp_f": day.get("mintempF"),
                        "total_snow_cm": day.get("totalSnow_cm"),
                        "sun_hours": day.get("sunHour"),
                        "uv_index": day.get("uvIndex")
                    })
                
                result["data"] = {
                    "forecast": forecast_data
                }
                result["source"] = "wttr.in (Weather Forecast)"
                
            else:
                # Historical data would require more complex API access
                result["data"] = {
                    "note": "Historical climate data requires specialized NOAA API access",
                    "suggestion": "Use timeframe 'current' or 'forecast' for available data"
                }
                result["source"] = "Limited historical data available"
            
            # Cache for 30 minutes for current, 2 hours for forecast
            cache_ttl = 1800 if timeframe == "current" else 7200
            await self.cache.set(cache_key, result, cache_ttl)
            
            logger.info("Climate data retrieved", location=location, metric=metric)
            return result
            
        except Exception as e:
            logger.error("Failed to get climate data", location=location, metric=metric, error=str(e))
            return {
                "error": f"Failed to get climate data: {str(e)}",
                "location": location,
                "metric": metric,
                "timestamp": datetime.now().isoformat()
            } 