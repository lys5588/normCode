# First Person Perspective Interface

This document defines the **FirstPersonPerspective** interface - the sole entry point
for AI to interact with the canvas app from the user's perspective.

---

## Philosophy

> "I am the user. I see what they see. I do what they can do."

The AI operates as a **first-person participant** in the canvas app:
- **ONE interface** = ONE identity (the "I")
- **Internal faculties** = organized capabilities (vision, hands, mind)

This is like a person who has eyes, hands, and a mind - but is still ONE person.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    FIRST PERSON PERSPECTIVE                                 │
│                                                                             │
│    ┌─────────────┐                           ┌─────────────────────┐       │
│    │     AI      │                           │      FRONTEND       │       │
│    │  (in plan)  │                           │    (User's View)    │       │
│    └──────┬──────┘                           └──────────┬──────────┘       │
│           │                                             │                   │
│           │  ┌─────────────────────────────────────┐    │                   │
│           │  │     IFirstPersonPerspective         │    │                   │
│           │  │                                     │    │                   │
│           │  │  ┌─────────┐ ┌─────────┐ ┌───────┐ │    │                   │
│           ├──┤  │ VISION  │ │  HANDS  │ │ MIND  │ ├────┤                   │
│           │  │  │ (see)   │ │ (act)   │ │(think)│ │    │                   │
│           │  │  └─────────┘ └─────────┘ └───────┘ │    │                   │
│           │  │                                     │    │                   │
│           │  └─────────────────────────────────────┘    │                   │
│           │                                             │                   │
│           │         AI sees & acts AS the user          │                   │
│           │                                             │                   │
└───────────┴─────────────────────────────────────────────┴───────────────────┘
```

---

## The Three Faculties

| Faculty | Purpose | Examples |
|---------|---------|----------|
| **Vision** | What I can **see** | Snapshots, node details, panel states |
| **Hands** | What I can **manipulate** | Click, drag, type, collapse, toggle |
| **Mind** | What I can **understand/control** | Run, pause, configure, query relationships |

---

## Core Interface

```python
from typing import Protocol, List, Optional, Any
from abc import abstractmethod


class IFirstPersonPerspective(Protocol):
    """
    The SOLE entry point for all first-person interaction.
    
    I am the user. This interface is my eyes, hands, and mind.
    
    Usage:
        me: IFirstPersonPerspective
        
        # Look at everything
        snapshot = me.look()
        
        # Use faculties
        canvas = me.vision.get_canvas()
        me.hands.click_node("1.3")
        me.mind.run()
        
        # Shortcuts
        me.click("1.3")
        me.say("What is this?")
    """
    
    # ═══════════════════════════════════════════════════════════════════
    # FACULTIES
    # ═══════════════════════════════════════════════════════════════════
    
    @property
    def vision(self) -> 'IVision':
        """My eyes - what I can see."""
        ...
    
    @property
    def hands(self) -> 'IHands':
        """My hands - what I can manipulate."""
        ...
    
    @property
    def mind(self) -> 'IMind':
        """My mind - understanding and control."""
        ...
    
    # ═══════════════════════════════════════════════════════════════════
    # SHORTCUTS (convenience methods for common actions)
    # ═══════════════════════════════════════════════════════════════════
    
    def look(self) -> 'UserViewSnapshot':
        """Look at everything. Shortcut for vision.get_full_snapshot()."""
        ...
    
    def click(self, target: str) -> 'ActionResult':
        """Click a node. Shortcut for hands.click_node()."""
        ...
    
    def say(self, message: str) -> 'ActionResult':
        """Send a chat message. Shortcut for hands.send_chat_message()."""
        ...
```

---

## Faculty: Vision

Everything the AI can **see** - reading the UI state.

```python
class IVision(Protocol):
    """
    What I can see - all VIEW operations.
    
    Vision is READ-ONLY. It observes but does not change state.
    """
    
    # ═══════════════════════════════════════════════════════════════════
    # FULL VIEW
    # ═══════════════════════════════════════════════════════════════════
    
    def get_full_snapshot(self) -> 'UserViewSnapshot':
        """
        See everything at once.
        
        Returns complete snapshot of all visible UI state,
        convertible to text via .to_text() for AI consumption.
        """
        ...
    
    # ═══════════════════════════════════════════════════════════════════
    # CANVAS VIEW
    # ═══════════════════════════════════════════════════════════════════
    
    def get_canvas(self) -> 'CanvasSnapshot':
        """
        Look at the canvas/graph area.
        
        Returns:
            CanvasSnapshot with:
            - visible_nodes: Nodes in viewport
            - visible_edges: Edges in viewport
            - selected_node_ids: Currently selected
            - highlighted_node_ids: Currently highlighted
            - collapsed_node_ids: Which nodes are collapsed
            - viewport: {x, y, zoom}
            - layout_mode: "hierarchical" or "flow_aligned"
            - is_executing: Whether execution is running
            - current_executing_node: Which node is currently executing
        """
        ...
    
    def get_node_details(self, node_id: str) -> 'NodeDetails':
        """
        Focus on a specific node.
        
        Returns detailed info about one node including:
        - Basic info (id, label, type, status)
        - Position and visibility
        - Collapse state and children count
        - Breakpoint state
        - Value (if computed)
        - Connections (parents, children)
        """
        ...
    
    def get_visible_nodes(self) -> List['VisibleNode']:
        """Get list of nodes currently visible in viewport."""
        ...
    
    def get_selected_nodes(self) -> List['VisibleNode']:
        """Get list of currently selected nodes."""
        ...
    
    # ═══════════════════════════════════════════════════════════════════
    # CHAT VIEW
    # ═══════════════════════════════════════════════════════════════════
    
    def get_chat(self) -> 'ChatSnapshot':
        """
        Look at the chat panel.
        
        Returns:
            ChatSnapshot with:
            - is_visible: Is chat panel open
            - messages: Recent messages
            - pending_input: Any pending input request
            - input_field_value: Current text in input
        """
        ...
    
    # ═══════════════════════════════════════════════════════════════════
    # PANELS VIEW
    # ═══════════════════════════════════════════════════════════════════
    
    def get_panels(self) -> 'PanelsSnapshot':
        """
        See which panels are open/focused.
        
        Returns state of: canvas, chat, agent, editor, inspector, log, etc.
        """
        ...
    
    # ═══════════════════════════════════════════════════════════════════
    # EXECUTION VIEW
    # ═══════════════════════════════════════════════════════════════════
    
    def get_execution(self) -> 'ExecutionSnapshot':
        """
        See current execution state.
        
        Returns:
            ExecutionSnapshot with:
            - status: "idle", "running", "paused", "completed", "failed"
            - current_inference: Which node is executing
            - completed_count, total_count, cycle_count
            - node_statuses: Status of each node
            - breakpoints: Set of nodes with breakpoints
            - run_mode: "slow" or "fast"
        """
        ...
    
    def get_logs(self) -> 'LogsSnapshot':
        """
        See execution logs.
        
        Returns recent log entries with flow_index, level, message, timestamp.
        """
        ...
    
    # ═══════════════════════════════════════════════════════════════════
    # PROJECT VIEW
    # ═══════════════════════════════════════════════════════════════════
    
    def get_project(self) -> 'ProjectSnapshot':
        """
        See current project context.
        
        Returns:
            ProjectSnapshot with:
            - name, path, is_loaded
            - open_tabs: List of open project tabs
            - active_tab_id: Currently active tab
        """
        ...
```

---

## Faculty: Hands

Everything the AI can **manipulate** - taking actions in the UI.

```python
class IHands(Protocol):
    """
    What I can manipulate - all ACTION operations.
    
    Hands CHANGE state. Every method returns ActionResult.
    """
    
    # ═══════════════════════════════════════════════════════════════════
    # NODE INTERACTION
    # ═══════════════════════════════════════════════════════════════════
    
    def click_node(self, node_id: str) -> 'ActionResult':
        """Click/select a node."""
        ...
    
    def double_click_node(self, node_id: str) -> 'ActionResult':
        """Double-click a node (open details)."""
        ...
    
    def right_click_node(self, node_id: str) -> 'ActionResult':
        """Right-click a node (context menu)."""
        ...
    
    def hover_node(self, node_id: str) -> 'ActionResult':
        """Hover over a node (show tooltip)."""
        ...
    
    def drag_node(self, node_id: str, to_x: float, to_y: float) -> 'ActionResult':
        """Drag a node to a new position."""
        ...
    
    def select_nodes(self, node_ids: List[str]) -> 'ActionResult':
        """Select multiple nodes."""
        ...
    
    def deselect_all(self) -> 'ActionResult':
        """Clear all selections."""
        ...
    
    # ═══════════════════════════════════════════════════════════════════
    # GRAPH STRUCTURE
    # ═══════════════════════════════════════════════════════════════════
    
    def collapse_node(self, node_id: str) -> 'ActionResult':
        """Collapse a node (hide its descendants)."""
        ...
    
    def expand_node(self, node_id: str) -> 'ActionResult':
        """Expand a collapsed node."""
        ...
    
    def toggle_collapse(self, node_id: str) -> 'ActionResult':
        """Toggle collapse state of a node."""
        ...
    
    def collapse_all(self) -> 'ActionResult':
        """Collapse all nodes that have children."""
        ...
    
    def expand_all(self) -> 'ActionResult':
        """Expand all collapsed nodes."""
        ...
    
    def collapse_to_level(self, level: int) -> 'ActionResult':
        """Collapse all nodes at or below a level."""
        ...
    
    def highlight_branch(self, node_id: str) -> 'ActionResult':
        """Highlight the branch (ancestors + descendants) of a node."""
        ...
    
    def clear_highlight(self) -> 'ActionResult':
        """Clear branch highlighting."""
        ...
    
    # ═══════════════════════════════════════════════════════════════════
    # VIEW NAVIGATION
    # ═══════════════════════════════════════════════════════════════════
    
    def zoom_in(self, amount: float = 0.1) -> 'ActionResult':
        """Zoom in the canvas."""
        ...
    
    def zoom_out(self, amount: float = 0.1) -> 'ActionResult':
        """Zoom out the canvas."""
        ...
    
    def zoom_to(self, level: float) -> 'ActionResult':
        """Zoom to specific level (1.0 = 100%)."""
        ...
    
    def pan(self, dx: float, dy: float) -> 'ActionResult':
        """Pan the canvas view."""
        ...
    
    def fit_view(self) -> 'ActionResult':
        """Fit all nodes in the viewport."""
        ...
    
    def center_on_node(self, node_id: str) -> 'ActionResult':
        """Center the view on a specific node."""
        ...
    
    # ═══════════════════════════════════════════════════════════════════
    # PANEL MANIPULATION
    # ═══════════════════════════════════════════════════════════════════
    
    def open_panel(self, panel: str) -> 'ActionResult':
        """
        Open a panel.
        
        Args:
            panel: "chat", "agent", "editor", "inspector", "log", "settings"
        """
        ...
    
    def close_panel(self, panel: str) -> 'ActionResult':
        """Close a panel."""
        ...
    
    def toggle_panel(self, panel: str) -> 'ActionResult':
        """Toggle a panel open/closed."""
        ...
    
    def focus_panel(self, panel: str) -> 'ActionResult':
        """Focus a panel (make it active)."""
        ...
    
    # ═══════════════════════════════════════════════════════════════════
    # CHAT INTERACTION
    # ═══════════════════════════════════════════════════════════════════
    
    def type_in_chat(self, text: str) -> 'ActionResult':
        """Type text in the chat input field."""
        ...
    
    def clear_chat_input(self) -> 'ActionResult':
        """Clear the chat input field."""
        ...
    
    def send_chat_message(self) -> 'ActionResult':
        """Send the current chat input (press Enter)."""
        ...
    
    def say(self, message: str) -> 'ActionResult':
        """Type and send a message in one action."""
        ...
    
    def respond_to_prompt(self, response: str) -> 'ActionResult':
        """Respond to a pending input request."""
        ...
    
    def select_prompt_option(self, option: str) -> 'ActionResult':
        """Select an option from a pending select prompt."""
        ...
    
    def scroll_chat(self, direction: str, amount: int = 1) -> 'ActionResult':
        """Scroll chat panel ("up" or "down")."""
        ...
    
    # ═══════════════════════════════════════════════════════════════════
    # BUTTON & KEYBOARD
    # ═══════════════════════════════════════════════════════════════════
    
    def click_button(self, button_id: str) -> 'ActionResult':
        """
        Click a UI button.
        
        Args:
            button_id: "run", "pause", "step", "stop", "restart",
                       "save", "load", "settings", etc.
        """
        ...
    
    def press_key(self, key: str, modifiers: List[str] = None) -> 'ActionResult':
        """
        Press a keyboard key.
        
        Args:
            key: "Enter", "Escape", "Delete", "a", "F5", etc.
            modifiers: ["Ctrl"], ["Ctrl", "Shift"], etc.
        """
        ...
    
    def keyboard_shortcut(self, shortcut: str) -> 'ActionResult':
        """
        Execute a keyboard shortcut.
        
        Args:
            shortcut: "Ctrl+S", "Ctrl+Shift+R", etc.
        """
        ...
    
    # ═══════════════════════════════════════════════════════════════════
    # BREAKPOINTS
    # ═══════════════════════════════════════════════════════════════════
    
    def toggle_breakpoint(self, node_id: str) -> 'ActionResult':
        """Toggle breakpoint on a node."""
        ...
    
    def add_breakpoint(self, node_id: str) -> 'ActionResult':
        """Add breakpoint to a node."""
        ...
    
    def remove_breakpoint(self, node_id: str) -> 'ActionResult':
        """Remove breakpoint from a node."""
        ...
    
    def clear_all_breakpoints(self) -> 'ActionResult':
        """Clear all breakpoints."""
        ...
```

---

## Faculty: Mind

What the AI can **understand and control** - deeper operations beyond physical manipulation.

```python
class IMind(Protocol):
    """
    Understanding and control - operations that require "thinking".
    
    Mind handles:
    - Execution control (decisions about what should happen)
    - Configuration (preferences and settings)
    - Project management (context switching)
    - Deeper queries (relationships, values)
    """
    
    # ═══════════════════════════════════════════════════════════════════
    # EXECUTION CONTROL
    # ═══════════════════════════════════════════════════════════════════
    
    def run(self) -> 'ActionResult':
        """Start or continue execution."""
        ...
    
    def pause(self) -> 'ActionResult':
        """Pause execution."""
        ...
    
    def step(self) -> 'ActionResult':
        """Execute one inference."""
        ...
    
    def step_over(self) -> 'ActionResult':
        """Step over current node (execute without entering)."""
        ...
    
    def step_to_breakpoint(self) -> 'ActionResult':
        """Run until next breakpoint."""
        ...
    
    def stop(self) -> 'ActionResult':
        """Stop execution completely."""
        ...
    
    def restart(self) -> 'ActionResult':
        """Restart execution from beginning."""
        ...
    
    # ═══════════════════════════════════════════════════════════════════
    # CONFIGURATION
    # ═══════════════════════════════════════════════════════════════════
    
    def set_run_mode(self, mode: str) -> 'ActionResult':
        """
        Set run mode.
        
        Args:
            mode: "slow" (one at a time) or "fast" (all ready per cycle)
        """
        ...
    
    def set_layout_mode(self, mode: str) -> 'ActionResult':
        """
        Set graph layout mode.
        
        Args:
            mode: "hierarchical" or "flow_aligned"
        """
        ...
    
    def toggle_layout_mode(self) -> 'ActionResult':
        """Toggle between hierarchical and flow_aligned."""
        ...
    
    def set_verbose_logging(self, enabled: bool) -> 'ActionResult':
        """Enable/disable verbose logging."""
        ...
    
    # ═══════════════════════════════════════════════════════════════════
    # PROJECT MANAGEMENT
    # ═══════════════════════════════════════════════════════════════════
    
    def switch_tab(self, tab_id: str) -> 'ActionResult':
        """Switch to a different project tab."""
        ...
    
    def close_tab(self, tab_id: str) -> 'ActionResult':
        """Close a project tab."""
        ...
    
    def open_project(self, path: str) -> 'ActionResult':
        """Open a project as a new tab."""
        ...
    
    def load_repositories(self) -> 'ActionResult':
        """Load/reload repositories for current project."""
        ...
    
    def save_project(self) -> 'ActionResult':
        """Save the current project."""
        ...
    
    # ═══════════════════════════════════════════════════════════════════
    # DEEPER QUERIES
    # ═══════════════════════════════════════════════════════════════════
    
    def get_node_ancestors(self, node_id: str) -> List[str]:
        """Get all ancestor node IDs (parents, grandparents, etc.)."""
        ...
    
    def get_node_descendants(self, node_id: str) -> List[str]:
        """Get all descendant node IDs (children, grandchildren, etc.)."""
        ...
    
    def get_node_branch(self, node_id: str) -> List[str]:
        """Get entire branch (ancestors + descendants)."""
        ...
    
    def get_concept_value(self, concept_name: str) -> Any:
        """Get the computed value of a concept from blackboard."""
        ...
    
    def get_same_concept_nodes(self, node_id: str) -> List[str]:
        """Get all nodes with the same concept name."""
        ...
    
    # ═══════════════════════════════════════════════════════════════════
    # VALUE OVERRIDE
    # ═══════════════════════════════════════════════════════════════════
    
    def override_value(self, concept_name: str, value: Any) -> 'ActionResult':
        """Override a concept's value in blackboard."""
        ...
    
    def clear_override(self, concept_name: str) -> 'ActionResult':
        """Clear a value override."""
        ...
```

---

## Data Types

### Action Result

```python
from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class ActionResult:
    """Result of any action."""
    success: bool
    action: str
    message: Optional[str] = None
    error: Optional[str] = None
    new_state: Optional[Dict[str, Any]] = None
```

### Snapshots

```python
from dataclasses import dataclass
from typing import List, Optional, Set
from enum import Enum


class NodeType(Enum):
    CONCEPT = "concept"
    INFERENCE = "inference"
    VALUE = "value"
    FUNCTION = "function"
    CONTEXT = "context"


class NodeStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class PanelType(Enum):
    CANVAS = "canvas"
    CHAT = "chat"
    AGENT = "agent"
    EDITOR = "editor"
    INSPECTOR = "inspector"
    LOG = "log"
    SETTINGS = "settings"


@dataclass
class Position:
    x: float
    y: float


@dataclass
class Viewport:
    x: float
    y: float
    zoom: float
    width: float
    height: float


@dataclass
class VisibleNode:
    """A node visible in the canvas."""
    id: str
    flow_index: Optional[str]
    label: str
    node_type: NodeType
    status: NodeStatus
    position: Position
    is_selected: bool
    is_highlighted: bool
    is_collapsed: bool
    has_children: bool
    has_breakpoint: bool
    concept_name: Optional[str] = None
    has_value: bool = False


@dataclass
class VisibleEdge:
    """An edge visible in the canvas."""
    id: str
    source_id: str
    target_id: str
    edge_type: str
    is_highlighted: bool = False


@dataclass
class CanvasSnapshot:
    """Snapshot of the canvas state."""
    visible_nodes: List[VisibleNode]
    visible_edges: List[VisibleEdge]
    selected_node_ids: List[str]
    highlighted_node_ids: List[str]
    collapsed_node_ids: Set[str]
    viewport: Viewport
    layout_mode: str
    total_nodes: int
    total_edges: int
    is_executing: bool
    current_executing_node: Optional[str]
    
    def to_text(self) -> str:
        """Convert to AI-readable text."""
        lines = ["=== CANVAS ==="]
        lines.append(f"Layout: {self.layout_mode}, Zoom: {self.viewport.zoom:.0%}")
        lines.append(f"Showing {len(self.visible_nodes)}/{self.total_nodes} nodes")
        
        if self.is_executing:
            lines.append(f"⚡ EXECUTING: {self.current_executing_node}")
        
        if self.selected_node_ids:
            lines.append(f"Selected: {', '.join(self.selected_node_ids)}")
        
        lines.append("\nNODES:")
        for node in self.visible_nodes:
            icon = {"pending": "○", "running": "◐", "completed": "●", "failed": "✗"}.get(node.status.value, "?")
            flags = []
            if node.is_selected: flags.append("SEL")
            if node.is_collapsed: flags.append("COL")
            if node.has_breakpoint: flags.append("BP")
            flag_str = f" [{','.join(flags)}]" if flags else ""
            lines.append(f"  {icon} {node.flow_index or node.id}: {node.label}{flag_str}")
        
        return "\n".join(lines)


@dataclass
class ChatMessage:
    """A message in chat."""
    id: str
    role: str  # "user", "assistant", "system", "compiler"
    content: str
    timestamp: float


@dataclass
class PendingInput:
    """A pending input request."""
    request_id: str
    prompt: str
    input_type: str  # "text", "code", "confirm", "select"
    options: Optional[List[str]] = None


@dataclass
class ChatSnapshot:
    """Snapshot of chat panel."""
    is_visible: bool
    messages: List[ChatMessage]
    pending_input: Optional[PendingInput]
    input_field_value: str
    is_input_focused: bool
    
    def to_text(self) -> str:
        if not self.is_visible:
            return "=== CHAT: HIDDEN ==="
        
        lines = ["=== CHAT ==="]
        
        if self.pending_input:
            lines.append(f"⚠️ AWAITING: {self.pending_input.prompt}")
            if self.pending_input.options:
                lines.append(f"   Options: {', '.join(self.pending_input.options)}")
        
        lines.append("\nMESSAGES:")
        for msg in self.messages[-10:]:
            prefix = {"user": "👤", "assistant": "🤖", "system": "📢"}.get(msg.role, "•")
            content = msg.content[:80] + "..." if len(msg.content) > 80 else msg.content
            lines.append(f"  {prefix} {content}")
        
        return "\n".join(lines)


@dataclass
class PanelState:
    """State of a panel."""
    panel_type: PanelType
    is_open: bool
    is_focused: bool


@dataclass
class PanelsSnapshot:
    """Snapshot of all panels."""
    panels: List[PanelState]
    active_panel: Optional[PanelType]
    
    def to_text(self) -> str:
        lines = ["=== PANELS ==="]
        for p in self.panels:
            status = "OPEN" if p.is_open else "closed"
            focus = " [FOCUS]" if p.is_focused else ""
            lines.append(f"  {p.panel_type.value}: {status}{focus}")
        return "\n".join(lines)


@dataclass
class ExecutionSnapshot:
    """Snapshot of execution state."""
    status: str  # "idle", "running", "paused", "completed", "failed"
    current_inference: Optional[str]
    completed_count: int
    total_count: int
    cycle_count: int
    node_statuses: Dict[str, str]
    breakpoints: Set[str]
    run_mode: str  # "slow" or "fast"
    
    def to_text(self) -> str:
        lines = ["=== EXECUTION ==="]
        lines.append(f"Status: {self.status.upper()}")
        lines.append(f"Progress: {self.completed_count}/{self.total_count} (cycle {self.cycle_count})")
        lines.append(f"Mode: {self.run_mode}")
        
        if self.current_inference:
            lines.append(f"Current: {self.current_inference}")
        
        if self.breakpoints:
            lines.append(f"Breakpoints: {', '.join(self.breakpoints)}")
        
        return "\n".join(lines)


@dataclass
class ProjectTab:
    """A project tab."""
    id: str
    name: str
    path: str
    is_loaded: bool
    is_active: bool


@dataclass
class ProjectSnapshot:
    """Snapshot of project context."""
    name: Optional[str]
    path: Optional[str]
    is_loaded: bool
    tabs: List[ProjectTab]
    active_tab_id: Optional[str]
    
    def to_text(self) -> str:
        lines = ["=== PROJECT ==="]
        if self.name:
            status = "✓ LOADED" if self.is_loaded else "○ not loaded"
            lines.append(f"{self.name} [{status}]")
        else:
            lines.append("No project open")
        
        if len(self.tabs) > 1:
            lines.append(f"\nTabs: {len(self.tabs)}")
            for tab in self.tabs:
                active = " [ACTIVE]" if tab.is_active else ""
                lines.append(f"  • {tab.name}{active}")
        
        return "\n".join(lines)


@dataclass
class LogEntry:
    """A log entry."""
    flow_index: str
    level: str
    message: str
    timestamp: float


@dataclass
class LogsSnapshot:
    """Snapshot of logs."""
    entries: List[LogEntry]
    
    def to_text(self) -> str:
        lines = ["=== LOGS ==="]
        for entry in self.entries[-20:]:
            icon = {"info": "ℹ", "warning": "⚠", "error": "✗"}.get(entry.level, "•")
            lines.append(f"  {icon} [{entry.flow_index}] {entry.message}")
        return "\n".join(lines)


@dataclass
class NodeDetails:
    """Detailed info about a node."""
    id: str
    flow_index: Optional[str]
    label: str
    node_type: NodeType
    status: NodeStatus
    position: Position
    
    is_visible: bool
    is_selected: bool
    is_highlighted: bool
    is_collapsed: bool
    is_hidden: bool  # Hidden by parent collapse
    
    has_breakpoint: bool
    has_children: bool
    children_count: int
    
    parent_ids: List[str]
    child_ids: List[str]
    
    concept_name: Optional[str]
    has_value: bool
    value_preview: Optional[str]


@dataclass
class UserViewSnapshot:
    """
    Complete snapshot of everything the user can see.
    
    This is the "accessibility tree" - full UI state for AI.
    """
    canvas: CanvasSnapshot
    chat: ChatSnapshot
    panels: PanelsSnapshot
    execution: ExecutionSnapshot
    project: ProjectSnapshot
    
    is_loading: bool
    is_modal_open: bool
    modal_content: Optional[str]
    status_message: Optional[str]
    
    def to_text(self) -> str:
        """Convert entire view to text for AI consumption."""
        lines = []
        lines.append("╔══════════════════════════════════════════════════════╗")
        lines.append("║         FIRST PERSON VIEW - CANVAS APP               ║")
        lines.append("╚══════════════════════════════════════════════════════╝")
        lines.append("")
        
        if self.is_modal_open:
            lines.append(f"⚠️ MODAL: {self.modal_content}")
            lines.append("")
        
        if self.status_message:
            lines.append(f"STATUS: {self.status_message}")
            lines.append("")
        
        lines.append(self.project.to_text())
        lines.append("")
        lines.append(self.execution.to_text())
        lines.append("")
        lines.append(self.panels.to_text())
        lines.append("")
        lines.append(self.canvas.to_text())
        lines.append("")
        lines.append(self.chat.to_text())
        
        return "\n".join(lines)
```

---

## Usage Examples

```python
# AI has ONE interface - "me"
me: IFirstPersonPerspective


# ═══════════════════════════════════════════════════════════════════
# Example 1: Observe and understand
# ═══════════════════════════════════════════════════════════════════

def observe_state(me: IFirstPersonPerspective):
    """AI looks at the app and understands what's happening."""
    
    # Look at everything
    snapshot = me.look()
    print(snapshot.to_text())
    
    # Or query specific aspects
    canvas = me.vision.get_canvas()
    execution = me.vision.get_execution()
    
    if execution.status == "paused" and canvas.current_executing_node:
        print(f"Paused at: {canvas.current_executing_node}")
    
    # Check for pending input
    chat = me.vision.get_chat()
    if chat.pending_input:
        print(f"User is being asked: {chat.pending_input.prompt}")


# ═══════════════════════════════════════════════════════════════════
# Example 2: Navigate and select
# ═══════════════════════════════════════════════════════════════════

def navigate_to_node(me: IFirstPersonPerspective, target: str):
    """AI navigates to and selects a specific node."""
    
    # Check if visible
    visible = me.vision.get_visible_nodes()
    visible_ids = [n.flow_index for n in visible]
    
    if target not in visible_ids:
        # Navigate to it
        me.hands.center_on_node(target)
    
    # Select it
    me.hands.click_node(target)
    
    # Get details
    details = me.vision.get_node_details(target)
    print(f"Selected: {details.label} ({details.status.value})")


# ═══════════════════════════════════════════════════════════════════
# Example 3: Debug with breakpoints
# ═══════════════════════════════════════════════════════════════════

def debug_execution(me: IFirstPersonPerspective, suspect_nodes: List[str]):
    """AI sets up debugging for specific nodes."""
    
    # Clear existing breakpoints
    me.hands.clear_all_breakpoints()
    
    # Set breakpoints on suspect nodes
    for node_id in suspect_nodes:
        me.hands.add_breakpoint(node_id)
    
    # Start execution
    me.mind.run()
    
    # Wait and check
    execution = me.vision.get_execution()
    if execution.status == "paused":
        current = execution.current_inference
        print(f"Hit breakpoint at: {current}")
        
        # Inspect the node
        details = me.vision.get_node_details(current)
        value = me.mind.get_concept_value(details.concept_name)
        print(f"Value: {value}")


# ═══════════════════════════════════════════════════════════════════
# Example 4: Manage graph complexity
# ═══════════════════════════════════════════════════════════════════

def focus_on_branch(me: IFirstPersonPerspective, node_id: str):
    """AI collapses everything except a specific branch."""
    
    # Collapse all first
    me.hands.collapse_all()
    
    # Get the branch
    branch = me.mind.get_node_branch(node_id)
    
    # Expand just those nodes
    for ancestor in me.mind.get_node_ancestors(node_id):
        me.hands.expand_node(ancestor)
    
    # Highlight the branch
    me.hands.highlight_branch(node_id)
    
    # Center on target
    me.hands.center_on_node(node_id)


# ═══════════════════════════════════════════════════════════════════
# Example 5: Chat interaction
# ═══════════════════════════════════════════════════════════════════

def ask_and_respond(me: IFirstPersonPerspective, question: str):
    """AI asks a question in chat and handles response."""
    
    # Make sure chat is open
    panels = me.vision.get_panels()
    chat_open = any(p.is_open for p in panels.panels if p.panel_type == PanelType.CHAT)
    
    if not chat_open:
        me.hands.open_panel("chat")
    
    # Ask the question
    me.say(question)
    
    # Check for input request
    chat = me.vision.get_chat()
    if chat.pending_input:
        if chat.pending_input.input_type == "confirm":
            me.hands.respond_to_prompt("yes")
        elif chat.pending_input.options:
            me.hands.select_prompt_option(chat.pending_input.options[0])


# ═══════════════════════════════════════════════════════════════════
# Example 6: Step through execution
# ═══════════════════════════════════════════════════════════════════

def step_and_observe(me: IFirstPersonPerspective, max_steps: int = 10):
    """AI steps through execution, observing each step."""
    
    for i in range(max_steps):
        # Get current state
        exec_state = me.vision.get_execution()
        
        print(f"Step {i+1}: {exec_state.completed_count}/{exec_state.total_count}")
        
        if exec_state.status == "completed":
            print("Execution complete!")
            break
        
        if exec_state.status == "failed":
            print(f"Failed at: {exec_state.current_inference}")
            break
        
        # Step one inference
        me.mind.step()
        
        # Brief pause to let execution happen
        import time
        time.sleep(0.5)
```

---

## Implementation Notes

The `FirstPersonPerspectiveInterface` is conceptually **frontend-facing**, but technically:

1. **Backend holds the implementation** - The interface is implemented in the backend
2. **Commands route through WebSocket** - Actions are sent as WebSocket events to frontend
3. **Frontend reports state** - Snapshots are built from frontend state (via WebSocket or polling)

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│     AI      │────▶│   Backend   │────▶│  Frontend   │
│  (caller)   │     │ (interface) │     │  (target)   │
└─────────────┘     └─────────────┘     └─────────────┘
                           │
                    Implements IFirstPersonPerspective
                           │
                    - vision.*: queries frontend state
                    - hands.*: sends commands to frontend
                    - mind.*: queries backend + sends commands
```

---

## Summary

| Aspect | Value |
|--------|-------|
| **Entry Point** | Single: `IFirstPersonPerspective` |
| **Faculties** | `vision` (see), `hands` (act), `mind` (think) |
| **Philosophy** | "I am the user" - first-person participation |
| **Vision Methods** | ~10 (snapshots, details, queries) |
| **Hands Methods** | ~35 (click, drag, collapse, type, etc.) |
| **Mind Methods** | ~20 (run, pause, configure, query) |
| **Key Feature** | `.to_text()` for AI-readable descriptions |

---
