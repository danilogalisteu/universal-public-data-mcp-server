"""
Technology data adapter for GitHub trends, domain information, and tech metrics.
"""

import asyncio
import re
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

import httpx
import structlog
try:
    import whois
    WHOIS_AVAILABLE = True
except ImportError:
    WHOIS_AVAILABLE = False

from core.cache import CacheManager

logger = structlog.get_logger(__name__)

class TechnologyDataAdapter:
    """Adapter for technology-related data sources."""
    
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
    
    async def get_github_trends(
        self, 
        timeframe: str = "daily", 
        language: Optional[str] = None, 
        limit: int = 25
    ) -> Dict[str, Any]:
        """
        Get trending repositories from GitHub.
        Uses GitHub's public search API to find trending repos.
        """
        try:
            cache_key = f"github_trends:{timeframe}:{language}:{limit}"
            cached_result = await self.cache.get(cache_key)
            if cached_result:
                return cached_result
            
            # Calculate date range based on timeframe
            now = datetime.now()
            if timeframe == "daily":
                since = now - timedelta(days=1)
                cache_ttl = 3600  # 1 hour
            elif timeframe == "weekly":
                since = now - timedelta(days=7)
                cache_ttl = 3600 * 6  # 6 hours
            elif timeframe == "monthly":
                since = now - timedelta(days=30)
                cache_ttl = 3600 * 12  # 12 hours
            else:
                since = now - timedelta(days=1)
                cache_ttl = 3600
            
            # Build search query
            date_str = since.strftime("%Y-%m-%d")
            query = f"created:>{date_str}"
            
            if language:
                query += f" language:{language}"
            
            # GitHub Search API
            url = "https://api.github.com/search/repositories"
            params = {
                "q": query,
                "sort": "stars",
                "order": "desc",
                "per_page": min(limit, 100)  # GitHub API limit
            }
            
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            repositories = []
            
            for repo in data.get("items", []):
                repositories.append({
                    "name": repo["name"],
                    "full_name": repo["full_name"],
                    "description": repo.get("description", ""),
                    "language": repo.get("language"),
                    "stars": repo["stargazers_count"],
                    "forks": repo["forks_count"],
                    "watchers": repo["watchers_count"],
                    "open_issues": repo["open_issues_count"],
                    "created_at": repo["created_at"],
                    "updated_at": repo["updated_at"],
                    "html_url": repo["html_url"],
                    "homepage": repo.get("homepage"),
                    "topics": repo.get("topics", []),
                    "license": repo.get("license", {}).get("name") if repo.get("license") else None
                })
            
            result = {
                "timeframe": timeframe,
                "language": language,
                "total_count": data.get("total_count", 0),
                "repositories": repositories[:limit],
                "generated_at": datetime.now().isoformat(),
                "source": "GitHub API"
            }
            
            # Cache the result
            await self.cache.set(cache_key, result, cache_ttl)
            
            logger.info("GitHub trends retrieved", 
                       timeframe=timeframe, 
                       language=language, 
                       count=len(repositories))
            return result
            
        except Exception as e:
            logger.error("Failed to get GitHub trends", error=str(e))
            return {
                "error": f"Failed to get GitHub trends: {str(e)}",
                "timeframe": timeframe,
                "language": language,
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_domain_info(
        self, 
        domain: str, 
        include_dns: bool = False
    ) -> Dict[str, Any]:
        """
        Get domain information including WHOIS data.
        
        Args:
            domain: Domain name to lookup
            include_dns: Include DNS record information
        """
        domain = domain.lower().strip()
        
        # Validate domain format
        domain_pattern = re.compile(
            r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$'
        )
        
        if not domain_pattern.match(domain):
            return {
                "error": "Invalid domain format",
                "domain": domain,
                "timestamp": datetime.now().isoformat()
            }
        
        try:
            cache_key = f"domain_info:{domain}:{include_dns}"
            cached_result = await self.cache.get(cache_key)
            if cached_result:
                return cached_result
            
            result = {
                "domain": domain,
                "timestamp": datetime.now().isoformat()
            }
            
            # Get WHOIS information if available
            if WHOIS_AVAILABLE:
                try:
                    whois_data = whois.whois(domain)
                    result["whois"] = {
                        "registrar": whois_data.registrar,
                        "creation_date": str(whois_data.creation_date) if whois_data.creation_date else None,
                        "expiration_date": str(whois_data.expiration_date) if whois_data.expiration_date else None,
                        "updated_date": str(whois_data.updated_date) if whois_data.updated_date else None,
                        "status": whois_data.status,
                        "name_servers": whois_data.name_servers,
                        "country": whois_data.country,
                        "org": whois_data.org
                    }
                except Exception as e:
                    result["whois"] = {"error": f"WHOIS lookup failed: {str(e)}"}
            else:
                result["whois"] = {"error": "WHOIS module not available"}
            
            # Basic DNS information using HTTP APIs
            if include_dns:
                try:
                    # Use a public DNS-over-HTTPS service
                    dns_url = f"https://1.1.1.1/dns-query"
                    headers = {"Accept": "application/dns-json"}
                    
                    # Get A record
                    response = await self.client.get(
                        dns_url, 
                        params={"name": domain, "type": "A"},
                        headers=headers
                    )
                    
                    if response.status_code == 200:
                        dns_data = response.json()
                        result["dns"] = {
                            "a_records": [
                                answer["data"] for answer in dns_data.get("Answer", [])
                                if answer.get("type") == 1  # A record
                            ]
                        }
                    else:
                        result["dns"] = {"error": "DNS lookup failed"}
                        
                except Exception as e:
                    result["dns"] = {"error": f"DNS lookup failed: {str(e)}"}
            
            # Check if domain is reachable
            try:
                response = await self.client.head(f"https://{domain}", timeout=10.0)
                result["status"] = {
                    "reachable": True,
                    "status_code": response.status_code,
                    "headers": dict(response.headers)
                }
            except:
                try:
                    response = await self.client.head(f"http://{domain}", timeout=10.0)
                    result["status"] = {
                        "reachable": True,
                        "status_code": response.status_code,
                        "headers": dict(response.headers),
                        "note": "Only HTTP available"
                    }
                except:
                    result["status"] = {"reachable": False}
            
            # Cache for 1 hour (domain info doesn't change frequently)
            await self.cache.set(cache_key, result, 3600)
            
            logger.info("Domain info retrieved", domain=domain)
            return result
            
        except Exception as e:
            logger.error("Failed to get domain info", domain=domain, error=str(e))
            return {
                "error": f"Failed to get domain info for {domain}: {str(e)}",
                "domain": domain,
                "timestamp": datetime.now().isoformat()
            }
    
    async def analyze_tech_trends(
        self, 
        technology: str, 
        metrics: Optional[List[str]] = None, 
        timeframe: str = "6m"
    ) -> Dict[str, Any]:
        """
        Analyze technology trends using multiple data sources.
        
        Args:
            technology: Technology or framework to analyze
            metrics: Specific metrics to include
            timeframe: Analysis timeframe
        """
        if not metrics:
            metrics = ["github_stars", "stackoverflow_questions"]
        
        try:
            cache_key = f"tech_trends:{technology}:{':'.join(metrics)}:{timeframe}"
            cached_result = await self.cache.get(cache_key)
            if cached_result:
                return cached_result
            
            result = {
                "technology": technology,
                "timeframe": timeframe,
                "metrics": {},
                "timestamp": datetime.now().isoformat()
            }
            
            # GitHub analysis
            if "github_stars" in metrics:
                try:
                    # Search for repositories related to the technology
                    github_url = "https://api.github.com/search/repositories"
                    params = {
                        "q": f"{technology} in:name,description,topics",
                        "sort": "stars",
                        "order": "desc",
                        "per_page": 10
                    }
                    
                    response = await self.client.get(github_url, params=params)
                    if response.status_code == 200:
                        github_data = response.json()
                        total_stars = sum(repo["stargazers_count"] for repo in github_data.get("items", []))
                        
                        result["metrics"]["github"] = {
                            "total_repositories": github_data.get("total_count", 0),
                            "top_repositories": [
                                {
                                    "name": repo["full_name"],
                                    "stars": repo["stargazers_count"],
                                    "description": repo.get("description", ""),
                                    "language": repo.get("language")
                                }
                                for repo in github_data.get("items", [])[:5]
                            ],
                            "total_stars_top_10": total_stars
                        }
                except Exception as e:
                    result["metrics"]["github"] = {"error": str(e)}
            
            # Stack Overflow analysis
            if "stackoverflow_questions" in metrics:
                try:
                    # Use Stack Exchange API
                    so_url = "https://api.stackexchange.com/2.3/search"
                    params = {
                        "order": "desc",
                        "sort": "activity",
                        "intitle": technology,
                        "site": "stackoverflow"
                    }
                    
                    response = await self.client.get(so_url, params=params)
                    if response.status_code == 200:
                        so_data = response.json()
                        
                        result["metrics"]["stackoverflow"] = {
                            "total_questions": so_data.get("total", 0),
                            "recent_questions": [
                                {
                                    "title": q["title"],
                                    "score": q.get("score", 0),
                                    "view_count": q.get("view_count", 0),
                                    "answer_count": q.get("answer_count", 0),
                                    "tags": q.get("tags", [])
                                }
                                for q in so_data.get("items", [])[:5]
                            ]
                        }
                except Exception as e:
                    result["metrics"]["stackoverflow"] = {"error": str(e)}
            
            # NPM downloads (if technology might be a JS package)
            if "npm_downloads" in metrics:
                try:
                    npm_url = f"https://registry.npmjs.org/{technology}"
                    response = await self.client.get(npm_url)
                    
                    if response.status_code == 200:
                        npm_data = response.json()
                        
                        # Get download stats
                        downloads_url = f"https://api.npmjs.org/downloads/point/last-month/{technology}"
                        downloads_response = await self.client.get(downloads_url)
                        
                        downloads_data = {}
                        if downloads_response.status_code == 200:
                            downloads_data = downloads_response.json()
                        
                        result["metrics"]["npm"] = {
                            "name": npm_data.get("name"),
                            "description": npm_data.get("description"),
                            "version": npm_data.get("dist-tags", {}).get("latest"),
                            "monthly_downloads": downloads_data.get("downloads", 0),
                            "keywords": npm_data.get("keywords", []),
                            "license": npm_data.get("license"),
                            "homepage": npm_data.get("homepage")
                        }
                except Exception as e:
                    result["metrics"]["npm"] = {"error": str(e)}
            
            # Calculate trend analysis
            trend_indicators = []
            
            if "github" in result["metrics"] and "error" not in result["metrics"]["github"]:
                repo_count = result["metrics"]["github"]["total_repositories"]
                if repo_count > 1000:
                    trend_indicators.append("high_github_activity")
                elif repo_count > 100:
                    trend_indicators.append("moderate_github_activity")
            
            if "stackoverflow" in result["metrics"] and "error" not in result["metrics"]["stackoverflow"]:
                question_count = result["metrics"]["stackoverflow"]["total_questions"]
                if question_count > 10000:
                    trend_indicators.append("high_community_interest")
                elif question_count > 1000:
                    trend_indicators.append("moderate_community_interest")
            
            # Overall trend assessment
            if len(trend_indicators) >= 2:
                overall_trend = "rising"
            elif len(trend_indicators) == 1:
                overall_trend = "stable"
            else:
                overall_trend = "emerging"
            
            result["analysis"] = {
                "overall_trend": overall_trend,
                "indicators": trend_indicators,
                "confidence": len(trend_indicators) / len(metrics) if metrics else 0
            }
            
            # Cache for 2 hours
            await self.cache.set(cache_key, result, 7200)
            
            logger.info("Tech trends analyzed", technology=technology, trend=overall_trend)
            return result
            
        except Exception as e:
            logger.error("Failed to analyze tech trends", technology=technology, error=str(e))
            return {
                "error": f"Failed to analyze trends for {technology}: {str(e)}",
                "technology": technology,
                "timestamp": datetime.now().isoformat()
            } 