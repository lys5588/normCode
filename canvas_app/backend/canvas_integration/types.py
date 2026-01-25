"""
Data types for Canvas Integration.

These types represent snapshots of UI state, action results,
and structured data for AI consumption.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Set
from enum import Enum
from datetime import datetime


# =============================================================================
# Enums
# =============================================================================

class NodeType(Enum):
    """Types of nodes in the graph."""
    CONCEPT = "concept"
    INFERENCE = "inference"
    VALUE = "value"
    FUNCTION = "function"
    CONTEXT = "context"


class NodeStatus(Enum):
    """Execution status of a node."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class PanelType(Enum):
    """Types of panels in the UI."""
    CANVAS = "canvas"
    CHAT = "chat"
    AGENT = "agent"
    EDITOR = "editor"
    INSPECTOR = "inspector"
    LOG = "log"
    SETTINGS = "settings"


class ExecutionStatus(Enum):
    """Overall execution status."""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


# =============================================================================
# Basic Types
# =============================================================================

@dataclass
class Position:
    """2D position."""
    x: float
    y: float


@dataclass
class Viewport:
    """Canvas viewport state."""
    x: float
    y: float
    zoom: float
    width: float = 800.0
    height: float = 600.0


@dataclass
class ActionResult:
    """Result of any action."""
    success: bool
    action: str
    message: Optional[str] = None
    error: Optional[str] = None
    new_state: Optional[Dict[str, Any]] = None
    
    @classmethod
    def ok(cls, action: str, message: str = None, **kwargs) -> "ActionResult":
        """Create a successful result."""
        return cls(success=True, action=action, message=message, new_state=kwargs or None)
    
    @classmethod
    def fail(cls, action: str, error: str) -> "ActionResult":
        """Create a failed result."""
        return cls(success=False, action=action, error=error)


# =============================================================================
# Node Types
# =============================================================================

@dataclass
class VisibleNode:
    """A node visible in the canvas."""
    id: str
    flow_index: Optional[str]
    label: str
    node_type: NodeType
    status: NodeStatus
    position: Position
    is_selected: bool = False
    is_highlighted: bool = False
    is_collapsed: bool = False
    has_children: bool = False
    has_breakpoint: bool = False
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
class NodeDetails:
    """Detailed info about a node."""
    id: str
    flow_index: Optional[str]
    label: str
    node_type: NodeType
    status: NodeStatus
    position: Position
    
    is_visible: bool = True
    is_selected: bool = False
    is_highlighted: bool = False
    is_collapsed: bool = False
    is_hidden: bool = False  # Hidden by parent collapse
    
    has_breakpoint: bool = False
    has_children: bool = False
    children_count: int = 0
    
    parent_ids: List[str] = field(default_factory=list)
    child_ids: List[str] = field(default_factory=list)
    
    concept_name: Optional[str] = None
    has_value: bool = False
    value_preview: Optional[str] = None


# =============================================================================
# Snapshot Types
# =============================================================================

@dataclass
class CanvasSnapshot:
    """Snapshot of the canvas state."""
    visible_nodes: List[VisibleNode] = field(default_factory=list)
    visible_edges: List[VisibleEdge] = field(default_factory=list)
    selected_node_ids: List[str] = field(default_factory=list)
    highlighted_node_ids: List[str] = field(default_factory=list)
    collapsed_node_ids: Set[str] = field(default_factory=set)
    viewport: Viewport = field(default_factory=lambda: Viewport(0, 0, 1.0))
    layout_mode: str = "hierarchical"
    total_nodes: int = 0
    total_edges: int = 0
    is_executing: bool = False
    current_executing_node: Optional[str] = None
    
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
            icon = {"pending": "○", "running": "◐", "completed": "●", "failed": "✗"}.get(
                node.status.value if isinstance(node.status, NodeStatus) else node.status, "?"
            )
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
    is_visible: bool = True
    messages: List[ChatMessage] = field(default_factory=list)
    pending_input: Optional[PendingInput] = None
    input_field_value: str = ""
    is_input_focused: bool = False
    
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
            prefix = {"user": "👤", "assistant": "🤖", "system": "📢", "compiler": "⚙️"}.get(msg.role, "•")
            content = msg.content[:80] + "..." if len(msg.content) > 80 else msg.content
            lines.append(f"  {prefix} {content}")
        
        return "\n".join(lines)


@dataclass
class PanelState:
    """State of a panel."""
    panel_type: PanelType
    is_open: bool
    is_focused: bool = False


@dataclass
class PanelsSnapshot:
    """Snapshot of all panels."""
    panels: List[PanelState] = field(default_factory=list)
    active_panel: Optional[PanelType] = None
    
    def to_text(self) -> str:
        lines = ["=== PANELS ==="]
        for p in self.panels:
            status = "OPEN" if p.is_open else "closed"
            focus = " [FOCUS]" if p.is_focused else ""
            panel_name = p.panel_type.value if isinstance(p.panel_type, PanelType) else p.panel_type
            lines.append(f"  {panel_name}: {status}{focus}")
        return "\n".join(lines)


@dataclass
class ExecutionSnapshot:
    """Snapshot of execution state."""
    status: str = "idle"  # "idle", "running", "paused", "completed", "failed"
    current_inference: Optional[str] = None
    completed_count: int = 0
    total_count: int = 0
    cycle_count: int = 0
    node_statuses: Dict[str, str] = field(default_factory=dict)
    breakpoints: Set[str] = field(default_factory=set)
    run_mode: str = "slow"  # "slow" or "fast"
    
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
    name: Optional[str] = None
    path: Optional[str] = None
    is_loaded: bool = False
    tabs: List[ProjectTab] = field(default_factory=list)
    active_tab_id: Optional[str] = None
    
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
    entries: List[LogEntry] = field(default_factory=list)
    
    def to_text(self) -> str:
        lines = ["=== LOGS ==="]
        for entry in self.entries[-20:]:
            icon = {"info": "ℹ", "warning": "⚠", "error": "✗"}.get(entry.level, "•")
            lines.append(f"  {icon} [{entry.flow_index}] {entry.message}")
        return "\n".join(lines)


@dataclass
class UserViewSnapshot:
    """
    Complete snapshot of everything the user can see.
    
    This is the "accessibility tree" - full UI state for AI.
    """
    canvas: CanvasSnapshot = field(default_factory=CanvasSnapshot)
    chat: ChatSnapshot = field(default_factory=ChatSnapshot)
    panels: PanelsSnapshot = field(default_factory=PanelsSnapshot)
    execution: ExecutionSnapshot = field(default_factory=ExecutionSnapshot)
    project: ProjectSnapshot = field(default_factory=ProjectSnapshot)
    logs: LogsSnapshot = field(default_factory=LogsSnapshot)
    
    is_loading: bool = False
    is_modal_open: bool = False
    modal_content: Optional[str] = None
    status_message: Optional[str] = None
    
    timestamp: datetime = field(default_factory=datetime.now)
    
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

