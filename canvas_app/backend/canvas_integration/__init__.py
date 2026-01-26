"""
Canvas Integration - Unified interface for AI to interact with the Canvas App.

This module provides the three-perspective interface:
- me (First Person): Act as user on shared stage
- you (Second Person): Private backend/tool access  
- it (Third Person): Observe system activity

Usage:
    from canvas_integration import CanvasIntegrationTool
    
    canvas = CanvasIntegrationTool(emit_callback, execution_getter, ...)
    
    # First Person - user sees
    canvas.me.say("Hello")
    snapshot = canvas.me.look()
    
    # Second Person - user doesn't see
    content = canvas.you.files.read("config.json")
    
    # Third Person - observe activity
    events = canvas.it.events.recent()
"""

from .tool import CanvasIntegrationTool
from .types import (
    ActionResult,
    UserViewSnapshot,
    CanvasSnapshot,
    ChatSnapshot,
    ExecutionSnapshot,
    ProjectSnapshot,
    PanelsSnapshot,
    LogsSnapshot,
    NodeDetails,
    VisibleNode,
    VisibleEdge,
)
from .event_store import EventStore
from .injection import (
    create_canvas_integration,
    inject_canvas_integration,
    inject_backward_compatible_tools,
    full_injection,
)

__all__ = [
    # Main tool
    "CanvasIntegrationTool",
    
    # Types
    "ActionResult",
    "UserViewSnapshot",
    "CanvasSnapshot",
    "ChatSnapshot",
    "ExecutionSnapshot",
    "ProjectSnapshot",
    "PanelsSnapshot",
    "LogsSnapshot",
    "NodeDetails",
    "VisibleNode",
    "VisibleEdge",
    
    # Event store
    "EventStore",
    
    # Injection
    "create_canvas_integration",
    "inject_canvas_integration",
    "inject_backward_compatible_tools",
    "full_injection",
]

