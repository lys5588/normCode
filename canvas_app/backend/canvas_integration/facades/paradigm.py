"""
Paradigm facade for Second Person perspective.

Wraps CanvasParadigmTool with a cleaner API.
"""

from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from tools.paradigm_tool import CanvasParadigmTool


class ParadigmFacade:
    """
    Thin wrapper around CanvasParadigmTool.
    """
    
    def __init__(self, tool: Optional["CanvasParadigmTool"]):
        self._tool = tool
    
    def load(self, name: str) -> Any:
        """
        Load a paradigm by name.
        
        Args:
            name: Paradigm name
            
        Returns:
            Loaded paradigm object
        """
        if not self._tool:
            return None
        
        if hasattr(self._tool, 'load'):
            return self._tool.load(name)
        elif hasattr(self._tool, 'load_paradigm'):
            return self._tool.load_paradigm(name)
        
        raise NotImplementedError("paradigm load not available")
    
    def list_paradigms(self) -> List[str]:
        """
        List available paradigms.
        
        Returns:
            List of paradigm names
        """
        if not self._tool:
            return []
        
        if hasattr(self._tool, 'list_paradigms'):
            return self._tool.list_paradigms()
        elif hasattr(self._tool, 'list'):
            return self._tool.list()
        
        return []
    
    def list_manifest(self) -> List[Dict[str, Any]]:
        """
        Get manifest of all paradigms with metadata.
        
        Returns:
            List of paradigm metadata dicts
        """
        if not self._tool:
            return []
        
        if hasattr(self._tool, 'list_manifest'):
            return self._tool.list_manifest()
        elif hasattr(self._tool, 'get_manifest'):
            return self._tool.get_manifest()
        
        # Fallback: build from list
        return [{"name": name} for name in self.list_paradigms()]
    
    def get_info(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get info about a specific paradigm.
        
        Args:
            name: Paradigm name
            
        Returns:
            Paradigm info dict
        """
        if not self._tool:
            return None
        
        if hasattr(self._tool, 'get_info'):
            return self._tool.get_info(name)
        elif hasattr(self._tool, 'get_paradigm_info'):
            return self._tool.get_paradigm_info(name)
        
        return None

