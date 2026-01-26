"""
Prompt facade for Second Person perspective.

Wraps CanvasPromptTool with a cleaner API.
"""

from typing import Any, Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from tools.prompt_tool import CanvasPromptTool


class PromptFacade:
    """
    Thin wrapper around CanvasPromptTool.
    """
    
    def __init__(self, tool: Optional["CanvasPromptTool"]):
        self._tool = tool
    
    def read(self, path: str) -> str:
        """
        Read a prompt template from file.
        
        Args:
            path: Path to prompt file
            
        Returns:
            Template content
        """
        if not self._tool:
            return ""
        
        if hasattr(self._tool, 'read'):
            return self._tool.read(path)
        elif hasattr(self._tool, 'read_template'):
            return self._tool.read_template(path)
        
        raise NotImplementedError("prompt read not available")
    
    def substitute(self, template: str, **kwargs: Any) -> str:
        """
        Substitute variables in a template.
        
        Args:
            template: Template string with placeholders
            **kwargs: Values to substitute
            
        Returns:
            Filled template
        """
        if not self._tool:
            # Basic fallback
            result = template
            for key, value in kwargs.items():
                result = result.replace(f"{{{key}}}", str(value))
                result = result.replace(f"${{{key}}}", str(value))
            return result
        
        if hasattr(self._tool, 'substitute'):
            return self._tool.substitute(template, **kwargs)
        elif hasattr(self._tool, 'fill'):
            return self._tool.fill(template, kwargs)
        
        # Fallback to basic substitution
        result = template
        for key, value in kwargs.items():
            result = result.replace(f"{{{key}}}", str(value))
            result = result.replace(f"${{{key}}}", str(value))
        return result
    
    def read_and_substitute(self, path: str, **kwargs: Any) -> str:
        """
        Read template and substitute in one step.
        
        Args:
            path: Path to prompt file
            **kwargs: Values to substitute
            
        Returns:
            Filled template
        """
        template = self.read(path)
        return self.substitute(template, **kwargs)

