# Third Person Perspective Interface

**"It"** - Observing system behavior and activity over time.

---

## The Three Perspectives

| Perspective | Question | Focus |
|-------------|----------|-------|
| **First ("I")** | "What do I see/do?" | Acting on shared stage |
| **Second ("You")** | "What is the data?" | Querying system state |
| **Third ("It")** | "What is happening?" | Observing system activity |

---

## Distinction from Second Person

| Second Person (`you.*`) | Third Person (`it.*`) |
|------------------------|----------------------|
| Query **data/state** | Observe **activity/behavior** |
| Logs (the data) | Events (the flow) |
| Workers (what exists) | Activity (what's happening) |
| Trace (execution record) | Timeline (sequence of events) |
| **Static** queries | **Dynamic** observation |

---

## Interface Definition

```python
from typing import Protocol, List, Dict, Any
from datetime import datetime


class IThirdPersonPerspective(Protocol):
    """
    "It" - Observing system activity and behavior.
    
    Not what the data IS, but what is HAPPENING.
    """
    
    @property
    def events(self) -> 'IEvents': ...
    
    @property
    def activity(self) -> 'IActivity': ...


class IEvents(Protocol):
    """
    Observing system events flow.
    """
    
    def stream(self, filter: Dict = None) -> Iterator[Dict]:
        """Stream events as they happen."""
        ...
    
    def recent(self, limit: int = 100) -> List[Dict]:
        """Get recent events."""
        ...
    
    def between(self, start: datetime, end: datetime) -> List[Dict]:
        """Get events in time range."""
        ...
    
    def by_type(self, event_type: str, limit: int = 100) -> List[Dict]:
        """Get events of specific type."""
        ...


class IActivity(Protocol):
    """
    Observing system activity patterns.
    """
    
    def timeline(self, limit: int = 100) -> List[Dict]:
        """Timeline of all activity."""
        ...
    
    def compare_runs(self, run_id_1: str, run_id_2: str) -> Dict:
        """Compare activity between two runs."""
        ...
    
    def analyze_sequence(self, flow_index: str) -> Dict:
        """Analyze the sequence of events for an inference."""
        ...
    
    def get_patterns(self) -> List[Dict]:
        """Identify recurring activity patterns."""
        ...
```

---

## Usage Examples

```python
class CanvasAI:
    me: IFirstPersonPerspective   # Shared stage
    you: ISecondPersonPerspective  # Query data
    it: IThirdPersonPerspective    # Observe activity
    
    
    def understand_what_happened(self, flow_index: str):
        """Combine all perspectives to understand an issue."""
        
        # SECOND PERSON: Get the data
        trace = you.history.get_trace(flow_index)
        logs = you.blackboard.get_logs()
        
        # THIRD PERSON: Observe what happened
        timeline = it.activity.timeline(limit=50)
        events = it.events.by_type("error", limit=10)
        
        # FIRST PERSON: Report findings
        me.say(f"Trace shows: {trace}")
        me.say(f"Events during execution: {len(timeline)}")
    
    
    def watch_execution(self):
        """Stream events as they happen."""
        
        for event in it.events.stream():
            # Observe activity in real-time
            if event['type'] == 'node:computed':
                me.say(f"Node computed: {event['flow_index']}")
```

---

## Summary

```
┌───────────────────────────────────────────────────────────────────────────┐
│                                                                           │
│   "I" (First)       "You" (Second)                 "It" (Third)          │
│   ───────────       ──────────────                 ───────────           │
│   SHARED STAGE      DIRECT TOOLS                   OBSERVE ACTIVITY      │
│                                                                           │
│   me.vision.*       DATA: files, blackboard,       it.events.*           │
│   me.hands.*              parser, graph, db        it.activity.*         │
│   me.mind.*                                                               │
│                     EXEC: code, llm, prompt                               │
│                                                                           │
│                     MODEL: paradigm, model,                               │
│                            compose, perceive,                             │
│                            format                                         │
│                                                                           │
│                     OTHER: input, system,                                 │
│                            history                                        │
│                                                                           │
│   "What do I do?"   "What tools can I use?"        "What's happening?"   │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘
```

---
