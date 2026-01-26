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
    
    def click_node(self, node_id: str, show_details: bool = True) -> ActionResult:
        """
        Click/select a node and optionally show its details.
        
        Args:
            node_id: The node to select
            show_details: If True (default), also opens the detail panel
        """
        self._emit_canvas_command("select_node", {"node_id": node_id})
        if show_details:
            # Also open detail panel so user sees the node info
            self._do_emit("panel:open", {"panel": "detail"})
            self._do_emit("panel:focus", {"panel": "detail"})
        return ActionResult.ok("click_node", f"Clicked node {node_id}", node_id=node_id)
    
    def double_click_node(self, node_id: str) -> ActionResult:
        """Double-click a node (open details panel)."""
        self._emit_canvas_command("select_node", {"node_id": node_id})
        self._do_emit("panel:open", {"panel": "detail"})
        self._do_emit("panel:focus", {"panel": "detail"})
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
    
    def type_in_chat(self, text) -> ActionResult:
        """Type text in the chat input field."""
        # Handle dict input format
        if isinstance(text, dict):
            if "input_1" in text:
                text = text["input_1"]
            if isinstance(text, dict) and "content" in text:
                text = text["content"]
        text = str(text) if text else ""
        
        self._do_emit("chat:type", {"text": text})
        preview = text[:50] if len(text) > 50 else text
        return ActionResult.ok("type_in_chat", f"Typed in chat: {preview}...")
    
    def clear_chat_input(self) -> ActionResult:
        """Clear the chat input field."""
        self._do_emit("chat:clear_input", {})
        return ActionResult.ok("clear_chat_input", "Cleared chat input")
    
    def send_chat_message(self) -> ActionResult:
        """Send the current chat input (press Enter)."""
        self._do_emit("chat:send", {})
        return ActionResult.ok("send_chat_message", "Sent chat message")
    
    def _extract_message_content(self, message) -> str:
        """
        Extract string content from various input formats.
        
        Handles:
        - Direct strings
        - Dict with 'content' key
        - Dict with 'input_1' containing message dict
        """
        if isinstance(message, dict):
            # Check for nested input format from paradigm: {"input_1": {"content": "..."}}
            if "input_1" in message:
                inner = message["input_1"]
                if isinstance(inner, dict) and "content" in inner:
                    return str(inner["content"])
                else:
                    return str(inner)
            # Check for direct content format: {"content": "..."}
            elif "content" in message:
                return str(message["content"])
            else:
                return str(message)
        return str(message) if message else ""
    
    def say(self, message) -> ActionResult:
        """
        Send a PERMANENT message to chat (added to history).
        
        Use this for actual conversation responses that should persist.
        
        Args:
            message: Either a string, or a dict with 'content' key, 
                     or a dict with 'input_1' containing message dict
        """
        import uuid
        from datetime import datetime
        
        content = self._extract_message_content(message)
        
        # Emit full message object - persists in chat history
        msg_obj = {
            "id": str(uuid.uuid4())[:8],
            "role": "assistant",
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": {"source": "canvas_integration", "persistent": True},
        }
        self._do_emit("chat:message", msg_obj)
        
        preview = content[:50] if len(content) > 50 else content
        return ActionResult.ok("say", f"Said: {preview}...")
    
    def notify(self, message, status_type: str = "info") -> ActionResult:
        """
        Send a TEMPORARY notification/status to chat (NOT added to history).
        
        Use this for ephemeral status updates like:
        - "🔍 Understanding your request..."
        - "⚙️ Executing command..."
        - "💭 Generating response..."
        
        These appear briefly and don't clutter the chat history.
        
        Args:
            message: The notification content
            status_type: Type of status ("thinking", "executing", "generating", "info", "warning", "error")
        """
        content = self._extract_message_content(message)
        
        # Emit as notification - frontend should display temporarily
        self._do_emit("chat:notification", {
            "content": content,
            "type": status_type,
            "metadata": {"source": "canvas_integration", "persistent": False},
        })
        
        preview = content[:50] if len(content) > 50 else content
        return ActionResult.ok("notify", f"Notified: {preview}...")
    
    def status(self, status_type: str, message: Optional[str] = None) -> ActionResult:
        """
        Emit a typed status indicator.
        
        Convenience method for common status types with default messages.
        
        Args:
            status_type: "thinking", "executing", "generating", "success", "error"
            message: Optional custom message (uses default if not provided)
        """
        defaults = {
            "thinking": "🔍 Understanding your request...",
            "executing": "⚙️ Executing command...",
            "generating": "💭 Generating response...",
            "success": "✅ Done!",
            "error": "❌ Something went wrong",
        }
        
        content = message if message else defaults.get(status_type, f"Status: {status_type}")
        content = self._extract_message_content(content)
        
        self._do_emit("chat:status", {
            "type": status_type,
            "message": content,
            "metadata": {"source": "canvas_integration"},
        })
        
        return ActionResult.ok("status", f"Status: {status_type}")
    
    def respond_to_prompt(self, response) -> ActionResult:
        """Respond to a pending input request."""
        # Handle dict input format
        if isinstance(response, dict):
            if "input_1" in response:
                response = response["input_1"]
            if isinstance(response, dict) and "content" in response:
                response = response["content"]
        response = str(response) if response else ""
        
        self._do_emit("chat:respond", {"response": response})
        preview = response[:50] if len(response) > 50 else response
        return ActionResult.ok("respond_to_prompt", f"Responded: {preview}...")
    
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
    
    # =========================================================================
    # Command Execution (Dynamic Dispatch)
    # =========================================================================
    
    def execute_command(self, command) -> ActionResult:
        """
        Execute a parsed canvas command by dispatching to the appropriate method.
        
        Args:
            command: Dict with 'type', 'params', and optionally 'confidence'.
                     Or dict with 'input_1' containing the command dict.
        
        Returns:
            ActionResult from the executed command
        """
        # Handle nested input format from paradigm
        if isinstance(command, dict) and "input_1" in command:
            command = command["input_1"]
        
        if not isinstance(command, dict):
            return ActionResult.error("execute_command", f"Invalid command format: {type(command)}")
        
        cmd_type = command.get("type", "chat")
        params = command.get("params", {})
        
        # Map command types to methods
        command_map = {
            # Navigation
            "zoom_in": lambda: self.zoom_in(params.get("amount", 0.1)),
            "zoom_out": lambda: self.zoom_out(params.get("amount", 0.1)),
            "zoom_to": lambda: self.zoom_to(params.get("level", 1.0)),
            "pan": lambda: self.pan(params.get("dx", 0), params.get("dy", 0)),
            "fit_view": lambda: self.fit_view(),
            "center_on_node": lambda: self.center_on_node(params.get("node_id", "")),
            
            # Node interaction
            "click_node": lambda: self.click_node(params.get("node_id", "")),
            "select": lambda: self.click_node(params.get("node_id", "")),  # alias
            "select_nodes": lambda: self.select_nodes(params.get("node_ids", [])),
            "deselect_all": lambda: self.deselect_all(),
            "double_click_node": lambda: self.double_click_node(params.get("node_id", "")),
            "hover_node": lambda: self.hover_node(params.get("node_id", "")),
            
            # Collapse/expand
            "collapse_node": lambda: self.collapse_node(params.get("node_id", "")),
            "collapse": lambda: self.collapse_node(params.get("node_id", "")),  # alias
            "expand_node": lambda: self.expand_node(params.get("node_id", "")),
            "expand": lambda: self.expand_node(params.get("node_id", "")),  # alias
            "toggle_collapse": lambda: self.toggle_collapse(params.get("node_id", "")),
            "collapse_all": lambda: self.collapse_all(),
            "expand_all": lambda: self.expand_all(),
            "collapse_to_level": lambda: self.collapse_to_level(params.get("level", 1)),
            
            # Highlight
            "highlight_branch": lambda: self.highlight_branch(params.get("node_id", "")),
            "highlight": lambda: self.highlight_branch(params.get("node_id", "")),  # alias
            "clear_highlight": lambda: self.clear_highlight(),
            
            # Panels
            "open_panel": lambda: self.open_panel(params.get("panel", "")),
            "close_panel": lambda: self.close_panel(params.get("panel", "")),
            "toggle_panel": lambda: self.toggle_panel(params.get("panel", "")),
            "focus_panel": lambda: self.focus_panel(params.get("panel", "")),
            
            # Breakpoints
            "add_breakpoint": lambda: self.add_breakpoint(params.get("node_id", "")),
            "remove_breakpoint": lambda: self.remove_breakpoint(params.get("node_id", "")),
            "toggle_breakpoint": lambda: self.toggle_breakpoint(params.get("node_id", "")),
            "breakpoint": lambda: self.toggle_breakpoint(params.get("node_id", "")),  # alias
            "clear_all_breakpoints": lambda: self.clear_all_breakpoints(),
            
            # Execution control (via Mind, but accessible here for convenience)
            "run": lambda: self._execution_control("run"),
            "start": lambda: self._execution_control("run"),  # alias
            "step": lambda: self._execution_control("step"),
            "pause": lambda: self._execution_control("pause"),
            "stop": lambda: self._execution_control("stop"),
            "restart": lambda: self._execution_control("restart"),
            
            # Chat (no canvas action, just acknowledge)
            "chat": lambda: ActionResult.ok("chat", "Conversational message - no canvas action taken"),
            "greet": lambda: ActionResult.ok("greet", "Greeting received - no canvas action taken"),
            "help": lambda: ActionResult.ok("help", "Help requested - no canvas action taken"),
        }
        
        if cmd_type in command_map:
            try:
                return command_map[cmd_type]()
            except Exception as e:
                return ActionResult.error("execute_command", f"Error executing {cmd_type}: {e}")
        else:
            # Unknown command type - treat as chat
            logger.warning(f"Unknown command type: {cmd_type}, treating as chat")
            return ActionResult.ok("chat", f"Unknown command '{cmd_type}' - no canvas action taken")
    
    def _execution_control(self, action: str) -> ActionResult:
        """Helper for execution control commands."""
        controller = self._execution_getter() if self._execution_getter else None
        if not controller:
            return ActionResult.error(action, "No execution controller available")
        
        self._do_emit(f"execution:{action}", {})
        return ActionResult.ok(action, f"Execution {action} requested")

