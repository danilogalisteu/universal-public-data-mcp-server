"""
Data quality and validation system for Universal Public Data MCP Server.
Ensures data integrity, freshness, and reliability.
"""

import asyncio
from typing import Dict, Any, List, Optional, Union, Callable
from datetime import datetime, timedelta
from enum import Enum
import re

import structlog

logger = structlog.get_logger(__name__)

class QualityLevel(Enum):
    """Data quality levels."""
    EXCELLENT = "excellent"    # 90-100% quality score
    GOOD = "good"             # 70-89% quality score  
    FAIR = "fair"             # 50-69% quality score
    POOR = "poor"             # Below 50% quality score

class DataValidator:
    """Validates data quality and completeness."""
    
    def __init__(self):
        self.validation_rules = {
            "nasa": self._validate_nasa_data,
            "financial": self._validate_financial_data,
            "news": self._validate_news_data,
            "geographic": self._validate_geographic_data,
            "government": self._validate_government_data,
            "technology": self._validate_technology_data
        }
    
    def validate_data(self, data_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data and return quality assessment."""
        if data_type in self.validation_rules:
            return self.validation_rules[data_type](data)
        else:
            return self._validate_generic_data(data)
    
    def _validate_generic_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generic data validation."""
        quality_score = 100.0
        issues = []
        
        # Check for error indicators
        if "error" in data:
            quality_score = 0.0
            issues.append("Data contains error message")
        
        # Check timestamp freshness
        if "timestamp" in data:
            try:
                timestamp = datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))
                age_hours = (datetime.now() - timestamp).total_seconds() / 3600
                
                if age_hours > 24:
                    quality_score -= 20
                    issues.append(f"Data is {age_hours:.1f} hours old")
                elif age_hours > 1:
                    quality_score -= 5
                    issues.append(f"Data is {age_hours:.1f} hours old")
            except:
                quality_score -= 10
                issues.append("Invalid timestamp format")
        
        # Check for empty or null values
        empty_fields = [k for k, v in data.items() if v is None or v == ""]
        if empty_fields:
            quality_score -= len(empty_fields) * 2
            issues.append(f"Empty fields: {empty_fields}")
        
        # Check data completeness
        if len(data) < 3:
            quality_score -= 15
            issues.append("Limited data fields")
        
        return {
            "quality_score": max(0, quality_score),
            "quality_level": self._score_to_level(quality_score),
            "issues": issues,
            "field_count": len(data),
            "validated_at": datetime.now().isoformat()
        }
    
    def _validate_nasa_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate NASA-specific data."""
        quality_score = 100.0
        issues = []
        
        # Check for required NASA fields
        required_fields = ["dataset", "source", "timestamp"]
        missing_fields = [f for f in required_fields if f not in data]
        if missing_fields:
            quality_score -= len(missing_fields) * 15
            issues.append(f"Missing NASA fields: {missing_fields}")
        
        # Validate dataset-specific requirements
        dataset = data.get("dataset")
        if dataset == "apod":
            if "title" not in data or "explanation" not in data:
                quality_score -= 20
                issues.append("APOD missing title or explanation")
        elif dataset == "asteroids":
            if "asteroids" in data and len(data["asteroids"]) == 0:
                quality_score -= 30
                issues.append("No asteroids found")
        elif dataset == "mars_rover":
            if "photos" in data and len(data["photos"]) == 0:
                quality_score -= 25
                issues.append("No Mars rover photos found")
        
        # Check for NASA API consistency
        if "source" in data and "NASA" not in data["source"]:
            quality_score -= 10
            issues.append("Source may not be NASA")
        
        base_validation = self._validate_generic_data(data)
        combined_score = (quality_score + base_validation["quality_score"]) / 2
        
        return {
            "quality_score": combined_score,
            "quality_level": self._score_to_level(combined_score),
            "issues": issues + base_validation["issues"],
            "nasa_specific": True,
            "dataset": dataset,
            "validated_at": datetime.now().isoformat()
        }
    
    def _validate_financial_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate financial data."""
        quality_score = 100.0
        issues = []
        
        # Check for numeric values
        numeric_fields = ["current_price", "volume", "market_cap", "rate", "amount"]
        for field in numeric_fields:
            if field in data:
                try:
                    float(data[field])
                except (ValueError, TypeError):
                    quality_score -= 15
                    issues.append(f"Invalid numeric value in {field}")
        
        # Check for negative prices (usually invalid)
        if "current_price" in data:
            try:
                if float(data["current_price"]) <= 0:
                    quality_score -= 25
                    issues.append("Invalid price (zero or negative)")
            except:
                pass
        
        # Check symbol format
        if "symbol" in data:
            symbol = data["symbol"]
            if not re.match(r'^[A-Z]{1,5}$', symbol):
                quality_score -= 10
                issues.append("Symbol format may be invalid")
        
        base_validation = self._validate_generic_data(data)
        combined_score = (quality_score + base_validation["quality_score"]) / 2
        
        return {
            "quality_score": combined_score,
            "quality_level": self._score_to_level(combined_score),
            "issues": issues + base_validation["issues"],
            "financial_specific": True,
            "validated_at": datetime.now().isoformat()
        }
    
    def _validate_news_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate news data."""
        quality_score = 100.0
        issues = []
        
        # Check article structure
        if "articles" in data:
            articles = data["articles"]
            if not articles:
                quality_score -= 30
                issues.append("No articles found")
            else:
                # Check article quality
                for i, article in enumerate(articles[:5]):  # Check first 5
                    if not article.get("title"):
                        quality_score -= 5
                        issues.append(f"Article {i+1} missing title")
                    if not article.get("description") and not article.get("summary"):
                        quality_score -= 3
                        issues.append(f"Article {i+1} missing description")
                    if not article.get("link") and not article.get("url"):
                        quality_score -= 3
                        issues.append(f"Article {i+1} missing link")
        
        # Check for content variety
        if "sources" in data and len(data["sources"]) < 2:
            quality_score -= 10
            issues.append("Limited news source diversity")
        
        base_validation = self._validate_generic_data(data)
        combined_score = (quality_score + base_validation["quality_score"]) / 2
        
        return {
            "quality_score": combined_score,
            "quality_level": self._score_to_level(combined_score),
            "issues": issues + base_validation["issues"],
            "news_specific": True,
            "validated_at": datetime.now().isoformat()
        }
    
    def _validate_geographic_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate geographic data."""
        quality_score = 100.0
        issues = []
        
        # Check coordinate validity
        if "location" in data or "lat" in data or "lon" in data:
            lat = data.get("lat") or data.get("location", {}).get("lat")
            lon = data.get("lon") or data.get("location", {}).get("lon")
            
            if lat is not None:
                try:
                    lat_val = float(lat)
                    if not -90 <= lat_val <= 90:
                        quality_score -= 20
                        issues.append("Invalid latitude range")
                except:
                    quality_score -= 15
                    issues.append("Invalid latitude format")
            
            if lon is not None:
                try:
                    lon_val = float(lon)
                    if not -180 <= lon_val <= 180:
                        quality_score -= 20
                        issues.append("Invalid longitude range")
                except:
                    quality_score -= 15
                    issues.append("Invalid longitude format")
        
        # Check weather data consistency
        if "temperature" in data or "temp_c" in data:
            temp = data.get("temperature") or data.get("temp_c")
            if temp is not None:
                try:
                    temp_val = float(temp)
                    if temp_val < -100 or temp_val > 60:  # Reasonable Earth temperature range
                        quality_score -= 15
                        issues.append("Temperature outside expected range")
                except:
                    quality_score -= 10
                    issues.append("Invalid temperature format")
        
        base_validation = self._validate_generic_data(data)
        combined_score = (quality_score + base_validation["quality_score"]) / 2
        
        return {
            "quality_score": combined_score,
            "quality_level": self._score_to_level(combined_score),
            "issues": issues + base_validation["issues"],
            "geographic_specific": True,
            "validated_at": datetime.now().isoformat()
        }
    
    def _validate_government_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate government data."""
        quality_score = 100.0
        issues = []
        
        # Check for official source indicators
        if "source" in data:
            source = data["source"].lower()
            official_indicators = ["census", "bureau", "gov", "federal", "usgs", "noaa", "sec"]
            if not any(indicator in source for indicator in official_indicators):
                quality_score -= 10
                issues.append("Source may not be official government data")
        
        # Check data recency for government data (can be older)
        if "timestamp" in data:
            try:
                timestamp = datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))
                age_days = (datetime.now() - timestamp).total_seconds() / 86400
                
                if age_days > 365:  # Government data can be annual
                    quality_score -= 10
                    issues.append(f"Data is {age_days:.0f} days old")
            except:
                pass
        
        base_validation = self._validate_generic_data(data)
        combined_score = (quality_score + base_validation["quality_score"]) / 2
        
        return {
            "quality_score": combined_score,
            "quality_level": self._score_to_level(combined_score),
            "issues": issues + base_validation["issues"],
            "government_specific": True,
            "validated_at": datetime.now().isoformat()
        }
    
    def _validate_technology_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate technology data."""
        quality_score = 100.0
        issues = []
        
        # Check GitHub-specific data
        if "repositories" in data:
            repos = data["repositories"]
            if not repos:
                quality_score -= 20
                issues.append("No repositories found")
            else:
                for repo in repos[:3]:  # Check first 3
                    if not repo.get("name"):
                        quality_score -= 5
                        issues.append("Repository missing name")
                    if not repo.get("url") and not repo.get("html_url"):
                        quality_score -= 5
                        issues.append("Repository missing URL")
        
        # Check domain data
        if "domain" in data:
            domain = data["domain"]
            if not re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$', domain):
                quality_score -= 15
                issues.append("Invalid domain format")
        
        base_validation = self._validate_generic_data(data)
        combined_score = (quality_score + base_validation["quality_score"]) / 2
        
        return {
            "quality_score": combined_score,
            "quality_level": self._score_to_level(combined_score),
            "issues": issues + base_validation["issues"],
            "technology_specific": True,
            "validated_at": datetime.now().isoformat()
        }
    
    def _score_to_level(self, score: float) -> str:
        """Convert quality score to quality level."""
        if score >= 90:
            return QualityLevel.EXCELLENT.value
        elif score >= 70:
            return QualityLevel.GOOD.value
        elif score >= 50:
            return QualityLevel.FAIR.value
        else:
            return QualityLevel.POOR.value

