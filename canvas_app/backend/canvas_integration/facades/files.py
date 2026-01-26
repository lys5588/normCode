"""
Files facade for Second Person perspective.

Wraps CanvasFileSystemTool with a cleaner API.
"""

import json
from typing import Any, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from tools.file_system_tool import CanvasFileSystemTool


class FilesFacade:
    """
    Thin wrapper around CanvasFileSystemTool.
    
    Provides cleaner API but delegates all work to existing tool.
    """
    
    def __init__(self, tool: "CanvasFileSystemTool"):
        self._tool = tool
    
    def read(self, path: str) -> str:
        """Read file contents."""
        return self._tool.read_file(path)
    
    def write(self, path: str, content: str) -> str:
        """Write content to file."""
        return self._tool.write_file(path, content)
    
    def read_json(self, path: str) -> Any:
        """Read and parse JSON file."""
        if hasattr(self._tool, 'read_json'):
            return self._tool.read_json(path)
        content = self.read(path)
        return json.loads(content)
    
    def write_json(self, path: str, data: Any, indent: int = 2) -> str:
        """Write data as JSON file."""
        if hasattr(self._tool, 'write_json'):
            return self._tool.write_json(path, data)
        content = json.dumps(data, indent=indent)
        return self.write(path, content)
    
    def list_dir(self, path: str = ".") -> List[str]:
        """List directory contents."""
        if hasattr(self._tool, 'list_directory'):
            return self._tool.list_directory(path)
        elif hasattr(self._tool, 'list_dir'):
            return self._tool.list_dir(path)
        raise NotImplementedError("list_dir not available")
    
    def exists(self, path: str) -> bool:
        """Check if path exists."""
        if hasattr(self._tool, 'exists'):
            return self._tool.exists(path)
        try:
            self.read(path)
            return True
        except:
            return False
    
    def delete(self, path: str) -> str:
        """Delete a file."""
        if hasattr(self._tool, 'delete'):
            return self._tool.delete(path)
        elif hasattr(self._tool, 'delete_file'):
            return self._tool.delete_file(path)
        raise NotImplementedError("delete not available")
    
    def mkdir(self, path: str) -> str:
        """Create directory."""
        if hasattr(self._tool, 'mkdir'):
            return self._tool.mkdir(path)
        elif hasattr(self._tool, 'create_directory'):
            return self._tool.create_directory(path)
        raise NotImplementedError("mkdir not available")
    
    def copy(self, src: str, dst: str) -> str:
        """Copy file."""
        if hasattr(self._tool, 'copy'):
            return self._tool.copy(src, dst)
        # Fallback: read and write
        content = self.read(src)
        return self.write(dst, content)
    
    def move(self, src: str, dst: str) -> str:
        """Move file."""
        if hasattr(self._tool, 'move'):
            return self._tool.move(src, dst)
        # Fallback: copy and delete
        self.copy(src, dst)
        return self.delete(src)

