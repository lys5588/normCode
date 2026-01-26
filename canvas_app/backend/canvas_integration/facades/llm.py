"""
LLM facade for Second Person perspective.

Wraps CanvasLLMTool with a cleaner API.
"""

from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from tools.llm_tool import CanvasLLMTool


class LLMFacade:
    """
    Thin wrapper around CanvasLLMTool.
    """
    
    def __init__(self, tool: Optional["CanvasLLMTool"]):
        self._tool = tool
    
    def call(
        self, 
        prompt: str, 
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Call LLM with a prompt.
        
        Args:
            prompt: The prompt text
            model: Optional model override
            temperature: Optional temperature override
            max_tokens: Optional max tokens override
            
        Returns:
            LLM response text
        """
        if not self._tool:
            return "[LLM tool not available]"
        
        kwargs: Dict[str, Any] = {}
        if model:
            kwargs['model'] = model
        if temperature is not None:
            kwargs['temperature'] = temperature
        if max_tokens:
            kwargs['max_tokens'] = max_tokens
        
        if hasattr(self._tool, 'call'):
            return self._tool.call(prompt, **kwargs)
        elif hasattr(self._tool, 'complete'):
            return self._tool.complete(prompt, **kwargs)
        
        raise NotImplementedError("LLM call not available")
    
    def call_with_messages(
        self, 
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None
    ) -> str:
        """
        Call LLM with message history.
        
        Args:
            messages: List of {"role": str, "content": str} dicts
            model: Optional model override
            temperature: Optional temperature override
            
        Returns:
            LLM response text
        """
        if not self._tool:
            return "[LLM tool not available]"
        
        if hasattr(self._tool, 'call_with_messages'):
            return self._tool.call_with_messages(messages, model=model, temperature=temperature)
        
        # Fallback: convert to single prompt
        prompt = "\n".join([
            f"{m.get('role', 'user')}: {m.get('content', '')}" 
            for m in messages
        ])
        return self.call(prompt, model=model, temperature=temperature)
    
    def get_available_models(self) -> List[str]:
        """
        Get list of available models.
        
        Returns:
            List of model names
        """
        if not self._tool:
            return []
        
        if hasattr(self._tool, 'get_available_models'):
            return self._tool.get_available_models()
        
        if hasattr(self._tool, 'models'):
            return self._tool.models
        
        return []
    
    def get_current_model(self) -> Optional[str]:
        """
        Get currently configured model.
        
        Returns:
            Model name or None
        """
        if not self._tool:
            return None
        
        if hasattr(self._tool, 'get_current_model'):
            return self._tool.get_current_model()
        
        if hasattr(self._tool, 'model'):
            return self._tool.model
        
        return None