class QualityEnhancer:
    """Enhances data quality through enrichment and cleanup."""
    
    def __init__(self):
        self.enhancement_rules = {
            "nasa": self._enhance_nasa_data,
            "financial": self._enhance_financial_data,
            "news": self._enhance_news_data,
            "geographic": self._enhance_geographic_data
        }
    
    def enhance_data(self, data_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance data quality and add metadata."""
        enhanced_data = data.copy()
        
        # Add quality metadata
        validator = DataValidator()
        quality_info = validator.validate_data(data_type, data)
        enhanced_data["_quality"] = quality_info
        
        # Apply type-specific enhancements
        if data_type in self.enhancement_rules:
            enhanced_data = self.enhancement_rules[data_type](enhanced_data)
        
        # Add enhancement metadata
        enhanced_data["_enhanced"] = {
            "enhanced_at": datetime.now().isoformat(),
            "enhancements_applied": True,
            "original_field_count": len(data),
            "enhanced_field_count": len(enhanced_data)
        }
        
        return enhanced_data
    
    def _enhance_nasa_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance NASA data with additional context."""
        enhanced = data.copy()
        
        # Add dataset descriptions
        dataset_descriptions = {
            "apod": "NASA's Astronomy Picture of the Day showcases stunning astronomical images",
            "asteroids": "Near Earth Objects (NEOs) tracked by NASA's planetary defense program",
            "mars_rover": "Images captured by NASA's Mars rovers exploring the Red Planet",
            "earth": "Earth imagery from NASA's satellite observation systems",
            "exoplanets": "Confirmed exoplanets from NASA's Exoplanet Archive database"
        }
        
        dataset = data.get("dataset")
        if dataset in dataset_descriptions:
            enhanced["_context"] = {
                "description": dataset_descriptions[dataset],
                "data_category": "Scientific/Space"
            }
        
        return enhanced
    
    def _enhance_financial_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance financial data with additional context."""
        enhanced = data.copy()
        
        # Add market classification
        if "symbol" in data:
            symbol = data["symbol"]
            enhanced["_context"] = {
                "asset_type": "Stock" if len(symbol) <= 5 else "Cryptocurrency",
                "data_category": "Financial/Markets"
            }
        
        # Add price formatting
        if "current_price" in data:
            try:
                price = float(data["current_price"])
                enhanced["_formatted"] = {
                    "price_display": f"${price:,.2f}",
                    "price_class": "high" if price > 100 else "medium" if price > 10 else "low"
                }
            except:
                pass
        
        return enhanced
    
    def _enhance_news_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance news data with additional context."""
        enhanced = data.copy()
        
        # Add article insights
        if "articles" in data:
            articles = data["articles"]
            enhanced["_insights"] = {
                "article_count": len(articles),
                "avg_title_length": sum(len(a.get("title", "")) for a in articles) / len(articles) if articles else 0,
                "sources_count": len(set(a.get("source", "") for a in articles)),
                "data_category": "News/Media"
            }
        
        return enhanced
    
    def _enhance_geographic_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance geographic data with additional context."""
        enhanced = data.copy()
        
        # Add location context
        if "city" in data or "location" in data:
            enhanced["_context"] = {
                "data_category": "Geographic/Environmental",
                "data_type": "Weather" if "temperature" in data else "Location"
            }
        
        return enhanced

# Global quality system instances
data_validator = DataValidator()
quality_enhancer = QualityEnhancer() 