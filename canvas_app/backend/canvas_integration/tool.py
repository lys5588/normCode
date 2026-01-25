"""
Canvas Integration Tool - Unified interface for canvas interaction.

This is the single entry point for all canvas integration.
It composes the three perspectives and wraps existing tools.
"""

import logging
from typing import Any, Callable, Dict, Optional, TYPE_CHECKING

from .event_store import EventStore
from .perspectives import (
    FirstPersonPerspective,
    SecondPersonPerspective,
    ThirdPersonPerspective,
)
from .facades.system import ServiceContainer

if TYPE_CHECKING:
    from services.execution.controller import ExecutionController
    from services.graph_service import GraphService
    from tools.file_system_tool import CanvasFileSystemTool
    from tools.python_interpreter_tool import CanvasPythonInterpreterTool
    from tools.parser_tool import CanvasParserTool
    from tools.llm_tool import CanvasLLMTool
    from tools.prompt_tool import CanvasPromptTool
    from tools.paradigm_tool import CanvasParadigmTool
    from tools.model_runner_tool import CanvasModelRunnerTool
    from tools.composition_tool import CanvasCompositionTool
    from tools.perception_router_tool import CanvasPerceptionRouter
    from tools.formatter_tool import CanvasFormatterTool
    from tools.user_input_tool import CanvasUserInputTool
    from infra._orchest._db import OrchestratorDB

logger = logging.getLogger(__name__)


