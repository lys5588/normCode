"""
Execution service module - manages orchestrator execution with debugging support.

This module is organized into sub-modules for clarity:
- log_handler: Captures and parses orchestrator logs
- tool_injection: Tool monitoring and injection for Body
- checkpoint_service: Checkpoint listing, loading, and management
- value_service: Value override and dependency tracking
- controller: Core ExecutionController class
- worker_registry: Normalized worker management with flexible UI bindings (NEW)
- worker_manager: Legacy worker management (deprecated, use worker_registry)

Note: paradigm_tool has been moved to tools/paradigm_tool.py

The main execution_service.py file provides the facade and backwards-compatible API.
"""

from .log_handler import OrchestratorLogHandler, attach_log_handlers, detach_log_handlers

# Import from new location (tools/)
from tools.paradigm_tool import CanvasParadigmTool as CustomParadigmTool, create_canvas_paradigm_tool as create_paradigm_tool
from .tool_injection import (
    wrap_body_with_monitoring,
    inject_canvas_tools,
    CanvasToolSet,
    create_tool_event_emitter,
    setup_tool_monitoring,
)
from .checkpoint_service import CheckpointService, checkpoint_service
from .value_service import ValueService, value_service
from .controller import ExecutionController

# New normalized worker registry (preferred)
from .worker_registry import (
    WorkerRegistry,
    WorkerState,
    WorkerCategory,
    WorkerVisibility,
    WorkerStatus as RegistryWorkerStatus,
    PanelType,
    PanelBinding,
    RegisteredWorker,
    worker_registry,
    get_worker_registry,
)

# Legacy worker manager (deprecated - use WorkerRegistry)
from .worker_manager import (
    WorkerManager,
    WorkerType,
    WorkerStatus,
    WorkerInfo,
    worker_manager,
    get_worker_manager,
)

__all__ = [
    # Controller
    'ExecutionController',
    
    # Worker Registry (NEW - preferred)
    'WorkerRegistry',
    'WorkerState',
    'WorkerCategory',
    'WorkerVisibility',
    'RegistryWorkerStatus',
    'PanelType',
    'PanelBinding',
    'RegisteredWorker',
    'worker_registry',
    'get_worker_registry',
    
    # Worker Manager (LEGACY - deprecated)
    'WorkerManager',
    'WorkerType',
    'WorkerStatus',
    'WorkerInfo',
    'worker_manager',
    'get_worker_manager',
    
    # Log handler
    'OrchestratorLogHandler',
    'attach_log_handlers',
    'detach_log_handlers',
    
    # Paradigm tool
    'CustomParadigmTool',
    'create_paradigm_tool',
    
    # Tool injection
    'wrap_body_with_monitoring',
    'inject_canvas_tools',
    'CanvasToolSet',
    'create_tool_event_emitter',
    'setup_tool_monitoring',
    
    # Checkpoint service
    'CheckpointService',
    'checkpoint_service',
    
    # Value service
    'ValueService',
    'value_service',
]
