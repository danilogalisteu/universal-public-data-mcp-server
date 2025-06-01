"""
Geographic and environmental data adapter using real weather and environmental APIs.
"""

import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

import httpx
import structlog

from core.cache import CacheManager

logger = structlog.get_logger(__name__)

class GeographicDataAdapter:
    """Adapter for geographic and environmental data sources using real APIs."""
    
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
    
    async def get_weather_data(
        self, 
        location: str, 
        type: str = "current", 
        units: str = "metric"
    ) -> Dict[str, Any]:
        """
        Get weather data and forecasts from free weather APIs.
        
        Args:
            location: City, state, or coordinates
            type: Type of weather data (current, forecast, historical)
            units: Temperature units (metric, imperial)
        """
        try:
            cache_key = f"weather:{location}:{type}:{units}"
            cached_result = await self.cache.get(cache_key)
            if cached_result:
                return cached_result
            
            result = {
                "location": location,
                "type": type,
                "units": units,
                "timestamp": datetime.now().isoformat()
            }
            
            # Use wttr.in - a free, comprehensive weather service
            url = f"https://wttr.in/{location}"
            params = {"format": "j1"}  # JSON format
            
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if type == "current":
                current = data.get("current_condition", [{}])[0]
                
                weather_data = {
                    "temperature": {
                        "celsius": current.get("temp_C"),
                        "fahrenheit": current.get("temp_F"),
                        "feels_like_celsius": current.get("FeelsLikeC"),
                        "feels_like_fahrenheit": current.get("FeelsLikeF")
                    },
                    "conditions": {
                        "description": current.get("weatherDesc", [{}])[0].get("value", ""),
                        "humidity": current.get("humidity"),
                        "cloud_cover": current.get("cloudcover"),
                        "visibility_km": current.get("visibility"),
                        "uv_index": current.get("uvIndex")
                    },
                    "wind": {
                        "speed_kmph": current.get("windspeedKmph"),
                        "speed_mph": current.get("windspeedMiles"),
                        "direction_degrees": current.get("winddirDegree"),
                        "direction_compass": current.get("winddir16Point")
                    },
                    "atmospheric": {
                        "pressure_mb": current.get("pressure"),
                        "pressure_inches": current.get("pressureInches"),
                        "precipitation_mm": current.get("precipMM")
                    }
                }
                
                result["weather"] = weather_data
                result["source"] = "wttr.in (Current Weather)"
                
            elif type == "forecast":
                forecast = data.get("weather", [])
                forecast_data = []
                
                for day in forecast:
                    day_data = {
                        "date": day.get("date"),
                        "temperature": {
                            "max_celsius": day.get("maxtempC"),
                            "max_fahrenheit": day.get("maxtempF"),
                            "min_celsius": day.get("mintempC"),
                            "min_fahrenheit": day.get("mintempF"),
                            "avg_celsius": day.get("avgtempC"),
                            "avg_fahrenheit": day.get("avgtempF")
                        },
                        "conditions": {
                            "total_snow_cm": day.get("totalSnow_cm"),
                            "sun_hours": day.get("sunHour"),
                            "uv_index": day.get("uvIndex")
                        },
                        "hourly_forecast": []
                    }
                    
                    # Add hourly data for the day
                    for hour in day.get("hourly", []):
                        hour_data = {
                            "time": hour.get("time"),
                            "temperature_c": hour.get("tempC"),
                            "temperature_f": hour.get("tempF"),
                            "feels_like_c": hour.get("FeelsLikeC"),
                            "feels_like_f": hour.get("FeelsLikeF"),
                            "wind_speed_kmph": hour.get("windspeedKmph"),
                            "humidity": hour.get("humidity"),
                            "pressure": hour.get("pressure"),
                            "precipitation_mm": hour.get("precipMM"),
                            "cloud_cover": hour.get("cloudcover"),
                            "weather_desc": hour.get("weatherDesc", [{}])[0].get("value", "")
                        }
                        day_data["hourly_forecast"].append(hour_data)
                    
                    forecast_data.append(day_data)
                
                result["forecast"] = forecast_data
                result["source"] = "wttr.in (Weather Forecast)"
                
            else:
                result["error"] = f"Weather type '{type}' not supported. Available: current, forecast"
                return result
            
            # Add location info from the response
            if "nearest_area" in data and data["nearest_area"]:
                area = data["nearest_area"][0]
                result["location_info"] = {
                    "area_name": area.get("areaName", [{}])[0].get("value", ""),
                    "country": area.get("country", [{}])[0].get("value", ""),
                    "region": area.get("region", [{}])[0].get("value", ""),
                    "latitude": area.get("latitude"),
                    "longitude": area.get("longitude")
                }
            
            # Cache for 30 minutes for current, 2 hours for forecast
            cache_ttl = 1800 if type == "current" else 7200
            await self.cache.set(cache_key, result, cache_ttl)
            
            logger.info("Weather data retrieved", location=location, type=type)
            return result
            
        except Exception as e:
            logger.error("Failed to get weather data", location=location, type=type, error=str(e))
            return {
                "error": f"Failed to get weather data: {str(e)}",
                "location": location,
                "type": type,
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_air_quality(
        self, 
        location: str, 
        pollutants: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get air quality measurements using free air quality APIs.
        
        Args:
            location: City, state, or coordinates
            pollutants: Specific pollutants to check
        """
        try:
            cache_key = f"air_quality:{location}:{pollutants or 'all'}"
            cached_result = await self.cache.get(cache_key)
            if cached_result:
                return cached_result
            
            result = {
                "location": location,
                "pollutants_requested": pollutants,
                "timestamp": datetime.now().isoformat()
            }
            
            # Try World Air Quality Index API (free, no API key required)
            try:
                # First try with the location directly
                url = f"https://api.waqi.info/feed/{location}/"
                params = {"token": "demo"}  # Demo token for testing
                
                response = await self.client.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                if data.get("status") == "ok":
                    aqi_data = data.get("data", {})
                    
                    # Extract air quality information
                    air_quality = {
                        "aqi": aqi_data.get("aqi"),
                        "dominant_pollutant": aqi_data.get("dominentpol"),
                        "station_name": aqi_data.get("city", {}).get("name"),
                        "coordinates": {
                            "latitude": aqi_data.get("city", {}).get("geo", [None, None])[0],
                            "longitude": aqi_data.get("city", {}).get("geo", [None, None])[1]
                        },
                        "measurement_time": aqi_data.get("time", {}).get("s"),
                        "pollutants": {}
                    }
                    
                    # Extract individual pollutant measurements
                    iaqi = aqi_data.get("iaqi", {})
                    pollutant_map = {
                        "pm25": "PM2.5",
                        "pm10": "PM10", 
                        "o3": "Ozone",
                        "no2": "Nitrogen Dioxide",
                        "so2": "Sulfur Dioxide",
                        "co": "Carbon Monoxide"
                    }
                    
                    for key, name in pollutant_map.items():
                        if key in iaqi:
                            air_quality["pollutants"][key] = {
                                "name": name,
                                "value": iaqi[key].get("v"),
                                "unit": "μg/m³" if key in ["pm25", "pm10"] else "ppb"
                            }
                    
                    # Interpret AQI level
                    aqi_value = air_quality.get("aqi")
                    if aqi_value:
                        if aqi_value <= 50:
                            air_quality["quality_level"] = "Good"
                            air_quality["health_message"] = "Air quality is satisfactory"
                        elif aqi_value <= 100:
                            air_quality["quality_level"] = "Moderate"
                            air_quality["health_message"] = "Air quality is acceptable for most people"
                        elif aqi_value <= 150:
                            air_quality["quality_level"] = "Unhealthy for Sensitive Groups"
                            air_quality["health_message"] = "Sensitive individuals may experience health effects"
                        elif aqi_value <= 200:
                            air_quality["quality_level"] = "Unhealthy"
                            air_quality["health_message"] = "Everyone may experience health effects"
                        elif aqi_value <= 300:
                            air_quality["quality_level"] = "Very Unhealthy"
                            air_quality["health_message"] = "Health alert - everyone may experience serious health effects"
                        else:
                            air_quality["quality_level"] = "Hazardous"
                            air_quality["health_message"] = "Emergency conditions - entire population likely affected"
                    
                    result["air_quality"] = air_quality
                    result["source"] = "World Air Quality Index (WAQI)"
                    
                else:
                    # Try alternative approach with geocoding
                    result["air_quality"] = {
                        "message": "No air quality station found for this location",
                        "suggestion": "Try a major city name or coordinates"
                    }
                    result["source"] = "WAQI (No data available)"
                    
            except Exception as e:
                logger.warning("WAQI API failed", error=str(e))
                
                # Fallback: provide general information
                result["air_quality"] = {
                    "message": "Air quality data temporarily unavailable",
                    "note": "Real-time air quality requires specific monitoring stations",
                    "suggestion": "Try again later or use a different location"
                }
                result["source"] = "Limited air quality data available"
            
            # Cache for 1 hour
            await self.cache.set(cache_key, result, 3600)
            
            logger.info("Air quality data retrieved", location=location)
            return result
            
        except Exception as e:
            logger.error("Failed to get air quality", location=location, error=str(e))
            return {
                "error": f"Failed to get air quality data: {str(e)}",
                "location": location,
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_disaster_alerts(
        self, 
        location: str, 
        disaster_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get natural disaster alerts and warnings from various sources.
        
        Args:
            location: State, region, or country
            disaster_types: Types of disasters to check for
        """
        try:
            cache_key = f"disasters:{location}:{disaster_types or 'all'}"
            cached_result = await self.cache.get(cache_key)
            if cached_result:
                return cached_result
            
            result = {
                "location": location,
                "disaster_types": disaster_types,
                "alerts": [],
                "timestamp": datetime.now().isoformat()
            }
            
            alerts = []
            
            # Check USGS Earthquake data (if location is US-related)
            if "earthquake" in (disaster_types or ["earthquake"]):
                try:
                    # USGS real-time earthquake feed
                    usgs_url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/significant_day.geojson"
                    
                    response = await self.client.get(usgs_url)
                    response.raise_for_status()
                    
                    earthquake_data = response.json()
                    
                    for feature in earthquake_data.get("features", []):
                        properties = feature.get("properties", {})
                        geometry = feature.get("geometry", {})
                        
                        # Check if earthquake is relevant to location (basic check)
                        place = properties.get("place", "").lower()
                        if location.lower() in place or any(term in place for term in location.lower().split()):
                            alerts.append({
                                "type": "earthquake",
                                "magnitude": properties.get("mag"),
                                "location": properties.get("place"),
                                "time": datetime.fromtimestamp(properties.get("time", 0) / 1000).isoformat(),
                                "coordinates": geometry.get("coordinates", [])[:2],  # [lon, lat]
                                "depth_km": geometry.get("coordinates", [None, None, None])[2],
                                "significance": properties.get("sig"),
                                "felt_reports": properties.get("felt"),
                                "alert_level": properties.get("alert"),
                                "source": "USGS Earthquake Hazards Program",
                                "url": properties.get("url")
                            })
                    
                except Exception as e:
                    logger.warning("USGS earthquake data failed", error=str(e))
            
            # Check National Weather Service alerts (US only)
            try:
                # Try to get weather alerts for US locations
                if any(term in location.lower() for term in ["us", "usa", "united states"]) or location.count(",") == 1:
                    nws_url = "https://api.weather.gov/alerts"
                    params = {"status": "actual", "urgency": "immediate,expected"}
                    
                    response = await self.client.get(nws_url, params=params)
                    response.raise_for_status()
                    
                    nws_data = response.json()
                    
                    for alert in nws_data.get("features", [])[:10]:  # Limit to 10 alerts
                        properties = alert.get("properties", {})
                        
                        # Check if alert is relevant to location
                        areas = properties.get("areaDesc", "").lower()
                        if location.lower() in areas:
                            event = properties.get("event", "").lower()
                            
                            # Categorize the alert
                            alert_type = "weather"
                            if any(term in event for term in ["tornado", "hurricane", "typhoon"]):
                                alert_type = "tornado" if "tornado" in event else "hurricane"
                            elif any(term in event for term in ["flood", "flash flood"]):
                                alert_type = "flood"
                            elif "fire" in event:
                                alert_type = "wildfire"
                            
                            # Only include if disaster type is requested
                            if not disaster_types or alert_type in disaster_types or "weather" in disaster_types:
                                alerts.append({
                                    "type": alert_type,
                                    "event": properties.get("event"),
                                    "headline": properties.get("headline"),
                                    "description": properties.get("description", "")[:500] + "..." if len(properties.get("description", "")) > 500 else properties.get("description", ""),
                                    "areas": properties.get("areaDesc"),
                                    "severity": properties.get("severity"),
                                    "urgency": properties.get("urgency"),
                                    "certainty": properties.get("certainty"),
                                    "effective": properties.get("effective"),
                                    "expires": properties.get("expires"),
                                    "source": "National Weather Service",
                                    "sender": properties.get("senderName")
                                })
                    
            except Exception as e:
                logger.warning("NWS alerts failed", error=str(e))
            
            # Check for recent significant global events (simplified)
            try:
                # Global Disaster Alert and Coordination System (GDACS) has some free feeds
                # For demo purposes, we'll provide a basic structure
                if not alerts:
                    alerts.append({
                        "type": "information",
                        "message": f"No active disaster alerts found for {location}",
                        "note": "This system checks USGS earthquakes and NWS weather alerts",
                        "last_checked": datetime.now().isoformat(),
                        "source": "Universal Public Data MCP"
                    })
            
            except Exception as e:
                logger.warning("Additional alert sources failed", error=str(e))
            
            result["alerts"] = alerts
            result["alerts_found"] = len([a for a in alerts if a.get("type") != "information"])
            
            # Add summary
            if alerts:
                alert_types = [alert.get("type") for alert in alerts if alert.get("type") != "information"]
                result["summary"] = {
                    "total_alerts": len(alert_types),
                    "alert_types": list(set(alert_types)),
                    "highest_severity": "high" if any("tornado" in str(a).lower() or "hurricane" in str(a).lower() for a in alerts) else "moderate" if alerts else "low"
                }
            
            result["sources"] = ["USGS Earthquake Hazards Program", "National Weather Service"]
            
            # Cache for 10 minutes (disaster alerts should be fresh)
            await self.cache.set(cache_key, result, 600)
            
            logger.info("Disaster alerts retrieved", location=location, alerts=len(alerts))
            return result
            
        except Exception as e:
            logger.error("Failed to get disaster alerts", location=location, error=str(e))
            return {
                "error": f"Failed to get disaster alerts: {str(e)}",
                "location": location,
                "timestamp": datetime.now().isoformat()
            } 