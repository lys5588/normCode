"""
Format facade for Second Person perspective.

Wraps CanvasFormatterTool with a cleaner API.
"""

from typing import Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from tools.formatter_tool import CanvasFormatterTool


class FormatFacade:
    """
    Thin wrapper around CanvasFormatterTool.
    """
    
    def __init__(self, tool: Optional["CanvasFormatterTool"]):
        self._tool = tool
    
    def format(self, data: Any, format_type: str) -> str:
        """
        Format data to string representation.
        
        Args:
            data: Data to format
            format_type: Target format (json, yaml, text, etc.)
            
        Returns:
            Formatted string
        """
        if not self._tool:
            return str(data)
        
        if hasattr(self._tool, 'format'):
            return self._tool.format(data, format_type)
        elif hasattr(self._tool, 'to_string'):
            return self._tool.to_string(data, format_type)
        
        # Fallback
        import json
        if format_type == 'json':
            return json.dumps(data, indent=2)
        return str(data)
    
    def parse(self, content: str, format_type: str) -> Any:
        """
        Parse string to data structure.
        
        Args:
            content: Content to parse
            format_type: Source format
            
        Returns:
            Parsed data
        """
        if not self._tool:
            import json
            if format_type == 'json':
                return json.loads(content)
            return content
        
        if hasattr(self._tool, 'parse'):
            return self._tool.parse(content, format_type)
        elif hasattr(self._tool, 'from_string'):
            return self._tool.from_string(content, format_type)
        
        # Fallback
        import json
        if format_type == 'json':
            return json.loads(content)
        return content

