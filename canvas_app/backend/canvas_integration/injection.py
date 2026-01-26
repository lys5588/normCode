"""
Canvas Integration Injection - Inject unified tool into Body.

This module provides functions to inject the CanvasIntegrationTool
into the execution Body, with backward compatibility for old tools.
"""

import logging
from typing import Any, Callable, Dict, Optional, TYPE_CHECKING

from .tool import CanvasIntegrationTool
from .facades.system import ServiceContainer

if TYPE_CHECKING:
    from services.execution.controller import ExecutionController
    from infra._agent._body import Body

logger = logging.getLogger(__name__)


def create_canvas_integration(
    emit_callback: Callable[[str, Dict], None],
    execution_getter: Optional[Callable[[], Optional["ExecutionController"]]] = None,
    services: Optional[Dict[str, Any]] = None,
    tools: Optional[Dict[str, Any]] = None,
    db: Optional[Any] = None,
    config: Optional[Dict[str, Any]] = None
) -> CanvasIntegrationTool:
    """
    Create a CanvasIntegrationTool with all dependencies.
    
    Args:
        emit_callback: WebSocket event emitter
        execution_getter: Callable that returns current ExecutionController
        services: Dict of service instances (project, graph, execution, parser, llm_settings)
        tools: Dict of tool instances (file, python, parser, llm, etc.)
        db: OrchestratorDB instance
        config: Additional configuration
        
    Returns:
        Configured CanvasIntegrationTool
    """
    services = services or {}
    tools = tools or {}
    
    return CanvasIntegrationTool(
        emit_callback=emit_callback,
        execution_getter=execution_getter,
        
        # Services
        project_service=services.get('project'),
        graph_service=services.get('graph'),
        execution_service=services.get('execution'),
        parser_service=services.get('parser'),
        llm_settings_service=services.get('llm_settings'),
        worker_registry=services.get('worker_registry'),
        
        # Tools
        file_tool=tools.get('file'),
        python_tool=tools.get('python'),
        parser_tool=tools.get('parser'),
        llm_tool=tools.get('llm'),
        prompt_tool=tools.get('prompt'),
        paradigm_tool=tools.get('paradigm'),
        model_runner_tool=tools.get('model_runner'),
        composition_tool=tools.get('composition'),
        perception_router=tools.get('perception'),
        formatter_tool=tools.get('formatter'),
        user_input_tool=tools.get('user_input'),
        
        # Database
        db=db,
        
        # Config
        config=config
    )


def inject_canvas_integration(
    body: "Body",
    emit_callback: Callable[[str, Dict], None],
    execution_getter: Optional[Callable[[], Optional["ExecutionController"]]] = None,
    services: Optional[Dict[str, Any]] = None,
    tools: Optional[Dict[str, Any]] = None,
    db: Optional[Any] = None,
    config: Optional[Dict[str, Any]] = None
) -> CanvasIntegrationTool:
    """
    Inject the unified canvas integration tool into a Body.
    
    This provides:
    - body.canvas: The unified CanvasIntegrationTool
    - body.canvas.me / .you / .it: Three perspectives
    - Backward compatibility: Direct tool access via body.canvas.*_tool
    
    Args:
        body: The Body instance to inject into
        emit_callback: WebSocket event emitter
        execution_getter: Callable that returns current ExecutionController
        services: Dict of service instances
        tools: Dict of existing tool instances to wrap
        db: OrchestratorDB instance
        config: Additional configuration
        
    Returns:
        The injected CanvasIntegrationTool
    """
    # Create the unified tool
    canvas = create_canvas_integration(
        emit_callback=emit_callback,
        execution_getter=execution_getter,
        services=services,
        tools=tools,
        db=db,
        config=config
    )
    
    # Inject as primary access point
    body.canvas = canvas
    
    # Also register under canvas_integration for paradigm compatibility
    # Paradigms like c_CanvasIntegrationGetChat-o_Literal use tool_name: "canvas_integration"
    body.canvas_integration = canvas
    
    logger.info("Injected CanvasIntegrationTool into body.canvas (also aliased as body.canvas_integration)")
    
    return canvas


def inject_backward_compatible_tools(
    body: "Body",
    canvas: CanvasIntegrationTool
) -> None:
    """
    Inject backward-compatible tool references into Body.
    
    This ensures old code using body.tools.* still works.
    
    Args:
        body: The Body instance
        canvas: The CanvasIntegrationTool
    """
    # Ensure body.tools exists
    if not hasattr(body, 'tools'):
        class ToolContainer:
            pass
        body.tools = ToolContainer()
    
    tools = body.tools
    
    # Inject tool references
    if canvas.user_input_tool:
        tools.user_input = canvas.user_input_tool
    if canvas.parser_tool:
        tools.parser = canvas.parser_tool
    if canvas.file_tool:
        tools.files = canvas.file_tool
        tools.file = canvas.file_tool  # alias
    if canvas.python_tool:
        tools.python = canvas.python_tool
    if canvas.llm_tool:
        tools.llm = canvas.llm_tool
    if canvas.prompt_tool:
        tools.prompt = canvas.prompt_tool
    if canvas.paradigm_tool:
        tools.paradigm = canvas.paradigm_tool
    if canvas.model_runner_tool:
        tools.model_runner = canvas.model_runner_tool
    if canvas.composition_tool:
        tools.composition = canvas.composition_tool
    if canvas.perception_router:
        tools.perception = canvas.perception_router
    if canvas.formatter_tool:
        tools.formatter = canvas.formatter_tool
    
    logger.debug("Injected backward-compatible tools into body.tools")


def full_injection(
    body: "Body",
    emit_callback: Callable[[str, Dict], None],
    execution_getter: Optional[Callable[[], Optional["ExecutionController"]]] = None,
    services: Optional[Dict[str, Any]] = None,
    tools: Optional[Dict[str, Any]] = None,
    db: Optional[Any] = None,
    config: Optional[Dict[str, Any]] = None
) -> CanvasIntegrationTool:
    """
    Full injection with both new and backward-compatible access.
    
    This is the recommended entry point for injection.
    
    Provides:
    - body.canvas: Unified tool with me/you/it perspectives
    - body.tools.*: Backward-compatible individual tool access
    
    Args:
        body: The Body instance
        emit_callback: WebSocket event emitter
        execution_getter: Callable that returns current ExecutionController
        services: Dict of service instances
        tools: Dict of existing tool instances
        db: OrchestratorDB instance
        config: Additional configuration
        
    Returns:
        The injected CanvasIntegrationTool
    """
    # Inject unified tool
    canvas = inject_canvas_integration(
        body=body,
        emit_callback=emit_callback,
        execution_getter=execution_getter,
        services=services,
        tools=tools,
        db=db,
        config=config
    )
    
    # Inject backward-compatible references
    inject_backward_compatible_tools(body, canvas)
    
    return canvas

