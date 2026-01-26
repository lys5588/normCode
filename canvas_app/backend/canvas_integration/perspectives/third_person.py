"""
Third Person Perspective - "What is happening"

Observing system behavior and activity over time.
Meta-level observation of the system.
"""

from typing import Dict, Iterator, List, Optional
from datetime import datetime

from ..event_store import EventStore


class EventsFacade:
    """
    Observing system events flow.
    """
    
    def __init__(self, event_store: EventStore):
        self._store = event_store
    
    def stream(self, filter: Optional[Dict] = None) -> Iterator[Dict]:
        """
        Stream events as they happen.
        
        Args:
            filter: Optional filter dict with keys:
                - type: Event type to match
                - type_prefix: Event type prefix to match
                
        Yields:
            Events matching the filter
        """
        return self._store.stream(filter)
    
    def recent(self, limit: int = 100) -> List[Dict]:
        """
        Get recent events.
        
        Args:
            limit: Maximum number of events to return
            
        Returns:
            List of recent events (newest last)
        """
        return self._store.recent(limit)
    
    def between(self, start: datetime, end: datetime) -> List[Dict]:
        """
        Get events in time range.
        
        Args:
            start: Start time (inclusive)
            end: End time (inclusive)
            
        Returns:
            List of events in range
        """
        return self._store.between(start, end)
    
    def by_type(self, event_type: str, limit: int = 100) -> List[Dict]:
        """
        Get events of specific type.
        
        Args:
            event_type: Event type to filter by
            limit: Maximum number of events
            
        Returns:
            List of matching events
        """
        return self._store.by_type(event_type, limit)
    
    def by_type_prefix(self, prefix: str, limit: int = 100) -> List[Dict]:
        """
        Get events with type starting with prefix.
        
        Args:
            prefix: Event type prefix (e.g., "execution:" for all execution events)
            limit: Maximum number of events
            
        Returns:
            List of matching events
        """
        return self._store.by_type_prefix(prefix, limit)


class ActivityFacade:
    """
    Observing system activity patterns.
    """
    
    def __init__(self, event_store: EventStore):
        self._store = event_store
    
    def timeline(self, limit: int = 100) -> List[Dict]:
        """
        Timeline of all activity.
        
        Args:
            limit: Maximum events
            
        Returns:
            List of activity events with timing
        """
        events = self._store.recent(limit)
        return [{
            "time": e.get("timestamp"),
            "type": e.get("type"),
            "summary": self._summarize_event(e)
        } for e in events]
    
    def compare_runs(self, run_id_1: str, run_id_2: str) -> Dict:
        """
        Compare activity between two runs.
        
        Args:
            run_id_1: First run ID
            run_id_2: Second run ID
            
        Returns:
            Comparison dict with differences
        """
        # Would need run-specific event storage
        return {
            "run_1": run_id_1,
            "run_2": run_id_2,
            "comparison": "Not yet implemented"
        }
    
    def analyze_sequence(self, flow_index: str) -> Dict:
        """
        Analyze the sequence of events for an inference.
        
        Args:
            flow_index: The flow_index to analyze
            
        Returns:
            Analysis dict with timing and steps
        """
        # Filter events related to this flow_index
        all_events = self._store.recent(1000)
        related = [
            e for e in all_events
            if e.get("data", {}).get("flow_index") == flow_index
        ]
        
        return {
            "flow_index": flow_index,
            "event_count": len(related),
            "events": related[-20:],  # Last 20 events
        }
    
    def get_patterns(self) -> List[Dict]:
        """
        Identify recurring activity patterns.
        
        Returns:
            List of identified patterns
        """
        stats = self._store.stats()
        type_counts = stats.get("by_type", {})
        
        # Sort by frequency
        sorted_types = sorted(type_counts.items(), key=lambda x: -x[1])
        
        return [{
            "pattern": event_type,
            "occurrences": count,
            "percentage": count / max(stats.get("total", 1), 1) * 100
        } for event_type, count in sorted_types[:10]]
    
    def _summarize_event(self, event: Dict) -> str:
        """Create a short summary of an event."""
        event_type = event.get("type", "unknown")
        data = event.get("data", {})
        
        if "node_id" in data:
            return f"{event_type} on {data['node_id']}"
        elif "message" in data:
            msg = data['message']
            return f"{event_type}: {msg[:50]}..."
        elif "content" in data:
            content = data['content']
            return f"{event_type}: {str(content)[:50]}..."
        
        return event_type


class ThirdPersonPerspective:
    """
    "What is happening" - observing system activity.
    
    Not what the data IS, but what is HAPPENING.
    Meta-level observation for debugging and analysis.
    """
    
    def __init__(self, event_store: EventStore):
        """
        Initialize Third Person perspective.
        
        Args:
            event_store: Event store to observe
        """
        self._event_store = event_store
        self._events = EventsFacade(event_store)
        self._activity = ActivityFacade(event_store)
    
    @property
    def events(self) -> EventsFacade:
        """Event stream observation."""
        return self._events
    
    @property
    def activity(self) -> ActivityFacade:
        """Activity pattern analysis."""
        return self._activity

