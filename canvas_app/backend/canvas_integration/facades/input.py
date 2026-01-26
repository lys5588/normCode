"""
Input facade for Second Person perspective.

Wraps CanvasUserInputTool with a cleaner API.
"""

from typing import Any, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from tools.user_input_tool import CanvasUserInputTool


class InputFacade:
    """
    Thin wrapper around CanvasUserInputTool.
    
    Note: This DOES interact with user (shows input dialog),
    but the request itself is a direct tool call, not UI navigation.
    """
    
    def __init__(self, tool: Optional["CanvasUserInputTool"]):
        self._tool = tool
    
    def request(
        self, 
        prompt: str, 
        input_type: str = "text",
        default: Optional[str] = None,
        timeout: Optional[float] = None
    ) -> str:
        """
        Request input from user (blocking).
        
        Args:
            prompt: Prompt to show user
            input_type: Type of input (text, code, etc.)
            default: Default value
            timeout: Optional timeout in seconds
            
        Returns:
            User's input
        """
        if not self._tool:
            return default or ""
        
        options = {}
        if default:
            options['default'] = default
        if timeout:
            options['timeout'] = timeout
        
        if hasattr(self._tool, 'request_input'):
            return self._tool.request_input(prompt, input_type, options)
        elif hasattr(self._tool, 'ask'):
            return self._tool.ask(prompt)
        
        raise NotImplementedError("input request not available")
    
    def request_choice(
        self, 
        prompt: str, 
        choices: List[str],
        default: Optional[str] = None
    ) -> str:
        """
        Request choice from user.
        
        Args:
            prompt: Prompt to show
            choices: List of choices
            default: Default selection
            
        Returns:
            Selected choice
        """
        if not self._tool:
            return default or (choices[0] if choices else "")
        
        options = {'choices': choices}
        if default:
            options['default'] = default
        
        if hasattr(self._tool, 'request_input'):
            return self._tool.request_input(prompt, 'select', options)
        elif hasattr(self._tool, 'select'):
            return self._tool.select(prompt, choices)
        
        raise NotImplementedError("choice request not available")
    
    def request_confirmation(
        self, 
        prompt: str, 
        default: bool = False
    ) -> bool:
        """
        Request yes/no confirmation.
        
        Args:
            prompt: Prompt to show
            default: Default value
            
        Returns:
            True for yes, False for no
        """
        if not self._tool:
            return default
        
        if hasattr(self._tool, 'request_input'):
            result = self._tool.request_input(prompt, 'confirm', {'default': default})
            return result in (True, 'true', 'yes', 'y', '1')
        elif hasattr(self._tool, 'confirm'):
            return self._tool.confirm(prompt)
        
        raise NotImplementedError("confirmation request not available")
    
    def request_code(
        self,
        prompt: str,
        language: str = "python",
        initial_value: str = ""
    ) -> str:
        """
        Request code input with editor.
        
        Args:
            prompt: Prompt to show
            language: Programming language
            initial_value: Initial code
            
        Returns:
            Code entered by user
        """
        if not self._tool:
            return initial_value
        
        options = {
            'language': language,
            'initial_value': initial_value
        }
        
        if hasattr(self._tool, 'request_input'):
            return self._tool.request_input(prompt, 'code', options)
        
        # Fallback to text
        return self.request(prompt, 'text', initial_value)

