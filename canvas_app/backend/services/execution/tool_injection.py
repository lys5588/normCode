"""
Tool Injection - Wraps Body tools with monitoring proxies.

This module provides functionality to:
1. Wrap Body tools with MonitoredToolProxy for real-time monitoring
2. Inject canvas-specific tools (chat, user_input, canvas, parser, paradigm, model_runner) into Body

This enables the Agent Panel to show tool calls during execution.

Available injected tools:
- user_input: Human-in-the-loop input tool
- chat: Chat/message display tool
- canvas: Canvas display and query tool
- parser: NormCode parsing and serialization tool
- paradigm: Domain-specific paradigm tool
- model_runner: Model/paradigm execution tool
"""

import logging
from typing import Any, Callable, Dict, Optional

from services.agent_service import MonitoredToolProxy, ToolCallEvent, agent_registry
from tools.user_input_tool import CanvasUserInputTool
from tools.chat_tool import CanvasChatTool
from tools.canvas_tool import CanvasDisplayTool
from tools.parser_tool import CanvasParserTool
from tools.paradigm_tool import CanvasParadigmTool, create_canvas_paradigm_tool
from tools.model_runner_tool import CanvasModelRunnerTool
from tools.composition_tool import CanvasCompositionTool
from tools.perception_router_tool import CanvasPerceptionRouter
from tools.formatter_tool import CanvasFormatterTool

logger = logging.getLogger(__name__)


def wrap_body_with_monitoring(
    body: Any,
    get_flow_index: Callable[[], str],
    emit_tool_event: Callable[[ToolCallEvent], None],
) -> None:
    """
    Wrap a Body's tools with MonitoredToolProxy for real-time monitoring.
    
    This enables the Agent Panel to show tool calls during execution.
    
    Args:
        body: The Body instance to wrap tools on
        get_flow_index: Callback to get current flow index
        emit_tool_event: Callback to emit tool call events
    """
    # Wrap the main tools used during execution
    if hasattr(body, 'llm') and body.llm is not None:
        body.llm = MonitoredToolProxy(
            "default", "llm", body.llm,
            emit_tool_event, get_flow_index
        )
    
    if hasattr(body, 'file_system') and body.file_system is not None:
        body.file_system = MonitoredToolProxy(
            "default", "file_system", body.file_system,
            emit_tool_event, get_flow_index
        )
    
    if hasattr(body, 'python_interpreter') and body.python_interpreter is not None:
        body.python_interpreter = MonitoredToolProxy(
            "default", "python_interpreter", body.python_interpreter,
            emit_tool_event, get_flow_index
        )
    
    if hasattr(body, 'prompt_tool') and body.prompt_tool is not None:
        body.prompt_tool = MonitoredToolProxy(
            "default", "prompt", body.prompt_tool,
            emit_tool_event, get_flow_index
        )
    
    if hasattr(body, 'user_input') and body.user_input is not None:
        body.user_input = MonitoredToolProxy(
            "default", "user_input", body.user_input,
            emit_tool_event, get_flow_index
        )

    if hasattr(body, 'paradigm_tool') and body.paradigm_tool is not None:
        body.paradigm_tool = MonitoredToolProxy(
            "default", "paradigm", body.paradigm_tool,
            emit_tool_event, get_flow_index
        )
    
    if hasattr(body, 'chat') and body.chat is not None:
        body.chat = MonitoredToolProxy(
            "default", "chat", body.chat,
            emit_tool_event, get_flow_index
        )
    
    if hasattr(body, 'canvas') and body.canvas is not None:
        body.canvas = MonitoredToolProxy(
            "default", "canvas", body.canvas,
            emit_tool_event, get_flow_index
        )
    
    # Also wrap canvas_integration alias (for paradigm compatibility)
    if hasattr(body, 'canvas_integration') and body.canvas_integration is not None:
        # Only wrap if it's not the same object as body.canvas (avoid double-wrapping)
        if not hasattr(body, 'canvas') or body.canvas_integration is not body.canvas:
            body.canvas_integration = MonitoredToolProxy(
                "default", "canvas_integration", body.canvas_integration,
                emit_tool_event, get_flow_index
            )
        else:
            # Same object, just update the reference after canvas was wrapped
            body.canvas_integration = body.canvas
    
    if hasattr(body, 'parser') and body.parser is not None:
        body.parser = MonitoredToolProxy(
            "default", "parser", body.parser,
            emit_tool_event, get_flow_index
        )
    
    if hasattr(body, 'model_runner') and body.model_runner is not None:
        body.model_runner = MonitoredToolProxy(
            "default", "model_runner", body.model_runner,
            emit_tool_event, get_flow_index
        )
    
    if hasattr(body, 'composition_tool') and body.composition_tool is not None:
        body.composition_tool = MonitoredToolProxy(
            "default", "composition", body.composition_tool,
            emit_tool_event, get_flow_index
        )
    
    if hasattr(body, 'perception_router') and body.perception_router is not None:
        body.perception_router = MonitoredToolProxy(
            "default", "perception", body.perception_router,
            emit_tool_event, get_flow_index
        )
    
    # Note: formatter_tool is an internal tool used for data formatting
    # and doesn't benefit from high-level monitoring.
    
    logger.info("Wrapped body tools with monitoring proxies")


