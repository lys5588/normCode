"""
Mind faculty for First Person perspective.

"My mind" - understanding and control (decisions, configuration, queries).
"""

import logging
from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING

from ..types import ActionResult

if TYPE_CHECKING:
    from services.execution.controller import ExecutionController
    from ..facades.system import ServiceContainer

logger = logging.getLogger(__name__)


class Mind:
    """
    Understanding and control - operations that require "thinking".
    
    Mind handles:
    - Execution control (decisions about what should happen)
    - Configuration (preferences and settings)
    - Project management (context switching)
    - Deeper queries (relationships, values)
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
    # Execution Control
    # =========================================================================
    
    def run(self) -> ActionResult:
        """Start or continue execution."""
        controller = self._controller()
        if controller and hasattr(controller, 'resume'):
            try:
                controller.resume()
                self._emit("execution:run", {})
                return ActionResult.ok("run", "Started execution")
            except Exception as e:
                return ActionResult.fail("run", str(e))
        
        self._emit("execution:run", {})
        return ActionResult.ok("run", "Requested run")
    
    def pause(self) -> ActionResult:
        """Pause execution."""
        controller = self._controller()
        if controller and hasattr(controller, 'pause'):
            try:
                controller.pause()
                self._emit("execution:pause", {})
                return ActionResult.ok("pause", "Paused execution")
            except Exception as e:
                return ActionResult.fail("pause", str(e))
        
        self._emit("execution:pause", {})
        return ActionResult.ok("pause", "Requested pause")
    
    def step(self) -> ActionResult:
        """Execute one inference."""
        controller = self._controller()
        if controller and hasattr(controller, 'step'):
            try:
                controller.step()
                self._emit("execution:step", {})
                return ActionResult.ok("step", "Stepped one inference")
            except Exception as e:
                return ActionResult.fail("step", str(e))
        
        self._emit("execution:step", {})
        return ActionResult.ok("step", "Requested step")
    
    def step_over(self) -> ActionResult:
        """Step over current node (execute without entering)."""
        self._emit("execution:step_over", {})
        return ActionResult.ok("step_over", "Stepped over")
    
    def step_to_breakpoint(self) -> ActionResult:
        """Run until next breakpoint."""
        self._emit("execution:step_to_breakpoint", {})
        return ActionResult.ok("step_to_breakpoint", "Running to breakpoint")
    
    def stop(self) -> ActionResult:
        """Stop execution completely."""
        controller = self._controller()
        if controller and hasattr(controller, 'stop'):
            try:
                controller.stop()
                self._emit("execution:stop", {})
                return ActionResult.ok("stop", "Stopped execution")
            except Exception as e:
                return ActionResult.fail("stop", str(e))
        
        self._emit("execution:stop", {})
        return ActionResult.ok("stop", "Requested stop")
    
    def restart(self) -> ActionResult:
        """Restart execution from beginning."""
        controller = self._controller()
        if controller and hasattr(controller, 'restart'):
            try:
                controller.restart()
                self._emit("execution:restart", {})
                return ActionResult.ok("restart", "Restarted execution")
            except Exception as e:
                return ActionResult.fail("restart", str(e))
        
        self._emit("execution:restart", {})
        return ActionResult.ok("restart", "Requested restart")
    
    def run_from(self, node_id: str) -> ActionResult:
        """Run starting from a specific node."""
        self._emit("execution:run_from", {"node_id": node_id})
        return ActionResult.ok("run_from", f"Running from {node_id}")
    
    # =========================================================================
    # Configuration
    # =========================================================================
    
    def set_run_mode(self, mode: str) -> ActionResult:
        """Set run mode ("slow" or "fast")."""
        self._emit("config:run_mode", {"mode": mode})
        return ActionResult.ok("set_run_mode", f"Set run mode to {mode}")
    
    def set_layout_mode(self, mode: str) -> ActionResult:
        """Set graph layout mode."""
        self._emit("config:layout_mode", {"mode": mode})
        return ActionResult.ok("set_layout_mode", f"Set layout mode to {mode}")
    
    def toggle_layout_mode(self) -> ActionResult:
        """Toggle between hierarchical and flow_aligned."""
        self._emit("config:toggle_layout", {})
        return ActionResult.ok("toggle_layout_mode", "Toggled layout mode")
    
    def set_verbose_logging(self, enabled: bool) -> ActionResult:
        """Enable/disable verbose logging."""
        self._emit("config:verbose_logging", {"enabled": enabled})
        return ActionResult.ok("set_verbose_logging", f"Verbose logging: {enabled}")
    
    # =========================================================================
    # Project Management
    # =========================================================================
    
    def switch_tab(self, tab_id: str) -> ActionResult:
        """Switch to a different project tab."""
        self._emit("project:switch_tab", {"tab_id": tab_id})
        return ActionResult.ok("switch_tab", f"Switched to tab {tab_id}")
    
    def close_tab(self, tab_id: str) -> ActionResult:
        """Close a project tab."""
        self._emit("project:close_tab", {"tab_id": tab_id})
        return ActionResult.ok("close_tab", f"Closed tab {tab_id}")
    
    def open_project(self, path: str) -> ActionResult:
        """Open a project as a new tab."""
        self._emit("project:open", {"path": path})
        return ActionResult.ok("open_project", f"Opening project: {path}")
    
    def load_repositories(self) -> ActionResult:
        """Load/reload repositories for current project."""
        self._emit("project:load_repos", {})
        return ActionResult.ok("load_repositories", "Loading repositories")
    
    def save_project(self) -> ActionResult:
        """Save the current project."""
        self._emit("project:save", {})
        return ActionResult.ok("save_project", "Saved project")
    
    # =========================================================================
    # Deeper Queries
    # =========================================================================
    
    def get_node_ancestors(self, node_id: str) -> List[str]:
        """Get all ancestor node IDs."""
        graph_service = self._services.graph if self._services else None
        if graph_service and hasattr(graph_service, 'get_ancestors'):
            return graph_service.get_ancestors(node_id)
        
        # Manual traversal
        ancestors = []
        if graph_service:
            visited = set()
            to_visit = []
            if hasattr(graph_service, 'get_parents'):
                to_visit = graph_service.get_parents(node_id)
            while to_visit:
                parent = to_visit.pop(0)
                if parent not in visited:
                    visited.add(parent)
                    ancestors.append(parent)
                    if hasattr(graph_service, 'get_parents'):
                        to_visit.extend(graph_service.get_parents(parent))
        return ancestors
    
    def get_node_descendants(self, node_id: str) -> List[str]:
        """Get all descendant node IDs."""
        graph_service = self._services.graph if self._services else None
        if graph_service and hasattr(graph_service, 'get_descendants'):
            return graph_service.get_descendants(node_id)
        
        descendants = []
        if graph_service:
            visited = set()
            to_visit = []
            if hasattr(graph_service, 'get_children'):
                to_visit = graph_service.get_children(node_id)
            while to_visit:
                child = to_visit.pop(0)
                if child not in visited:
                    visited.add(child)
                    descendants.append(child)
                    if hasattr(graph_service, 'get_children'):
                        to_visit.extend(graph_service.get_children(child))
        return descendants
    
    def get_node_branch(self, node_id: str) -> List[str]:
        """Get entire branch (ancestors + self + descendants)."""
        return self.get_node_ancestors(node_id) + [node_id] + self.get_node_descendants(node_id)
    
    def get_concept_value(self, concept_name: str) -> Any:
        """Get the computed value of a concept from blackboard."""
        controller = self._controller()
        if not controller:
            return None
        
        if hasattr(controller, 'get_concept_value'):
            return controller.get_concept_value(concept_name)
        
        if hasattr(controller, '_orchestrator') and controller._orchestrator:
            orch = controller._orchestrator
            if hasattr(orch, 'blackboard'):
                return orch.blackboard.get(concept_name)
        
        return None
    
    def get_same_concept_nodes(self, node_id: str) -> List[str]:
        """Get all nodes with the same concept name."""
        graph_service = self._services.graph if self._services else None
        if not graph_service:
            return []
        
        # Get concept name of this node
        node = None
        if hasattr(graph_service, 'get_node'):
            node = graph_service.get_node(node_id)
        
        if not node:
            return []
        
        concept_name = node.get('concept_name')
        if not concept_name:
            return []
        
        # Find all nodes with same concept
        result = []
        if hasattr(graph_service, 'get_nodes'):
            for n in graph_service.get_nodes():
                if n.get('concept_name') == concept_name and n.get('id') != node_id:
                    result.append(n.get('id'))
        
        return result
    
    # =========================================================================
    # Value Override
    # =========================================================================
    
    def override_value(self, concept_name: str, value: Any) -> ActionResult:
        """Override a concept's value in blackboard."""
        controller = self._controller()
        if controller and hasattr(controller, 'set_override'):
            try:
                controller.set_override(concept_name, value)
                self._emit("blackboard:override", {"concept": concept_name, "value": str(value)[:100]})
                return ActionResult.ok("override_value", f"Overrode {concept_name}")
            except Exception as e:
                return ActionResult.fail("override_value", str(e))
        
        self._emit("blackboard:override", {"concept": concept_name, "value": str(value)[:100]})
        return ActionResult.ok("override_value", f"Requested override for {concept_name}")
    
    def clear_override(self, concept_name: str) -> ActionResult:
        """Clear a value override."""
        controller = self._controller()
        if controller and hasattr(controller, 'clear_override'):
            try:
                controller.clear_override(concept_name)
                self._emit("blackboard:clear_override", {"concept": concept_name})
                return ActionResult.ok("clear_override", f"Cleared override for {concept_name}")
            except Exception as e:
                return ActionResult.fail("clear_override", str(e))
        
        self._emit("blackboard:clear_override", {"concept": concept_name})
        return ActionResult.ok("clear_override", f"Requested clear override for {concept_name}")

