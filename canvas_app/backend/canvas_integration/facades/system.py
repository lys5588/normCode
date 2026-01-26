"""
System facade for Second Person perspective.

Provides access to system state (workers, connections, tools).
"""

from typing import Any, Dict, List, Optional


class ServiceContainer:
    """Container for backend services."""
    
    def __init__(
        self,
        project: Any = None,
        graph: Any = None,
        execution: Any = None,
        parser: Any = None,
        llm_settings: Any = None,
        worker_registry: Any = None
    ):
        self.project = project
        self.graph = graph
        self.execution = execution
        self.parser = parser
        self.llm_settings = llm_settings
        self.worker_registry = worker_registry


class SystemFacade:
    """
    Provides access to system state.
    
    Wraps worker registry and service connections.
    """
    
    def __init__(self, services: Optional[ServiceContainer]):
        self._services = services
    
    def get_workers(self) -> List[Dict[str, Any]]:
        """
        Get list of registered workers.
        
        Returns:
            List of worker info dicts
        """
        if not self._services or not self._services.worker_registry:
            return []
        
        registry = self._services.worker_registry
        
        if hasattr(registry, 'get_workers'):
            return registry.get_workers()
        elif hasattr(registry, 'list_workers'):
            return registry.list_workers()
        elif hasattr(registry, 'workers'):
            return list(registry.workers.values())
        
        return []
    
    def get_connections(self) -> Dict[str, Any]:
        """
        Get current service connections status.
        
        Returns:
            Dict with connection status for each service
        """
        if not self._services:
            return {}
        
        status = {}
        
        # Check each service
        for name in ['project', 'graph', 'execution', 'parser', 'llm_settings']:
            service = getattr(self._services, name, None)
            if service is None:
                status[name] = {"connected": False, "status": "not configured"}
            else:
                status[name] = {"connected": True, "status": "available"}
        
        return status
    
    def get_tool_calls(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get recent tool call history.
        
        Args:
            limit: Maximum calls to return
            
        Returns:
            List of tool call records
        """
        # This would need to be tracked separately
        # For now, return empty
        return []
    
    def get_active_executions(self) -> List[Dict[str, Any]]:
        """
        Get currently active executions.
        
        Returns:
            List of active execution info
        """
        if not self._services or not self._services.execution:
            return []
        
        exec_service = self._services.execution
        
        if hasattr(exec_service, 'get_active_executions'):
            return exec_service.get_active_executions()
        elif hasattr(exec_service, 'active_controllers'):
            return [{"id": k} for k in exec_service.active_controllers.keys()]
        
        return []
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get current system configuration.
        
        Returns:
            Configuration dict
        """
        config = {}
        
        if self._services and self._services.llm_settings:
            llm = self._services.llm_settings
            if hasattr(llm, 'get_settings'):
                config['llm'] = llm.get_settings()
            elif hasattr(llm, 'settings'):
                config['llm'] = llm.settings
        
        return config

