"""
Hands faculty for First Person perspective.

"My hands" - what I can manipulate (actions that change UI state).
"""

import logging
from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING

from ..types import ActionResult
from ..event_store import EventStore

if TYPE_CHECKING:
    from services.execution.controller import ExecutionController
    from ..facades.system import ServiceContainer

logger = logging.getLogger(__name__)


class Hands:
    """
    What I can manipulate - all ACTION operations.
    
    Hands CHANGE state. Every method returns ActionResult.
    All actions emit WebSocket events to the frontend.
    """
    
    def __init__(
        self,
        emit: Callable[[str, Dict], None],
        execution_getter: Optional[Callable[[], Optional["ExecutionController"]]],
        services: "ServiceContainer",
        event_store: EventStore
    ):
        self._emit = emit
        self._execution_getter = execution_getter
        self._services = services
        self._event_store = event_store
    
    def _do_emit(self, event_type: str, data: Dict[str, Any]) -> None:
        """Emit event and record it."""
        try:
            self._emit(event_type, data)
            self._event_store.record(event_type, data)
        except Exception as e:
            logger.error(f"Failed to emit {event_type}: {e}")
    
    def _emit_canvas_command(self, command_type: str, params: Dict[str, Any]) -> None:
        """
        Emit a canvas command in the format expected by the frontend.
        
        The frontend handles canvas operations via 'canvas:command' events
        with a 'type' field specifying the operation and 'params' for arguments.
        
        We also record the semantic event name for the event store (Third Person).
        """
        # Emit in frontend-expected format
        self._emit("canvas:command", {"type": command_type, "params": params})
        # Record with semantic name for event store / observation
        self._event_store.record(f"canvas:{command_type}", params)
    
    # =========================================================================
    # Node Interaction
    # =========================================================================
    
    def click_node(self, node_id: str) -> ActionResult:
        """Click/select a node."""
        self._emit_canvas_command("select_node", {"node_id": node_id})
        return ActionResult.ok("click_node", f"Clicked node {node_id}", node_id=node_id)
    
    def double_click_node(self, node_id: str) -> ActionResult:
        """Double-click a node (open details)."""
        self._emit_canvas_command("double_click_node", {"node_id": node_id})
        return ActionResult.ok("double_click_node", f"Double-clicked node {node_id}")
    
    def right_click_node(self, node_id: str) -> ActionResult:
        """Right-click a node (context menu)."""
        self._emit_canvas_command("right_click_node", {"node_id": node_id})
        return ActionResult.ok("right_click_node", f"Right-clicked node {node_id}")
    
    def hover_node(self, node_id: str) -> ActionResult:
        """Hover over a node (show tooltip)."""
        self._emit_canvas_command("hover_node", {"node_id": node_id})
        return ActionResult.ok("hover_node", f"Hovering over node {node_id}")
    
    def drag_node(self, node_id: str, to_x: float, to_y: float) -> ActionResult:
        """Drag a node to a new position."""
        self._emit_canvas_command("drag_node", {"node_id": node_id, "x": to_x, "y": to_y})
        return ActionResult.ok("drag_node", f"Dragged node {node_id} to ({to_x}, {to_y})")
    
    def select_nodes(self, node_ids: List[str]) -> ActionResult:
        """Select multiple nodes."""
        self._emit_canvas_command("select_nodes", {"node_ids": node_ids})
        return ActionResult.ok("select_nodes", f"Selected {len(node_ids)} nodes")
    
    def deselect_all(self) -> ActionResult:
        """Clear all selections."""
        self._emit_canvas_command("deselect_all", {})
        return ActionResult.ok("deselect_all", "Deselected all nodes")
    
    # =========================================================================
    # Graph Structure
    # =========================================================================
    
    def collapse_node(self, node_id: str) -> ActionResult:
        """Collapse a node (hide its descendants)."""
        self._emit_canvas_command("collapse_node", {"node_id": node_id})
        return ActionResult.ok("collapse_node", f"Collapsed node {node_id}")
    
    def expand_node(self, node_id: str) -> ActionResult:
        """Expand a collapsed node."""
        self._emit_canvas_command("expand_node", {"node_id": node_id})
        return ActionResult.ok("expand_node", f"Expanded node {node_id}")
    
    def toggle_collapse(self, node_id: str) -> ActionResult:
        """Toggle collapse state of a node."""
        self._emit_canvas_command("toggle_collapse", {"node_id": node_id})
        return ActionResult.ok("toggle_collapse", f"Toggled collapse for node {node_id}")
    
    def collapse_all(self) -> ActionResult:
        """Collapse all nodes that have children."""
        self._emit_canvas_command("collapse_all", {})
        return ActionResult.ok("collapse_all", "Collapsed all nodes")
    
    def expand_all(self) -> ActionResult:
        """Expand all collapsed nodes."""
        self._emit_canvas_command("expand_all", {})
        return ActionResult.ok("expand_all", "Expanded all nodes")
    
    def collapse_to_level(self, level: int) -> ActionResult:
        """Collapse all nodes at or below a level."""
        self._emit_canvas_command("collapse_to_level", {"level": level})
        return ActionResult.ok("collapse_to_level", f"Collapsed to level {level}")
    
    def highlight_branch(self, node_id: str) -> ActionResult:
        """Highlight the branch (ancestors + descendants) of a node."""
        self._emit_canvas_command("highlight_branch", {"node_id": node_id})
        return ActionResult.ok("highlight_branch", f"Highlighted branch for {node_id}")
    
    def clear_highlight(self) -> ActionResult:
        """Clear branch highlighting."""
        self._emit_canvas_command("clear_highlight", {})
        return ActionResult.ok("clear_highlight", "Cleared highlighting")
    
    # =========================================================================
    # View Navigation
    # =========================================================================
    
    def zoom_in(self, amount: float = 0.1) -> ActionResult:
        """Zoom in the canvas."""
        self._emit_canvas_command("zoom_in", {"amount": amount})
        return ActionResult.ok("zoom_in", f"Zoomed in by {amount}")
    
    def zoom_out(self, amount: float = 0.1) -> ActionResult:
        """Zoom out the canvas."""
        self._emit_canvas_command("zoom_out", {"amount": amount})
        return ActionResult.ok("zoom_out", f"Zoomed out by {amount}")
    
    def zoom_to(self, level: float) -> ActionResult:
        """Zoom to specific level (1.0 = 100%)."""
        self._emit_canvas_command("zoom_to", {"level": level})
        return ActionResult.ok("zoom_to", f"Zoomed to {level:.0%}")
    
    def pan(self, dx: float, dy: float) -> ActionResult:
        """Pan the canvas view."""
        self._emit_canvas_command("pan", {"dx": dx, "dy": dy})
        return ActionResult.ok("pan", f"Panned by ({dx}, {dy})")
    
    def fit_view(self) -> ActionResult:
        """Fit all nodes in the viewport."""
        self._emit_canvas_command("fit_view", {})
        return ActionResult.ok("fit_view", "Fit view to all nodes")
    
    def center_on_node(self, node_id: str) -> ActionResult:
        """Center the view on a specific node."""
        self._emit_canvas_command("center_on_node", {"node_id": node_id})
        return ActionResult.ok("center_on_node", f"Centered on node {node_id}")
    
    # =========================================================================
    # Panel Manipulation
    # =========================================================================
    
    def open_panel(self, panel: str) -> ActionResult:
        """Open a panel."""
        self._do_emit("panel:open", {"panel": panel})
        return ActionResult.ok("open_panel", f"Opened {panel} panel")
    
    def close_panel(self, panel: str) -> ActionResult:
        """Close a panel."""
        self._do_emit("panel:close", {"panel": panel})
        return ActionResult.ok("close_panel", f"Closed {panel} panel")
    
    def toggle_panel(self, panel: str) -> ActionResult:
        """Toggle a panel open/closed."""
        self._do_emit("panel:toggle", {"panel": panel})
        return ActionResult.ok("toggle_panel", f"Toggled {panel} panel")
    
    def focus_panel(self, panel: str) -> ActionResult:
        """Focus a panel (make it active)."""
        self._do_emit("panel:focus", {"panel": panel})
        return ActionResult.ok("focus_panel", f"Focused {panel} panel")
    
    # =========================================================================
    # Chat Interaction
    # =========================================================================
    
    def type_in_chat(self, text: str) -> ActionResult:
        """Type text in the chat input field."""
        self._do_emit("chat:type", {"text": text})
        return ActionResult.ok("type_in_chat", f"Typed in chat: {text[:50]}...")
    
    def clear_chat_input(self) -> ActionResult:
        """Clear the chat input field."""
        self._do_emit("chat:clear_input", {})
        return ActionResult.ok("clear_chat_input", "Cleared chat input")
    
    def send_chat_message(self) -> ActionResult:
        """Send the current chat input (press Enter)."""
        self._do_emit("chat:send", {})
        return ActionResult.ok("send_chat_message", "Sent chat message")
    
    def say(self, message: str) -> ActionResult:
        """Type and send a message in one action."""
        self._do_emit("chat:message", {"content": message, "role": "assistant"})
        return ActionResult.ok("say", f"Said: {message[:50]}...")
    
    def respond_to_prompt(self, response: str) -> ActionResult:
        """Respond to a pending input request."""
        self._do_emit("chat:respond", {"response": response})
        return ActionResult.ok("respond_to_prompt", f"Responded: {response[:50]}...")
    
    def select_prompt_option(self, option: str) -> ActionResult:
        """Select an option from a pending select prompt."""
        self._do_emit("chat:select_option", {"option": option})
        return ActionResult.ok("select_prompt_option", f"Selected: {option}")
    
    def scroll_chat(self, direction: str, amount: int = 1) -> ActionResult:
        """Scroll chat panel ("up" or "down")."""
        self._do_emit("chat:scroll", {"direction": direction, "amount": amount})
        return ActionResult.ok("scroll_chat", f"Scrolled chat {direction}")
    
    # =========================================================================
    # Button & Keyboard
    # =========================================================================
    
    def click_button(self, button_id: str) -> ActionResult:
        """Click a UI button."""
        self._do_emit("ui:click_button", {"button_id": button_id})
        return ActionResult.ok("click_button", f"Clicked button: {button_id}")
    
    def press_key(self, key: str, modifiers: Optional[List[str]] = None) -> ActionResult:
        """Press a keyboard key."""
        self._do_emit("ui:press_key", {"key": key, "modifiers": modifiers or []})
        return ActionResult.ok("press_key", f"Pressed: {key}")
    
    def keyboard_shortcut(self, shortcut: str) -> ActionResult:
        """Execute a keyboard shortcut."""
        self._do_emit("ui:shortcut", {"shortcut": shortcut})
        return ActionResult.ok("keyboard_shortcut", f"Executed: {shortcut}")
    
    # =========================================================================
    # Breakpoints
    # =========================================================================
    
    def toggle_breakpoint(self, node_id: str) -> ActionResult:
        """Toggle breakpoint on a node."""
        self._do_emit("execution:toggle_breakpoint", {"node_id": node_id})
        return ActionResult.ok("toggle_breakpoint", f"Toggled breakpoint on {node_id}")
    
    def add_breakpoint(self, node_id: str) -> ActionResult:
        """Add breakpoint to a node."""
        self._do_emit("execution:add_breakpoint", {"node_id": node_id})
        return ActionResult.ok("add_breakpoint", f"Added breakpoint to {node_id}")
    
    def remove_breakpoint(self, node_id: str) -> ActionResult:
        """Remove breakpoint from a node."""
        self._do_emit("execution:remove_breakpoint", {"node_id": node_id})
        return ActionResult.ok("remove_breakpoint", f"Removed breakpoint from {node_id}")
    
    def clear_all_breakpoints(self) -> ActionResult:
        """Clear all breakpoints."""
        self._do_emit("execution:clear_breakpoints", {})
        return ActionResult.ok("clear_all_breakpoints", "Cleared all breakpoints")
    
    # =========================================================================
    # Display (from old CanvasDisplayTool)
    # =========================================================================
    
    def show_source(self, code: str, language: str = "python") -> ActionResult:
        """Display source code in the editor."""
        self._do_emit("editor:show_source", {"code": code, "language": language})
        return ActionResult.ok("show_source", "Displayed source code")
    
    def show_artifact(self, artifact_type: str, data: Any) -> ActionResult:
        """Display an artifact."""
        self._do_emit("artifact:show", {"type": artifact_type, "data": data})
        return ActionResult.ok("show_artifact", f"Displayed {artifact_type}")

