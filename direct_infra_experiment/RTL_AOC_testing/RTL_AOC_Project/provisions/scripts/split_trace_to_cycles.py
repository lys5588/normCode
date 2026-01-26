"""
Split Trace to Cycles Script
Splits an RTL simulation trace into discrete cycle-by-cycle events.
"""

from typing import Dict, List, Any
import json

def split_to_cycles(trace: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Split an RTL trace into discrete cycles.
    
    Args:
        trace: Dict with 'events' list and 'metadata'
               Each event has 'time' (cycle number) and signal data
    
    Returns:
        List of dicts, one per cycle:
        [
            {"cycle_num": 0, "events": [...]},
            {"cycle_num": 1, "events": [...]},
            ...
        ]
    """
    events = trace.get("events", [])
    
    # Group events by cycle
    cycles_dict: Dict[int, List[Dict]] = {}
    for event in events:
        cycle = event.get("time", 0)
        if cycle not in cycles_dict:
            cycles_dict[cycle] = []
        cycles_dict[cycle].append(event)
    
    # Convert to sorted list
    result = []
    for cycle_num in sorted(cycles_dict.keys()):
        result.append({
            "cycle_num": cycle_num,
            "events": cycles_dict[cycle_num]
        })
    
    return result

def main(input_1: str) -> List[Dict[str, Any]]:
    """Entry point for NormCode execution."""
    # Parse JSON string input
    if isinstance(input_1, str):
        trace = json.loads(input_1)
    else:
        trace = input_1
    return split_to_cycles(trace)