class CanvasToolSet:
    """
    Container for canvas-specific tools that can be injected into a Body.
    
    These tools enable human-in-the-loop interactions, canvas operations,
    NormCode parsing, paradigm loading, model execution, composition, and perception capabilities.
    """
    
    def __init__(
        self, 
        emit_callback: Callable[[str, Dict], None],
        execution_getter: Optional[Callable[[], Any]] = None,
        paradigm_dir: Optional[str] = None,
        base_dir: Optional[str] = None
    ):
        """
        Initialize the canvas tool set.
        
        Args:
            emit_callback: Callback to emit WebSocket events
            execution_getter: Optional callback to get the main ExecutionController
                             This enables canvas tool to query execution state
            paradigm_dir: Optional directory for custom paradigms
            base_dir: Base directory for resolving relative paradigm paths
        """
        # Core interaction tools
        self.user_input_tool = CanvasUserInputTool(emit_callback=emit_callback)
        self.chat_tool = CanvasChatTool(emit_callback=emit_callback, source="execution")
        self.canvas_tool = CanvasDisplayTool(
            emit_callback=emit_callback,
            execution_getter=execution_getter
        )
        self.parser_tool = CanvasParserTool()
        
        # Paradigm/model execution tools
        self.model_runner_tool = CanvasModelRunnerTool(emit_callback=emit_callback)
        self.composition_tool = CanvasCompositionTool(emit_callback=emit_callback)
        self.perception_router = CanvasPerceptionRouter(emit_callback=emit_callback)
        self.formatter_tool = CanvasFormatterTool(emit_callback=emit_callback)
        
        # Wire perception router into formatter tool for wrap() operations
        self.formatter_tool.perception_router = self.perception_router
        
        # Create paradigm tool if directory is specified
        self.paradigm_tool = None
        if paradigm_dir and base_dir:
            self.paradigm_tool = create_canvas_paradigm_tool(
                paradigm_dir=paradigm_dir,
                base_dir=base_dir,
                emit_callback=emit_callback
            )
    
    def inject_into_body(self, body: Any) -> None:
        """Inject all canvas tools into a Body instance."""
        # Core interaction tools
        body.user_input = self.user_input_tool
        body.chat = self.chat_tool
        body.canvas = self.canvas_tool
        body.parser = self.parser_tool
        
        # Paradigm/model execution tools
        body.model_runner = self.model_runner_tool
        body.composition_tool = self.composition_tool
        body.perception_router = self.perception_router
        body.formatter_tool = self.formatter_tool
        
        if self.paradigm_tool:
            body.paradigm_tool = self.paradigm_tool
        
        logger.info("Injected canvas tools into body (parser, model_runner, composition, perception, formatter)")
    
    def set_execution_getter(self, getter: Callable[[], Any]) -> None:
        """
        Set the execution getter for the canvas tool.
        
        This can be called after initialization to wire up the execution controller.
        """
        self.canvas_tool.set_execution_getter(getter)
    
    def set_paradigm_dir(self, paradigm_dir: str, base_dir: str, emit_callback: Callable[[str, Dict], None]) -> None:
        """
        Set or update the paradigm tool with a new paradigm directory.
        
        Args:
            paradigm_dir: Directory containing paradigm files
            base_dir: Base directory for resolving relative paths
            emit_callback: Callback for emitting WebSocket events
        """
        self.paradigm_tool = create_canvas_paradigm_tool(
            paradigm_dir=paradigm_dir,
            base_dir=base_dir,
            emit_callback=emit_callback
        )


def inject_canvas_tools(
    body: Any, 
    emit_callback: Callable[[str, Dict], None],
    execution_getter: Optional[Callable[[], Any]] = None,
    paradigm_dir: Optional[str] = None,
    base_dir: Optional[str] = None
) -> CanvasToolSet:
    """
    Create and inject canvas-specific tools into a Body.
    
    Args:
        body: The Body instance to inject tools into
        emit_callback: Callback to emit WebSocket events
        execution_getter: Optional callback to get the main ExecutionController
                         for querying execution state
        paradigm_dir: Optional directory for custom paradigms
        base_dir: Base directory for resolving relative paradigm paths
        
    Returns:
        CanvasToolSet containing the created tools
    """
    tool_set = CanvasToolSet(
        emit_callback, 
        execution_getter,
        paradigm_dir=paradigm_dir,
        base_dir=base_dir
    )
    tool_set.inject_into_body(body)
    return tool_set


