"""
Blackboard facade for Second Person perspective.

Provides access to computed concept values via ExecutionController.
"""

from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from services.execution.controller import ExecutionController


class BlackboardFacade:
    """
    Provides access to blackboard (computed concept values).
    
    Wraps ExecutionController's blackboard access.
    """
    
    def __init__(self, execution_getter: Callable[[], Optional["ExecutionController"]]):
        """
        Initialize blackboard facade.
        
        Args:
            execution_getter: Callable that returns current ExecutionController
        """
        self._get_controller = execution_getter
    
    def _controller(self) -> Optional["ExecutionController"]:
        """Get current execution controller."""
        return self._get_controller() if self._get_controller else None
    
    def get(self, concept_name: str) -> Any:
        """
        Get value of a computed concept.
        
        Args:
            concept_name: Name of concept
            
        Returns:
            Concept value or None if not computed
        """
        controller = self._controller()
        if not controller:
            return None
        
        if hasattr(controller, 'get_concept_value'):
            return controller.get_concept_value(concept_name)
        
        # Try accessing blackboard directly
        if hasattr(controller, '_orchestrator') and controller._orchestrator:
            orch = controller._orchestrator
            if hasattr(orch, 'blackboard'):
                return orch.blackboard.get(concept_name)
        
        return None
    
    def get_all(self) -> Dict[str, Any]:
        """
        Get all computed concept values.
        
        Returns:
            Dict of concept_name -> value
        """
        controller = self._controller()
        if not controller:
            return {}
        
        if hasattr(controller, 'get_all_values'):
            return controller.get_all_values()
        
        if hasattr(controller, '_orchestrator') and controller._orchestrator:
            orch = controller._orchestrator
            if hasattr(orch, 'blackboard') and hasattr(orch.blackboard, 'get_all'):
                return orch.blackboard.get_all()
        
        return {}
    
    def get_status(self, concept_name: str) -> Optional[str]:
        """
        Get computation status of a concept.
        
        Args:
            concept_name: Name of concept
            
        Returns:
            Status string or None
        """
        controller = self._controller()
        if not controller:
            return None
        
        if hasattr(controller, 'get_node_status'):
            return controller.get_node_status(concept_name)
        
        return None
    
    def list_concepts(self) -> List[str]:
        """
        List all known concept names.
        
        Returns:
            List of concept names
        """
        controller = self._controller()
        if not controller:
            return []
        
        if hasattr(controller, 'list_concepts'):
            return controller.list_concepts()
        
        # Try getting from blackboard
        all_values = self.get_all()
        return list(all_values.keys())
    
    def get_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get execution logs.
        
        Args:
            limit: Maximum number of log entries
            
        Returns:
            List of log entries
        """
        controller = self._controller()
        if not controller:
            return []
        
        if hasattr(controller, 'get_logs'):
            return controller.get_logs(limit)
        
        if hasattr(controller, '_logs'):
            return list(controller._logs)[-limit:]
        
        return []
    
    def is_computed(self, concept_name: str) -> bool:
        """
        Check if a concept has been computed.
        
        Args:
            concept_name: Name of concept
            
        Returns:
            True if computed
        """
        return self.get(concept_name) is not None

