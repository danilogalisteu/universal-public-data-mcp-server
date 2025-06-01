"""
Real-time data streaming capabilities for Universal Public Data MCP Server.
Supports WebSocket connections and live data feeds.
"""

import asyncio
import json
from typing import Dict, Any, Optional, Callable, Set
from datetime import datetime
import weakref

import structlog

logger = structlog.get_logger(__name__)

class DataStream:
    """Manages real-time data streaming for specific data sources."""
    
    def __init__(self, stream_id: str, data_source: str, update_interval: int = 30):
        self.stream_id = stream_id
        self.data_source = data_source
        self.update_interval = update_interval
        self.is_active = False
        self.subscribers: Set[Callable] = set()
        self.last_data = None
        self.task: Optional[asyncio.Task] = None
        
    async def start(self):
        """Start the data stream."""
        if self.is_active:
            return
            
        self.is_active = True
        self.task = asyncio.create_task(self._stream_loop())
        logger.info("Data stream started", stream_id=self.stream_id, source=self.data_source)
    
    async def stop(self):
        """Stop the data stream."""
        self.is_active = False
        if self.task:
            self.task.cancel()
        logger.info("Data stream stopped", stream_id=self.stream_id)
    
    def subscribe(self, callback: Callable[[Dict[str, Any]], None]):
        """Subscribe to stream updates."""
        self.subscribers.add(callback)
        
        # Send last data immediately if available
        if self.last_data:
            try:
                callback(self.last_data)
            except Exception as e:
                logger.warning("Subscriber callback failed", error=str(e))
    
    def unsubscribe(self, callback: Callable):
        """Unsubscribe from stream updates."""
        self.subscribers.discard(callback)
    
    async def _stream_loop(self):
        """Main streaming loop."""
        while self.is_active:
            try:
                # Fetch fresh data based on source type
                new_data = await self._fetch_data()
                
                if new_data and new_data != self.last_data:
                    self.last_data = new_data
                    await self._notify_subscribers(new_data)
                
                await asyncio.sleep(self.update_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Stream loop error", stream_id=self.stream_id, error=str(e))
                await asyncio.sleep(5)  # Brief pause before retry
    
    async def _fetch_data(self) -> Optional[Dict[str, Any]]:
        """Fetch fresh data for this stream."""
        # This would be implemented based on the specific data source
        # For now, return a placeholder
        return {
            "stream_id": self.stream_id,
            "source": self.data_source,
            "timestamp": datetime.now().isoformat(),
            "data": f"Live data from {self.data_source}"
        }
    
    async def _notify_subscribers(self, data: Dict[str, Any]):
        """Notify all subscribers of new data."""
        failed_callbacks = []
        
        for callback in self.subscribers:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(data)
                else:
                    callback(data)
            except Exception as e:
                logger.warning("Subscriber notification failed", error=str(e))
                failed_callbacks.append(callback)
        
        # Remove failed callbacks
        for callback in failed_callbacks:
            self.subscribers.discard(callback)

class StreamManager:
    """Manages multiple data streams."""
    
    def __init__(self):
        self.streams: Dict[str, DataStream] = {}
        self.stream_configs = {
            "live_stock_prices": {
                "source": "financial",
                "interval": 60,  # 1 minute
                "description": "Real-time stock price updates"
            },
            "earthquake_alerts": {
                "source": "geographic", 
                "interval": 300,  # 5 minutes
                "description": "Live earthquake monitoring"
            },
            "nasa_iss_location": {
                "source": "scientific",
                "interval": 30,  # 30 seconds
                "description": "International Space Station location"
            },
            "breaking_news": {
                "source": "news",
                "interval": 180,  # 3 minutes  
                "description": "Breaking news updates"
            }
        }
    
    async def create_stream(self, stream_id: str, custom_config: Optional[Dict[str, Any]] = None) -> DataStream:
        """Create a new data stream."""
        if stream_id in self.streams:
            return self.streams[stream_id]
        
        # Use predefined config or custom config
        if stream_id in self.stream_configs:
            config = self.stream_configs[stream_id]
        elif custom_config:
            config = custom_config
        else:
            raise ValueError(f"No configuration found for stream: {stream_id}")
        
        stream = DataStream(
            stream_id=stream_id,
            data_source=config["source"],
            update_interval=config["interval"]
        )
        
        self.streams[stream_id] = stream
        logger.info("Stream created", stream_id=stream_id, config=config)
        return stream
    
    async def start_stream(self, stream_id: str) -> bool:
        """Start a specific stream."""
        if stream_id not in self.streams:
            try:
                await self.create_stream(stream_id)
            except ValueError as e:
                logger.error("Failed to create stream", stream_id=stream_id, error=str(e))
                return False
        
        await self.streams[stream_id].start()
        return True
    
    async def stop_stream(self, stream_id: str) -> bool:
        """Stop a specific stream."""
        if stream_id in self.streams:
            await self.streams[stream_id].stop()
            return True
        return False
    
    async def stop_all_streams(self):
        """Stop all active streams."""
        for stream in self.streams.values():
            await stream.stop()
    
    def get_stream_status(self) -> Dict[str, Any]:
        """Get status of all streams."""
        return {
            "active_streams": len([s for s in self.streams.values() if s.is_active]),
            "total_streams": len(self.streams),
            "streams": {
                stream_id: {
                    "active": stream.is_active,
                    "subscribers": len(stream.subscribers),
                    "source": stream.data_source,
                    "interval": stream.update_interval,
                    "last_update": stream.last_data.get("timestamp") if stream.last_data else None
                }
                for stream_id, stream in self.streams.items()
            },
            "available_streams": list(self.stream_configs.keys())
        }

# Global stream manager instance
stream_manager = StreamManager() 