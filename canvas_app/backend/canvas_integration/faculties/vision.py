"""
Vision faculty for First Person perspective.

"My eyes" - what I can see (read-only UI state queries).
"""

import logging
from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING

from ..types import (
    UserViewSnapshot,
    CanvasSnapshot,
    ChatSnapshot,
    PanelsSnapshot,
    ExecutionSnapshot,
    ProjectSnapshot,
    LogsSnapshot,
    NodeDetails,
    VisibleNode,
    VisibleEdge,
    Position,
    Viewport,
    NodeType,
    NodeStatus,
    PanelType,
    PanelState,
    ChatMessage,
    PendingInput,
    LogEntry,
    ProjectTab,
)

if TYPE_CHECKING:
    from services.execution.controller import ExecutionController
    from ..facades.system import ServiceContainer

logger = logging.getLogger(__name__)


class Vision:
    """
    What I can see - all VIEW operations.
    
    Vision is READ-ONLY. It observes but does not change state.
    """
    
    def __init__(
        self,
        emit: Callable[[str, Dict], None],
        execution_getter: Optional[Callable[[], Optional["ExecutionController"]]],
        services: "ServiceContainer"
    ):
        self._emit = emit
        self._execution_getter = execution_getter
        self._services = services
    
    def _controller(self) -> Optional["ExecutionController"]:
        """Get current execution controller."""
        return self._execution_getter() if self._execution_getter else None
    
    # =========================================================================
    # Full View
    # =========================================================================
    
    def get_full_snapshot(self) -> UserViewSnapshot:
        """
        See everything at once.
        
        Returns complete snapshot of all visible UI state,
        convertible to text via .to_text() for AI consumption.
        """
        return UserViewSnapshot(
            canvas=self.get_canvas(),
            chat=self.get_chat(),
            panels=self.get_panels(),
            execution=self.get_execution(),
            project=self.get_project(),
            logs=self.get_logs(),
        )
    
    # =========================================================================
    # Canvas View
    # =========================================================================
    
    def get_canvas(self) -> CanvasSnapshot:
        """
        Look at the canvas/graph area.
        """
        controller = self._controller()
        graph_service = self._services.graph if self._services else None
        
        visible_nodes: List[VisibleNode] = []
        visible_edges: List[VisibleEdge] = []
        
        # Get nodes from graph service
        if graph_service and hasattr(graph_service, 'get_nodes'):
            for node_data in graph_service.get_nodes():
                visible_nodes.append(VisibleNode(
                    id=node_data.get('id', ''),
                    flow_index=node_data.get('flow_index'),
                    label=node_data.get('label', node_data.get('name', '')),
                    node_type=NodeType.INFERENCE if 'inference' in str(node_data.get('type', '')).lower() else NodeType.CONCEPT,
                    status=NodeStatus.PENDING,
                    position=Position(
                        x=node_data.get('x', 0),
                        y=node_data.get('y', 0)
                    ),
                    is_selected=node_data.get('selected', False),
                    is_collapsed=node_data.get('collapsed', False),
                    has_breakpoint=node_data.get('hasBreakpoint', False),
                    concept_name=node_data.get('concept_name'),
                ))
        
        # Get edges
        if graph_service and hasattr(graph_service, 'get_edges'):
            for edge_data in graph_service.get_edges():
                visible_edges.append(VisibleEdge(
                    id=edge_data.get('id', ''),
                    source_id=edge_data.get('source', ''),
                    target_id=edge_data.get('target', ''),
                    edge_type=edge_data.get('type', 'default'),
                ))
        
        # Get execution state
        is_executing = False
        current_node = None
        if controller:
            is_executing = getattr(controller, 'is_running', False)
            current_node = getattr(controller, 'current_flow_index', None)
        
        return CanvasSnapshot(
            visible_nodes=visible_nodes,
            visible_edges=visible_edges,
            selected_node_ids=[n.id for n in visible_nodes if n.is_selected],
            highlighted_node_ids=[],
            collapsed_node_ids=set(n.id for n in visible_nodes if n.is_collapsed),
            viewport=Viewport(0, 0, 1.0),
            layout_mode="hierarchical",
            total_nodes=len(visible_nodes),
            total_edges=len(visible_edges),
            is_executing=is_executing,
            current_executing_node=current_node,
        )
    
    def get_node_details(self, node_id: str) -> Optional[NodeDetails]:
        """
        Focus on a specific node.
        """
        graph_service = self._services.graph if self._services else None
        if not graph_service:
            return None
        
        node_data = None
        if hasattr(graph_service, 'get_node'):
            node_data = graph_service.get_node(node_id)
        
        if not node_data:
            return None
        
        # Get parent/child info
        parents = []
        children = []
        if hasattr(graph_service, 'get_parents'):
            parents = graph_service.get_parents(node_id)
        if hasattr(graph_service, 'get_children'):
            children = graph_service.get_children(node_id)
        
        return NodeDetails(
            id=node_data.get('id', ''),
            flow_index=node_data.get('flow_index'),
            label=node_data.get('label', ''),
            node_type=NodeType.CONCEPT,
            status=NodeStatus.PENDING,
            position=Position(node_data.get('x', 0), node_data.get('y', 0)),
            parent_ids=parents,
            child_ids=children,
            has_children=len(children) > 0,
            children_count=len(children),
            concept_name=node_data.get('concept_name'),
        )
    
    def get_visible_nodes(self) -> List[VisibleNode]:
        """Get list of nodes currently visible in viewport."""
        return self.get_canvas().visible_nodes
    
    def get_selected_nodes(self) -> List[VisibleNode]:
        """Get list of currently selected nodes."""
        canvas = self.get_canvas()
        return [n for n in canvas.visible_nodes if n.is_selected]
    
    # =========================================================================
    # Chat View
    # =========================================================================
    
    def get_chat(self) -> ChatSnapshot:
        """
        Look at the chat panel.
        """
        # Chat state would typically come from chat service
        # For now, return empty snapshot
        return ChatSnapshot(
            is_visible=True,
            messages=[],
            pending_input=None,
            input_field_value="",
            is_input_focused=False,
        )
    
    # =========================================================================
    # Panels View
    # =========================================================================
    
    def get_panels(self) -> PanelsSnapshot:
        """
        See which panels are open/focused.
        """
        # This would come from frontend state
        # Return reasonable defaults
        panels = [
            PanelState(PanelType.CANVAS, is_open=True, is_focused=True),
            PanelState(PanelType.CHAT, is_open=True, is_focused=False),
            PanelState(PanelType.AGENT, is_open=False, is_focused=False),
            PanelState(PanelType.EDITOR, is_open=False, is_focused=False),
            PanelState(PanelType.LOG, is_open=False, is_focused=False),
        ]
        return PanelsSnapshot(panels=panels, active_panel=PanelType.CANVAS)
    
    # =========================================================================
    # Execution View
    # =========================================================================
    
    def get_execution(self) -> ExecutionSnapshot:
        """
        See current execution state.
        """
        controller = self._controller()
        if not controller:
            return ExecutionSnapshot()
        
        # Extract state from controller
        status = "idle"
        if hasattr(controller, 'status'):
            status = controller.status
        elif hasattr(controller, 'is_running'):
            status = "running" if controller.is_running else "idle"
        
        current = None
        if hasattr(controller, 'current_flow_index'):
            current = controller.current_flow_index
        
        completed = 0
        total = 0
        cycle = 0
        if hasattr(controller, '_orchestrator') and controller._orchestrator:
            orch = controller._orchestrator
            completed = getattr(orch, 'inference_count', 0)
            cycle = getattr(orch, 'cycle_count', 0)
        
        return ExecutionSnapshot(
            status=status,
            current_inference=current,
            completed_count=completed,
            total_count=total,
            cycle_count=cycle,
            run_mode="slow",
        )
    
    def get_logs(self) -> LogsSnapshot:
        """
        See execution logs.
        """
        controller = self._controller()
        if not controller:
            return LogsSnapshot()
        
        entries: List[LogEntry] = []
        if hasattr(controller, 'get_logs'):
            for log in controller.get_logs(20):
                entries.append(LogEntry(
                    flow_index=log.get('flow_index', ''),
                    level=log.get('level', 'info'),
                    message=log.get('message', ''),
                    timestamp=log.get('timestamp', 0),
                ))
        
        return LogsSnapshot(entries=entries)
    
    # =========================================================================
    # Project View
    # =========================================================================
    
    def get_project(self) -> ProjectSnapshot:
        """
        See current project context.
        """
        project_service = self._services.project if self._services else None
        if not project_service:
            return ProjectSnapshot()
        
        name = None
        path = None
        is_loaded = False
        
        if hasattr(project_service, 'current_project'):
            proj = project_service.current_project
            if proj:
                name = getattr(proj, 'name', None)
                path = getattr(proj, 'path', None)
                is_loaded = True
        
        return ProjectSnapshot(
            name=name,
            path=path,
            is_loaded=is_loaded,
        )

