"""
Perceive facade for Second Person perspective.

Wraps CanvasPerceptionRouter with a cleaner API.
"""

from typing import Any, Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from tools.perception_router_tool import CanvasPerceptionRouter


class PerceiveFacade:
    """
    Thin wrapper around CanvasPerceptionRouter.
    """
    
    def __init__(self, tool: Optional["CanvasPerceptionRouter"]):
        self._tool = tool
    
    def encode_sign(self, content: Any, norm: Optional[str] = None) -> str:
        """
        Create a perceptual sign from content.
        
        Args:
            content: Content to encode
            norm: Optional norm identifier
            
        Returns:
            Encoded sign string
        """
        if not self._tool:
            return str(content)
        
        if hasattr(self._tool, 'encode_sign'):
            return self._tool.encode_sign(content, norm)
        
        raise NotImplementedError("encode_sign not available")
    
    def decode_sign(self, token: str) -> Optional[Dict]:
        """
        Decode a perceptual sign.
        
        Args:
            token: Sign string to decode
            
        Returns:
            Decoded sign dict or None
        """
        if not self._tool:
            return None
        
        if hasattr(self._tool, 'decode_sign'):
            return self._tool.decode_sign(token)
        
        return None
    
    def perceive(self, token: Any, body: Any) -> Any:
        """
        Apply perception to transform token using body faculties.
        
        Args:
            token: Token to perceive
            body: Body with faculties
            
        Returns:
            Transformed result
        """
        if not self._tool:
            return token
        
        if hasattr(self._tool, 'perceive'):
            return self._tool.perceive(token, body)
        
        return token
    
    def transform(self, token: Any, config: Dict, body: Any) -> Any:
        """
        Apply transformation based on config.
        
        Args:
            token: Token to transform
            config: Transformation configuration
            body: Body with faculties
            
        Returns:
            Transformed result
        """
        if not self._tool:
            return token
        
        if hasattr(self._tool, 'transform'):
            return self._tool.transform(token, config, body)
        
        return token
    
    def strip_sign(self, token: Any) -> Any:
        """
        Strip perceptual sign wrapper from token.
        
        Args:
            token: Token that may contain sign
            
        Returns:
            Content without sign wrapper
        """
        if not self._tool:
            return token
        
        if hasattr(self._tool, 'strip_sign'):
            return self._tool.strip_sign(token)
        
        return token

