"""
Model facade for Second Person perspective.

Wraps CanvasModelRunnerTool with a cleaner API.
"""

from typing import Any, Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from tools.model_runner_tool import CanvasModelRunnerTool


class ModelFacade:
    """
    Thin wrapper around CanvasModelRunnerTool.
    """
    
    def __init__(self, tool: Optional["CanvasModelRunnerTool"]):
        self._tool = tool
    
    def create_env(self, spec: Any = None, **kwargs: Any) -> Any:
        """
        Create a model execution environment.
        
        Args:
            spec: Environment specification
            **kwargs: Additional configuration
            
        Returns:
            ModelEnv instance
        """
        if not self._tool:
            return None
        
        if hasattr(self._tool, 'create_env'):
            return self._tool.create_env(spec, **kwargs)
        
        raise NotImplementedError("create_env not available")
    
    def run_sequence(self, states: Any, sequence_spec: Any) -> Dict[str, Any]:
        """
        Run a model sequence.
        
        Args:
            states: State object
            sequence_spec: Sequence specification
            
        Returns:
            Execution result
        """
        if not self._tool:
            return {"error": "Model runner tool not available"}
        
        if hasattr(self._tool, 'run_sequence'):
            return self._tool.run_sequence(states, sequence_spec)
        
        raise NotImplementedError("run_sequence not available")
    
    def execute_step(self, env: Any, step: Any) -> Any:
        """
        Execute a single model step.
        
        Args:
            env: Model environment
            step: Step specification
            
        Returns:
            Step result
        """
        if not self._tool:
            return None
        
        if hasattr(self._tool, 'execute_step'):
            return self._tool.execute_step(env, step)
        
        raise NotImplementedError("execute_step not available")
    
    def execute_affordance(
        self, 
        name: str, 
        context: Dict[str, Any],
        **kwargs: Any
    ) -> Any:
        """
        Execute a named affordance.
        
        Args:
            name: Affordance name
            context: Execution context
            **kwargs: Additional parameters
            
        Returns:
            Execution result
        """
        if not self._tool:
            return None
        
        if hasattr(self._tool, 'execute_affordance'):
            return self._tool.execute_affordance(name, context, **kwargs)
        
        raise NotImplementedError("execute_affordance not available")

