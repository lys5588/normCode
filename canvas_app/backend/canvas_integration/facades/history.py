"""
History facade for Second Person perspective.

Provides access to execution history and state snapshots.
"""

from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from services.execution.controller import ExecutionController


class HistoryFacade:
    """
    Provides access to execution history.
    
    Wraps ExecutionController's historical data access.
    """
    
    def __init__(self, execution_getter: Callable[[], Optional["ExecutionController"]]):
        """
        Initialize history facade.
        
        Args:
            execution_getter: Callable that returns current ExecutionController
        """
        self._get_controller = execution_getter
    
    def _controller(self) -> Optional["ExecutionController"]:
        """Get current execution controller."""
        return self._get_controller() if self._get_controller else None
    
    def get_trace(self, flow_index: str) -> Dict[str, Any]:
        """
        Get execution trace for a specific inference.
        
        Args:
            flow_index: The flow_index to trace
            
        Returns:
            Trace data including inputs, outputs, timing
        """
        controller = self._controller()
        if not controller:
            return {}
        
        if hasattr(controller, 'get_trace'):
            return controller.get_trace(flow_index)
        
        if hasattr(controller, 'get_inference_trace'):
            return controller.get_inference_trace(flow_index)
        
        return {}
    
    def get_state_at_cycle(self, cycle: int) -> Dict[str, Any]:
        """
        Get blackboard state at a specific cycle.
        
        Args:
            cycle: Cycle number
            
        Returns:
            State snapshot at that cycle
        """
        controller = self._controller()
        if not controller:
            return {}
        
        if hasattr(controller, 'get_state_at_cycle'):
            return controller.get_state_at_cycle(cycle)
        
        if hasattr(controller, '_orchestrator') and controller._orchestrator:
            orch = controller._orchestrator
            if hasattr(orch, 'get_checkpoint_at_cycle'):
                return orch.get_checkpoint_at_cycle(cycle)
        
        return {}
    
    def get_execution_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get history of execution events.
        
        Args:
            limit: Maximum events to return
            
        Returns:
            List of execution event records
        """
        controller = self._controller()
        if not controller:
            return []
        
        if hasattr(controller, 'get_execution_history'):
            return controller.get_execution_history(limit)
        
        if hasattr(controller, '_execution_history'):
            return list(controller._execution_history)[-limit:]
        
        return []
    
    def get_inference_stats(self) -> Dict[str, Any]:
        """
        Get statistics about inferences.
        
        Returns:
            Dict with counts, timing, etc.
        """
        controller = self._controller()
        if not controller:
            return {}
        
        if hasattr(controller, 'get_inference_stats'):
            return controller.get_inference_stats()
        
        if hasattr(controller, '_orchestrator') and controller._orchestrator:
            orch = controller._orchestrator
            stats = {
                "total_inferences": getattr(orch, 'inference_count', 0),
                "current_cycle": getattr(orch, 'cycle_count', 0),
            }
            return stats
        
        return {}
    
    def list_cycles(self) -> List[int]:
        """
        List all completed cycles.
        
        Returns:
            List of cycle numbers
        """
        controller = self._controller()
        if not controller:
            return []
        
        if hasattr(controller, 'list_cycles'):
            return controller.list_cycles()
        
        if hasattr(controller, '_orchestrator') and controller._orchestrator:
            orch = controller._orchestrator
            return list(range(1, getattr(orch, 'cycle_count', 0) + 1))
        
        return []