class CanvasIntegrationTool:
    """
    The unified canvas integration tool.
    
    Single entry point for all canvas interaction.
    
    Replaces: CanvasDisplayTool, CanvasChatTool (new implementation)
    Contains: All canvas tools (unchanged, wrapped)
    
    Usage:
        canvas = CanvasIntegrationTool(...)
        
        # First Person - user sees
        canvas.me.say("Hello")
        canvas.me.vision.get_canvas()
        canvas.me.mind.run()
        
        # Second Person - user doesn't see
        content = canvas.you.files.read("config.json")
        value = canvas.you.blackboard.get("X")
        
        # Third Person - observe activity
        for event in canvas.it.events.stream():
            ...
    """
    
    def __init__(
        self,
        # External dependencies
        emit_callback: Optional[Callable[[str, Dict], None]] = None,
        execution_getter: Optional[Callable[[], Optional["ExecutionController"]]] = None,
        
        # Services
        project_service: Optional[Any] = None,
        graph_service: Optional["GraphService"] = None,
        execution_service: Optional[Any] = None,
        parser_service: Optional[Any] = None,
        llm_settings_service: Optional[Any] = None,
        worker_registry: Optional[Any] = None,
        
        # Existing tools (for wrapping)
        file_tool: Optional["CanvasFileSystemTool"] = None,
        python_tool: Optional["CanvasPythonInterpreterTool"] = None,
        parser_tool: Optional["CanvasParserTool"] = None,
        llm_tool: Optional["CanvasLLMTool"] = None,
        prompt_tool: Optional["CanvasPromptTool"] = None,
        paradigm_tool: Optional["CanvasParadigmTool"] = None,
        model_runner_tool: Optional["CanvasModelRunnerTool"] = None,
        composition_tool: Optional["CanvasCompositionTool"] = None,
        perception_router: Optional["CanvasPerceptionRouter"] = None,
        formatter_tool: Optional["CanvasFormatterTool"] = None,
        user_input_tool: Optional["CanvasUserInputTool"] = None,
        
        # Database
        db: Optional["OrchestratorDB"] = None,
        
        # Configuration
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the Canvas Integration Tool.
        
        Args:
            emit_callback: Callback to emit WebSocket events
            execution_getter: Callable that returns current ExecutionController
            *_service: Backend services
            *_tool: Existing canvas tools to wrap
            db: OrchestratorDB for database access
            config: Additional configuration
        """
        # Store dependencies
        self._emit_callback = emit_callback or self._noop_emit
        self._execution_getter = execution_getter
        self._config = config or {}
        
        # Create service container
        self._services = ServiceContainer(
            project=project_service,
            graph=graph_service,
            execution=execution_service,
            parser=parser_service,
            llm_settings=llm_settings_service,
            worker_registry=worker_registry
        )
        
        # Store tool references (for backward compatibility access)
        self._file_tool = file_tool
        self._python_tool = python_tool
        self._parser_tool = parser_tool
        self._llm_tool = llm_tool
        self._prompt_tool = prompt_tool
        self._paradigm_tool = paradigm_tool
        self._model_runner_tool = model_runner_tool
        self._composition_tool = composition_tool
        self._perception_router = perception_router
        self._formatter_tool = formatter_tool
        self._user_input_tool = user_input_tool
        self._db = db
        
        # Create event store for Third Person
        self._event_store = EventStore(max_events=self._config.get('max_events', 10000))
        
        # Create wrapper emit that also records to event store
        def emit_with_recording(event_type: str, data: Dict[str, Any]):
            self._emit_callback(event_type, data)
            self._event_store.record(event_type, data)
        
        # Create perspectives
        self._me = FirstPersonPerspective(
            emit=emit_with_recording,
            execution_getter=execution_getter,
            services=self._services,
            event_store=self._event_store
        )
        
        self._you = SecondPersonPerspective(
            file_tool=file_tool,
            python_tool=python_tool,
            parser_tool=parser_tool,
            llm_tool=llm_tool,
            prompt_tool=prompt_tool,
            paradigm_tool=paradigm_tool,
            model_runner_tool=model_runner_tool,
            composition_tool=composition_tool,
            perception_router=perception_router,
            formatter_tool=formatter_tool,
            user_input_tool=user_input_tool,
            execution_getter=execution_getter,
            services=self._services,
            db=db
        )
        
        self._it = ThirdPersonPerspective(
            event_store=self._event_store
        )
        
        logger.debug("CanvasIntegrationTool initialized")
    
    def _noop_emit(self, event_type: str, data: Dict[str, Any]) -> None:
        """No-op emit for when no callback is provided."""
        logger.debug(f"Event (no handler): {event_type}")
    
    # =========================================================================
    # Perspective Properties
    # =========================================================================
    
    @property
    def me(self) -> FirstPersonPerspective:
        """
        First Person - "I am the user"
        
        Everything here affects what the user sees.
        Use for UI interaction and state changes.
        """
        return self._me
    
    @property
    def you(self) -> SecondPersonPerspective:
        """
        Second Person - "You are my helper"
        
        Private workspace for backend/tool access.
        User sees nothing until you show them via `me`.
        """
        return self._you
    
    @property
    def it(self) -> ThirdPersonPerspective:
        """
        Third Person - "What is happening"
        
        Observe system activity and events.
        Meta-level observation of the system.
        """
        return self._it
    
    # =========================================================================
    # Direct Tool Access (backward compatibility)
    # =========================================================================
    
    @property
    def user_input_tool(self) -> Optional["CanvasUserInputTool"]:
        """Direct access to user input tool (prefer you.input.*)."""
        return self._user_input_tool
    
    @property
    def parser_tool(self) -> Optional["CanvasParserTool"]:
        """Direct access to parser tool (prefer you.parser.*)."""
        return self._parser_tool
    
    @property
    def file_tool(self) -> Optional["CanvasFileSystemTool"]:
        """Direct access to file tool (prefer you.files.*)."""
        return self._file_tool
    
    @property
    def python_tool(self) -> Optional["CanvasPythonInterpreterTool"]:
        """Direct access to python tool (prefer you.code.*)."""
        return self._python_tool
    
    @property
    def llm_tool(self) -> Optional["CanvasLLMTool"]:
        """Direct access to LLM tool (prefer you.llm.*)."""
        return self._llm_tool
    
    @property
    def prompt_tool(self) -> Optional["CanvasPromptTool"]:
        """Direct access to prompt tool (prefer you.prompt.*)."""
        return self._prompt_tool
    
    @property
    def paradigm_tool(self) -> Optional["CanvasParadigmTool"]:
        """Direct access to paradigm tool (prefer you.paradigm.*)."""
        return self._paradigm_tool
    
    @property
    def model_runner_tool(self) -> Optional["CanvasModelRunnerTool"]:
        """Direct access to model runner tool (prefer you.model.*)."""
        return self._model_runner_tool
    
    @property
    def composition_tool(self) -> Optional["CanvasCompositionTool"]:
        """Direct access to composition tool (prefer you.compose.*)."""
        return self._composition_tool
    
    @property
    def perception_router(self) -> Optional["CanvasPerceptionRouter"]:
        """Direct access to perception router (prefer you.perceive.*)."""
        return self._perception_router
    
    @property
    def formatter_tool(self) -> Optional["CanvasFormatterTool"]:
        """Direct access to formatter tool (prefer you.format.*)."""
        return self._formatter_tool
    
    @property
    def db(self) -> Optional["OrchestratorDB"]:
        """Direct access to database (prefer you.db.*)."""
        return self._db
    
    @property
    def event_store(self) -> EventStore:
        """Access to the event store."""
        return self._event_store
    
    # =========================================================================
    # Configuration
    # =========================================================================
    
    def configure(self, **settings) -> None:
        """
        Update configuration for contained tools.
        
        Args:
            file_base_path: Base path for file operations
            python_timeout: Timeout for Python execution
            max_events: Maximum events to store
            ... other tool-specific settings
        """
        if 'file_base_path' in settings and self._file_tool:
            if hasattr(self._file_tool, 'set_base_path'):
                self._file_tool.set_base_path(settings['file_base_path'])
        
        if 'python_timeout' in settings and self._python_tool:
            if hasattr(self._python_tool, 'set_timeout'):
                self._python_tool.set_timeout(settings['python_timeout'])
        
        self._config.update(settings)
    
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration."""
        return self._config.copy()
    
    # =========================================================================
    # Utility Methods
    # =========================================================================
    
    def set_emit_callback(self, callback: Callable[[str, Dict], None]) -> None:
        """
        Set the emit callback for WebSocket events.
        
        Args:
            callback: Callback function (event_type, data) -> None
        """
        self._emit_callback = callback
        
        # Update First Person perspective
        def emit_with_recording(event_type: str, data: Dict[str, Any]):
            callback(event_type, data)
            self._event_store.record(event_type, data)
        
        # Recreate First Person with new emit
        self._me = FirstPersonPerspective(
            emit=emit_with_recording,
            execution_getter=self._execution_getter,
            services=self._services,
            event_store=self._event_store
        )
    
    def set_execution_getter(
        self, 
        getter: Callable[[], Optional["ExecutionController"]]
    ) -> None:
        """
        Set the execution controller getter.
        
        Args:
            getter: Callable that returns current ExecutionController
        """
        self._execution_getter = getter
        
        # Recreate perspectives with new getter
        self._me = FirstPersonPerspective(
            emit=self._emit_callback,
            execution_getter=getter,
            services=self._services,
            event_store=self._event_store
        )
        
        self._you = SecondPersonPerspective(
            file_tool=self._file_tool,
            python_tool=self._python_tool,
            parser_tool=self._parser_tool,
            llm_tool=self._llm_tool,
            prompt_tool=self._prompt_tool,
            paradigm_tool=self._paradigm_tool,
            model_runner_tool=self._model_runner_tool,
            composition_tool=self._composition_tool,
            perception_router=self._perception_router,
            formatter_tool=self._formatter_tool,
            user_input_tool=self._user_input_tool,
            execution_getter=getter,
            services=self._services,
            db=self._db
        )

