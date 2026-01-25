"""
Event Store for Third Person perspective.

Captures and stores events emitted by the canvas integration tool
for later observation and analysis.
"""

import logging
import threading
from collections import deque
from datetime import datetime
from typing import Dict, List, Any, Optional, Iterator, Callable

logger = logging.getLogger(__name__)


class EventStore:
    """
    Event store for Third Person observation.
    
    Captures events emitted by the tool for later analysis.
    Thread-safe for concurrent access.
    """
    
    def __init__(self, max_events: int = 10000):
        """
        Initialize the event store.
        
        Args:
            max_events: Maximum number of events to retain
        """
        self._events: deque = deque(maxlen=max_events)
        self._lock = threading.Lock()
        self._subscribers: List[Callable[[Dict], None]] = []
        self._max_events = max_events
    
    def record(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        Record an event (called by emit wrapper).
        
        Args:
            event_type: Type of event (e.g., "node:computed", "chat:message")
            data: Event payload
        """
        event = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat(),
            "timestamp_epoch": datetime.now().timestamp()
        }
        
        with self._lock:
            self._events.append(event)
        
        # Notify subscribers (outside lock to avoid deadlock)
        for subscriber in self._subscribers:
            try:
                subscriber(event)
            except Exception as e:
                logger.error(f"Event subscriber error: {e}")
    
    def recent(self, limit: int = 100) -> List[Dict]:
        """
        Get recent events.
        
        Args:
            limit: Maximum number of events to return
            
        Returns:
            List of recent events (newest last)
        """
        with self._lock:
            return list(self._events)[-limit:]
    
    def by_type(self, event_type: str, limit: int = 100) -> List[Dict]:
        """
        Get events of a specific type.
        
        Args:
            event_type: Event type to filter by
            limit: Maximum number of events to return
            
        Returns:
            List of matching events (newest last)
        """
        with self._lock:
            matching = [e for e in self._events if e["type"] == event_type]
            return matching[-limit:]
    
    def by_type_prefix(self, prefix: str, limit: int = 100) -> List[Dict]:
        """
        Get events with type starting with prefix.
        
        Args:
            prefix: Event type prefix (e.g., "execution:" for all execution events)
            limit: Maximum number of events to return
            
        Returns:
            List of matching events
        """
        with self._lock:
            matching = [e for e in self._events if e["type"].startswith(prefix)]
            return matching[-limit:]
    
    def between(
        self, 
        start: datetime, 
        end: datetime,
        limit: int = 1000
    ) -> List[Dict]:
        """
        Get events in a time range.
        
        Args:
            start: Start time (inclusive)
            end: End time (inclusive)
            limit: Maximum events to return
            
        Returns:
            List of events in range
        """
        start_ts = start.timestamp()
        end_ts = end.timestamp()
        
        with self._lock:
            matching = [
                e for e in self._events
                if start_ts <= e.get("timestamp_epoch", 0) <= end_ts
            ]
            return matching[-limit:]
    
    def stream(self, filter: Optional[Dict] = None) -> Iterator[Dict]:
        """
        Stream events as they happen.
        
        This is a generator that yields events. It blocks until
        new events arrive. Use in a thread.
        
        Args:
            filter: Optional filter dict with keys:
                - type: Event type to match
                - type_prefix: Event type prefix to match
                
        Yields:
            Events matching the filter
        """
        import time
        
        queue: List[Dict] = []
        
        def on_event(event: Dict):
            if filter is None:
                queue.append(event)
            elif self._matches_filter(event, filter):
                queue.append(event)
        
        self._subscribers.append(on_event)
        try:
            while True:
                if queue:
                    yield queue.pop(0)
                else:
                    time.sleep(0.01)
        finally:
            if on_event in self._subscribers:
                self._subscribers.remove(on_event)
    
    def _matches_filter(self, event: Dict, filter: Dict) -> bool:
        """Check if event matches filter criteria."""
        event_type = event.get("type", "")
        
        if "type" in filter and event_type != filter["type"]:
            return False
        
        if "type_prefix" in filter and not event_type.startswith(filter["type_prefix"]):
            return False
        
        return True
    
    def subscribe(self, callback: Callable[[Dict], None]) -> Callable[[], None]:
        """
        Subscribe to all events.
        
        Args:
            callback: Function to call with each event
            
        Returns:
            Unsubscribe function
        """
        self._subscribers.append(callback)
        
        def unsubscribe():
            if callback in self._subscribers:
                self._subscribers.remove(callback)
        
        return unsubscribe
    
    def clear(self) -> int:
        """
        Clear all events.
        
        Returns:
            Number of events cleared
        """
        with self._lock:
            count = len(self._events)
            self._events.clear()
            return count
    
    def count(self) -> int:
        """Get total event count."""
        with self._lock:
            return len(self._events)
    
    def stats(self) -> Dict[str, Any]:
        """
        Get event statistics.
        
        Returns:
            Dict with event counts by type, total, etc.
        """
        with self._lock:
            type_counts: Dict[str, int] = {}
            for event in self._events:
                event_type = event.get("type", "unknown")
                type_counts[event_type] = type_counts.get(event_type, 0) + 1
            
            return {
                "total": len(self._events),
                "max_capacity": self._max_events,
                "by_type": type_counts,
                "subscriber_count": len(self._subscribers)
            }

