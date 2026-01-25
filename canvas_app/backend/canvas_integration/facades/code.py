"""
Code facade for Second Person perspective.

Wraps CanvasPythonInterpreterTool with a cleaner API.
"""

from typing import Any, Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from tools.python_interpreter_tool import CanvasPythonInterpreterTool


class CodeFacade:
    """
    Thin wrapper around CanvasPythonInterpreterTool.
    """
    
    def __init__(self, tool: "CanvasPythonInterpreterTool"):
        self._tool = tool
    
    def run(self, code: str, inputs: Optional[Dict[str, Any]] = None) -> Any:
        """
        Execute Python code.
        
        Args:
            code: Python code to execute
            inputs: Variables to inject into execution context
            
        Returns:
            Execution result
        """
        if hasattr(self._tool, 'execute'):
            return self._tool.execute(code, inputs or {})
        elif hasattr(self._tool, 'run'):
            return self._tool.run(code, inputs or {})
        raise NotImplementedError("execute not available")
    
    def run_function(
        self, 
        code: str, 
        function_name: str, 
        params: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Execute a specific function from code.
        
        Args:
            code: Python code containing the function
            function_name: Name of function to call
            params: Parameters to pass to function
            
        Returns:
            Function return value
        """
        if hasattr(self._tool, 'execute_function'):
            return self._tool.execute_function(code, function_name, params or {})
        # Fallback: execute code that calls the function
        call_code = f"{code}\n\n__result__ = {function_name}(**__params__)"
        result = self.run(call_code, {"__params__": params or {}})
        return result
    
    def eval(self, expression: str, context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Evaluate a Python expression.
        
        Args:
            expression: Python expression to evaluate
            context: Variables available in evaluation
            
        Returns:
            Expression result
        """
        code = f"__result__ = {expression}"
        self.run(code, context or {})
        # The tool should have captured __result__
        if hasattr(self._tool, 'get_result'):
            return self._tool.get_result()
        return None

