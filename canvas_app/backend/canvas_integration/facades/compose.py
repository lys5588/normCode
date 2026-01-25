"""
Compose facade for Second Person perspective.

Wraps CanvasCompositionTool with a cleaner API.
"""

from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from tools.composition_tool import CanvasCompositionTool


class ComposeFacade:
    """
    Thin wrapper around CanvasCompositionTool.
    """
    
    def __init__(self, tool: Optional["CanvasCompositionTool"]):
        self._tool = tool
    
    def compose(self, plan: List[Dict[str, Any]]) -> Callable:
        """
        Compose multiple functions into a single callable.
        
        Args:
            plan: List of step definitions
            
        Returns:
            Composed callable
        """
        if not self._tool:
            raise NotImplementedError("Composition tool not available")
        
        if hasattr(self._tool, 'compose'):
            return self._tool.compose(plan)
        
        raise NotImplementedError("compose not available")
    
    def execute_plan(
        self, 
        plan: List[Dict[str, Any]], 
        input_data: Any
    ) -> Any:
        """
        Compose and execute a plan with input.
        
        Args:
            plan: List of step definitions
            input_data: Initial input
            
        Returns:
            Execution result
        """
        if not self._tool:
            return {"error": "Composition tool not available"}
        
        if hasattr(self._tool, 'execute_plan'):
            return self._tool.execute_plan(plan, input_data)
        
        # Fallback: compose then call
        composed = self.compose(plan)
        return composed(input_data)
    
    def validate_plan(self, plan: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate a composition plan.
        
        Args:
            plan: Plan to validate
            
        Returns:
            Validation result with 'valid' and 'errors' keys
        """
        if not self._tool:
            return {"valid": False, "errors": ["Composition tool not available"]}
        
        if hasattr(self._tool, 'validate_plan'):
            return self._tool.validate_plan(plan)
        
        # Basic validation
        if not isinstance(plan, list):
            return {"valid": False, "errors": ["Plan must be a list"]}
        
        return {"valid": True, "errors": []}

