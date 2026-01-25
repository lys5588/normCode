"""
Parser facade for Second Person perspective.

Wraps CanvasParserTool with a cleaner API.
"""

from typing import Any, Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from tools.parser_tool import CanvasParserTool


class ParserFacade:
    """
    Thin wrapper around CanvasParserTool.
    """
    
    def __init__(self, tool: "CanvasParserTool"):
        self._tool = tool
    
    def parse(self, content: str, format: str = "ncdn") -> Dict[str, Any]:
        """
        Parse content in specified format.
        
        Args:
            content: Content to parse
            format: Format type ("ncdn", "ncd", "yaml", "json")
            
        Returns:
            Parsed structure
        """
        if format == "ncdn":
            if hasattr(self._tool, 'parse_ncdn'):
                return self._tool.parse_ncdn(content)
        elif format == "ncd":
            if hasattr(self._tool, 'parse_ncd'):
                return self._tool.parse_ncd(content)
        
        # Generic parse
        if hasattr(self._tool, 'parse'):
            return self._tool.parse(content, format)
        
        raise NotImplementedError(f"parse for format {format} not available")
    
    def serialize(self, data: Dict[str, Any], format: str = "ncdn") -> str:
        """
        Serialize data to specified format.
        
        Args:
            data: Data to serialize
            format: Target format
            
        Returns:
            Serialized string
        """
        if format == "ncdn":
            if hasattr(self._tool, 'serialize_to_ncdn'):
                return self._tool.serialize_to_ncdn(data)
        elif format in ("ncd", "ncn"):
            if hasattr(self._tool, 'serialize_to_ncd_ncn'):
                return self._tool.serialize_to_ncd_ncn(data)
        
        if hasattr(self._tool, 'serialize'):
            return self._tool.serialize(data, format)
        
        raise NotImplementedError(f"serialize to format {format} not available")
    
    def convert(self, content: str, from_fmt: str, to_fmt: str) -> str:
        """
        Convert content between formats.
        
        Args:
            content: Content in source format
            from_fmt: Source format
            to_fmt: Target format
            
        Returns:
            Content in target format
        """
        if hasattr(self._tool, 'convert_format'):
            return self._tool.convert_format(content, from_fmt, to_fmt)
        
        # Fallback: parse then serialize
        data = self.parse(content, from_fmt)
        return self.serialize(data, to_fmt)
    
    def validate(self, content: str, format: str = "ncdn") -> Dict[str, Any]:
        """
        Validate content against format rules.
        
        Args:
            content: Content to validate
            format: Expected format
            
        Returns:
            Validation result with 'valid' and 'errors' keys
        """
        if hasattr(self._tool, 'validate'):
            return self._tool.validate(content, format)
        
        # Fallback: try parsing
        try:
            self.parse(content, format)
            return {"valid": True, "errors": []}
        except Exception as e:
            return {"valid": False, "errors": [str(e)]}

