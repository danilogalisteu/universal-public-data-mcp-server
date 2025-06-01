"""
News and media data adapter using real RSS feeds and news APIs.
"""

import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

import httpx
import structlog
import feedparser
from xml.etree import ElementTree as ET

from core.cache import CacheManager

logger = structlog.get_logger(__name__)

class NewsDataAdapter:
    """Adapter for news and media data sources using real APIs."""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache = cache_manager
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={"User-Agent": "Universal-Public-Data-MCP/1.0"}
        )
        
        # RSS feed sources
        self.rss_feeds = {
            "general": [
                "http://feeds.bbci.co.uk/news/rss.xml",
                "https://feeds.reuters.com/reuters/topNews",
                "https://feeds.npr.org/1001/feed.json",
                "https://rss.cnn.com/rss/edition.rss"
            ],
            "business": [
                "http://feeds.bbci.co.uk/news/business/rss.xml",
                "https://feeds.reuters.com/reuters/businessNews",
                "https://feeds.bloomberg.com/markets/index.xml"
            ],
            "technology": [
                "http://feeds.bbci.co.uk/news/technology/rss.xml", 
                "https://feeds.reuters.com/reuters/technologyNews",
                "https://feeds.ars-technica.com/arstechnica/index",
                "https://feeds.techcrunch.com/TechCrunch/"
            ],
            "science": [
                "http://feeds.bbci.co.uk/news/science_and_environment/rss.xml",
                "https://feeds.reuters.com/reuters/scienceNews",
                "https://www.science.org/rss/news_current.xml"
            ],
            "health": [
                "http://feeds.bbci.co.uk/news/health/rss.xml",
                "https://feeds.reuters.com/reuters/healthNews"
            ],
            "sports": [
                "http://feeds.bbci.co.uk/sport/rss.xml",
                "https://feeds.reuters.com/reuters/sportsNews"
            ]
        }
    
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def get_breaking_news(
        self, 
        category: str = "general", 
        limit: int = 10, 
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Get breaking news from multiple RSS sources.
        
        Args:
            category: News category
            limit: Number of articles to return
            language: Language for news (only 'en' supported currently)
        """
        try:
            cache_key = f"breaking_news:{category}:{limit}:{language}"
            cached_result = await self.cache.get(cache_key)
            if cached_result:
                return cached_result
            
            if category not in self.rss_feeds:
                return {
                    "error": f"Category '{category}' not supported. Available: {list(self.rss_feeds.keys())}",
                    "category": category,
                    "timestamp": datetime.now().isoformat()
                }
            
            articles = []
            feed_urls = self.rss_feeds[category]
            
            # Fetch from multiple RSS feeds
            for feed_url in feed_urls:
                try:
                    response = await self.client.get(feed_url)
                    response.raise_for_status()
                    
                    # Parse RSS feed
                    feed = feedparser.parse(response.text)
                    
                    for entry in feed.entries:
                        # Extract article data
                        article = {
                            "title": getattr(entry, 'title', ''),
                            "description": getattr(entry, 'description', '') or getattr(entry, 'summary', ''),
                            "link": getattr(entry, 'link', ''),
                            "published": getattr(entry, 'published', ''),
                            "source": feed.feed.get('title', feed_url),
                            "author": getattr(entry, 'author', ''),
                        }
                        
                        # Parse published date
                        if hasattr(entry, 'published_parsed') and entry.published_parsed:
                            try:
                                pub_time = datetime(*entry.published_parsed[:6])
                                article["published_timestamp"] = pub_time.isoformat()
                                article["hours_ago"] = (datetime.now() - pub_time).total_seconds() / 3600
                            except:
                                pass
                        
                        articles.append(article)
                        
                        # Stop if we have enough articles
                        if len(articles) >= limit * 2:  # Get extra to sort by recency
                            break
                    
                except Exception as e:
                    logger.warning("Failed to fetch RSS feed", feed_url=feed_url, error=str(e))
                    continue
            
            # Sort by publication time (most recent first)
            articles.sort(key=lambda x: x.get("hours_ago", float('inf')))
            
            result = {
                "category": category,
                "limit": limit,
                "language": language,
                "articles_found": len(articles),
                "articles": articles[:limit],
                "sources": list(set(article.get("source", "") for article in articles[:limit])),
                "timestamp": datetime.now().isoformat()
            }
            
            # Cache for 15 minutes (news changes frequently)
            await self.cache.set(cache_key, result, 900)
            
            logger.info("Breaking news retrieved", category=category, count=len(articles[:limit]))
            return result
            
        except Exception as e:
            logger.error("Failed to get breaking news", category=category, error=str(e))
            return {
                "error": f"Failed to get breaking news: {str(e)}",
                "category": category,
                "timestamp": datetime.now().isoformat()
            }
    
    async def search_news(
        self, 
        query: str, 
        timeframe: str = "24h", 
        sources: Optional[List[str]] = None, 
        limit: int = 15
    ) -> Dict[str, Any]:
        """
        Search news articles by topic across RSS feeds.
        
        Args:
            query: Search query for news articles
            timeframe: Time period for search
            sources: Specific news sources to search
            limit: Number of articles to return
        """
        try:
            cache_key = f"news_search:{query}:{timeframe}:{sources or 'all'}:{limit}"
            cached_result = await self.cache.get(cache_key)
            if cached_result:
                return cached_result
            
            # Calculate time cutoff
            now = datetime.now()
            if timeframe == "1h":
                cutoff = now - timedelta(hours=1)
            elif timeframe == "6h":
                cutoff = now - timedelta(hours=6)
            elif timeframe == "24h":
                cutoff = now - timedelta(hours=24)
            elif timeframe == "3d":
                cutoff = now - timedelta(days=3)
            elif timeframe == "1w":
                cutoff = now - timedelta(weeks=1)
            elif timeframe == "1m":
                cutoff = now - timedelta(days=30)
            else:
                cutoff = now - timedelta(hours=24)
            
            matching_articles = []
            search_terms = query.lower().split()
            
            # Search across all categories if no sources specified
            feed_categories = ["general", "business", "technology", "science", "health"]
            
            for category in feed_categories:
                for feed_url in self.rss_feeds[category]:
                    try:
                        response = await self.client.get(feed_url)
                        response.raise_for_status()
                        
                        feed = feedparser.parse(response.text)
                        
                        for entry in feed.entries:
                            # Check if article matches search terms
                            title = getattr(entry, 'title', '').lower()
                            description = getattr(entry, 'description', '').lower() or getattr(entry, 'summary', '').lower()
                            content = f"{title} {description}"
                            
                            # Simple keyword matching
                            matches = sum(1 for term in search_terms if term in content)
                            if matches == 0:
                                continue
                            
                            # Check publication time
                            article_time = None
                            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                                try:
                                    article_time = datetime(*entry.published_parsed[:6])
                                except:
                                    pass
                            
                            # Skip if outside timeframe
                            if article_time and article_time < cutoff:
                                continue
                            
                            article = {
                                "title": getattr(entry, 'title', ''),
                                "description": getattr(entry, 'description', '') or getattr(entry, 'summary', ''),
                                "link": getattr(entry, 'link', ''),
                                "published": getattr(entry, 'published', ''),
                                "source": feed.feed.get('title', feed_url),
                                "category": category,
                                "relevance_score": matches / len(search_terms),
                                "match_count": matches
                            }
                            
                            if article_time:
                                article["published_timestamp"] = article_time.isoformat()
                                article["hours_ago"] = (now - article_time).total_seconds() / 3600
                            
                            matching_articles.append(article)
                            
                    except Exception as e:
                        logger.warning("Failed to search RSS feed", feed_url=feed_url, error=str(e))
                        continue
            
            # Sort by relevance and recency
            matching_articles.sort(key=lambda x: (-x.get("relevance_score", 0), x.get("hours_ago", float('inf'))))
            
            result = {
                "query": query,
                "timeframe": timeframe,
                "sources": sources,
                "limit": limit,
                "articles_found": len(matching_articles),
                "articles": matching_articles[:limit],
                "search_summary": {
                    "total_matches": len(matching_articles),
                    "avg_relevance": sum(a.get("relevance_score", 0) for a in matching_articles[:limit]) / min(len(matching_articles), limit) if matching_articles else 0,
                    "categories_searched": feed_categories
                },
                "timestamp": datetime.now().isoformat()
            }
            
            # Cache for 30 minutes
            await self.cache.set(cache_key, result, 1800)
            
            logger.info("News search completed", query=query, matches=len(matching_articles))
            return result
            
        except Exception as e:
            logger.error("Failed to search news", query=query, error=str(e))
            return {
                "error": f"Failed to search news: {str(e)}",
                "query": query,
                "timestamp": datetime.now().isoformat()
            }
    
    async def analyze_media_sentiment(
        self, 
        topic: str, 
        timeframe: str = "24h"
    ) -> Dict[str, Any]:
        """
        Analyze sentiment of news articles about a topic.
        
        Args:
            topic: Topic to analyze sentiment for
            timeframe: Time period for analysis
        """
        try:
            cache_key = f"sentiment:{topic}:{timeframe}"
            cached_result = await self.cache.get(cache_key)
            if cached_result:
                return cached_result
            
            # First, search for articles about the topic
            news_result = await self.search_news(topic, timeframe, limit=50)
            
            if "error" in news_result:
                return {
                    "error": f"Failed to find articles for sentiment analysis: {news_result['error']}",
                    "topic": topic,
                    "timestamp": datetime.now().isoformat()
                }
            
            articles = news_result.get("articles", [])
            
            if not articles:
                return {
                    "topic": topic,
                    "timeframe": timeframe,
                    "sentiment": "neutral",
                    "confidence": 0,
                    "articles_analyzed": 0,
                    "message": "No articles found for sentiment analysis",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Simple sentiment analysis based on keywords
            positive_words = [
                "good", "great", "excellent", "positive", "success", "win", "growth", "improve", 
                "increase", "gain", "benefit", "advance", "breakthrough", "achievement", "rise",
                "boost", "surge", "soar", "triumph", "progress", "upgrade", "enhance"
            ]
            
            negative_words = [
                "bad", "terrible", "negative", "failure", "lose", "decline", "decrease", "fall",
                "drop", "crash", "crisis", "problem", "issue", "concern", "worry", "fear",
                "plunge", "tumble", "collapse", "scandal", "controversy", "threat", "risk"
            ]
            
            sentiment_scores = []
            article_sentiments = []
            
            for article in articles:
                content = f"{article.get('title', '')} {article.get('description', '')}".lower()
                
                positive_count = sum(1 for word in positive_words if word in content)
                negative_count = sum(1 for word in negative_words if word in content)
                
                # Calculate sentiment score (-1 to 1)
                total_sentiment_words = positive_count + negative_count
                if total_sentiment_words > 0:
                    score = (positive_count - negative_count) / total_sentiment_words
                else:
                    score = 0
                
                sentiment_scores.append(score)
                
                # Classify sentiment
                if score > 0.2:
                    sentiment = "positive"
                elif score < -0.2:
                    sentiment = "negative"
                else:
                    sentiment = "neutral"
                
                article_sentiments.append({
                    "title": article.get("title", ""),
                    "sentiment": sentiment,
                    "score": score,
                    "positive_words": positive_count,
                    "negative_words": negative_count,
                    "source": article.get("source", "")
                })
            
            # Calculate overall sentiment
            if sentiment_scores:
                avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
                confidence = min(abs(avg_sentiment) * 2, 1.0)  # Scale to 0-1
                
                if avg_sentiment > 0.1:
                    overall_sentiment = "positive"
                elif avg_sentiment < -0.1:
                    overall_sentiment = "negative"
                else:
                    overall_sentiment = "neutral"
            else:
                avg_sentiment = 0
                overall_sentiment = "neutral"
                confidence = 0
            
            # Calculate distribution
            positive_articles = sum(1 for s in sentiment_scores if s > 0.2)
            negative_articles = sum(1 for s in sentiment_scores if s < -0.2)
            neutral_articles = len(sentiment_scores) - positive_articles - negative_articles
            
            result = {
                "topic": topic,
                "timeframe": timeframe,
                "sentiment": overall_sentiment,
                "sentiment_score": avg_sentiment,
                "confidence": confidence,
                "articles_analyzed": len(articles),
                "distribution": {
                    "positive": positive_articles,
                    "negative": negative_articles,
                    "neutral": neutral_articles,
                    "positive_percentage": (positive_articles / len(articles)) * 100 if articles else 0,
                    "negative_percentage": (negative_articles / len(articles)) * 100 if articles else 0
                },
                "sample_articles": article_sentiments[:10],  # Top 10 for review
                "analysis_method": "keyword-based sentiment analysis",
                "timestamp": datetime.now().isoformat()
            }
            
            # Cache for 1 hour
            await self.cache.set(cache_key, result, 3600)
            
            logger.info("Media sentiment analyzed", topic=topic, sentiment=overall_sentiment, articles=len(articles))
            return result
            
        except Exception as e:
            logger.error("Failed to analyze media sentiment", topic=topic, error=str(e))
            return {
                "error": f"Failed to analyze media sentiment: {str(e)}",
                "topic": topic,
                "timestamp": datetime.now().isoformat()
            } 