def create_tool_event_emitter(
    emit_threadsafe: Callable[[str, Dict], None],
) -> Callable[[ToolCallEvent], None]:
    """
    Create a tool event emitter callback.
    
    Args:
        emit_threadsafe: Thread-safe emit function
        
    Returns:
        Callback that can be passed to MonitoredToolProxy
    """
    def emit_tool_event(event: ToolCallEvent):
        """Emit tool call event through WebSocket."""
        event_type = f"tool:call_{event.status}"
        emit_threadsafe(event_type, event.to_dict())
        # Also add to agent_registry history for persistence
        agent_registry.tool_call_history.append(event)
        if len(agent_registry.tool_call_history) > agent_registry.max_history:
            agent_registry.tool_call_history = agent_registry.tool_call_history[-agent_registry.max_history:]
    
    return emit_tool_event


def setup_tool_monitoring(
    body: Any,
    get_flow_index: Callable[[], str],
    emit_threadsafe: Callable[[str, Dict], None],
) -> None:
    """
    Complete tool monitoring setup for a Body.
    
    Creates the emit callback and wraps all tools with monitoring proxies.
    
    Args:
        body: The Body instance
        get_flow_index: Callback to get current flow index
        emit_threadsafe: Thread-safe emit function
    """
    emit_tool_event = create_tool_event_emitter(emit_threadsafe)
    wrap_body_with_monitoring(body, get_flow_index, emit_tool_event)


# =============================================================================
# NEW: Canvas Integration Tool Injection
# =============================================================================

def inject_canvas_integration(
    body: Any,
    emit_callback: Callable[[str, Dict], None],
    execution_getter: Optional[Callable[[], Any]] = None,
    services: Optional[Dict[str, Any]] = None,
    db: Optional[Any] = None,
    paradigm_dir: Optional[str] = None,
    base_dir: Optional[str] = None,
    use_unified_tool: bool = False,
) -> Any:
    """
    Inject canvas tools with optional unified CanvasIntegrationTool.
    
    This is the new recommended entry point that supports both:
    - Old style: Separate tools injected individually (backward compatible)
    - New style: Unified CanvasIntegrationTool with me/you/it perspectives
    
    Args:
        body: The Body instance to inject tools into
        emit_callback: Callback to emit WebSocket events
        execution_getter: Optional callback to get the main ExecutionController
        services: Dict of service instances (project, graph, execution, parser, llm_settings)
        db: OrchestratorDB instance for database access
        paradigm_dir: Optional directory for custom paradigms
        base_dir: Base directory for resolving relative paradigm paths
        use_unified_tool: If True, use new CanvasIntegrationTool; if False, use old separate tools
        
    Returns:
        CanvasIntegrationTool if use_unified_tool=True, else CanvasToolSet
    """
    if use_unified_tool:
        # NEW: Use unified CanvasIntegrationTool
        from canvas_integration import CanvasIntegrationTool
        from canvas_integration.injection import full_injection
        
        # Create tool instances that will be wrapped
        tools = {}
        
        # Create individual tools
        tools['user_input'] = CanvasUserInputTool(emit_callback=emit_callback)
        tools['parser'] = CanvasParserTool()
        tools['model_runner'] = CanvasModelRunnerTool(emit_callback=emit_callback)
        tools['composition'] = CanvasCompositionTool(emit_callback=emit_callback)
        tools['perception'] = CanvasPerceptionRouter(emit_callback=emit_callback)
        tools['formatter'] = CanvasFormatterTool(emit_callback=emit_callback)
        
        # Wire perception router into formatter tool
        tools['formatter'].perception_router = tools['perception']
        
        if paradigm_dir and base_dir:
            tools['paradigm'] = create_canvas_paradigm_tool(
                paradigm_dir=paradigm_dir,
                base_dir=base_dir,
                emit_callback=emit_callback
            )
        
        # Get services from body or passed dict
        services = services or {}
        
        # Inject unified tool
        canvas = full_injection(
            body=body,
            emit_callback=emit_callback,
            execution_getter=execution_getter,
            services=services,
            tools=tools,
            db=db
        )
        
        # Also inject old-style tools for backward compatibility
        body.user_input = canvas.user_input_tool
        body.chat = CanvasChatTool(emit_callback=emit_callback, source="execution")
        body.parser = canvas.parser_tool
        body.model_runner = canvas.model_runner_tool
        body.composition_tool = canvas.composition_tool
        body.perception_router = canvas.perception_router
        body.formatter_tool = canvas.formatter_tool if canvas.formatter_tool else tools['formatter']
        if canvas.paradigm_tool:
            body.paradigm_tool = canvas.paradigm_tool
        
        logger.info("Injected CanvasIntegrationTool with unified me/you/it perspectives (includes formatter_tool)")
        return canvas
    else:
        # OLD: Use separate tools (backward compatible)
        return inject_canvas_tools(
            body=body,
            emit_callback=emit_callback,
            execution_getter=execution_getter,
            paradigm_dir=paradigm_dir,
            base_dir=base_dir
        )
