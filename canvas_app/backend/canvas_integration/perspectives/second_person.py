"""
Second Person Perspective - "You are my helper"

AI's private workspace / direct tool access.
User sees nothing (except when using input tool).
"""

from typing import Callable, Optional, TYPE_CHECKING

from ..facades import (
    FilesFacade,
    CodeFacade,
    ParserFacade,
    BlackboardFacade,
    GraphFacade,
    DatabaseFacade,
    LLMFacade,
    PromptFacade,
    ParadigmFacade,
    ModelFacade,
    ComposeFacade,
    PerceiveFacade,
    FormatFacade,
    InputFacade,
    SystemFacade,
    HistoryFacade,
)
from ..facades.system import ServiceContainer

if TYPE_CHECKING:
    from services.execution.controller import ExecutionController
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


class SecondPersonPerspective:
    """
    "You are my helper" - private workspace / direct tool access.
    
    All canvas tools are accessible here for direct invocation.
    Does NOT affect shared UI state or what user sees.
    
    Categories:
    - Data access: files, blackboard, parser, graph, db
    - Execution: code, llm, prompt
    - Paradigm/model: paradigm, model, compose, perceive, format
    - Interaction: input
    - System: system, history
    """
    
    def __init__(
        self,
        # Canvas tools
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
        # Services
        execution_getter: Optional[Callable[[], Optional["ExecutionController"]]] = None,
        services: Optional[ServiceContainer] = None,
        db: Optional["OrchestratorDB"] = None
    ):
        """
        Initialize Second Person perspective.
        
        All parameters are optional to allow partial initialization.
        """
        # Data access facades
        self._files = FilesFacade(file_tool) if file_tool else None
        self._parser = ParserFacade(parser_tool) if parser_tool else None
        self._blackboard = BlackboardFacade(execution_getter) if execution_getter else None
        self._graph = GraphFacade(services.graph if services else None)
        self._db = DatabaseFacade(db)
        
        # Execution facades
        self._code = CodeFacade(python_tool) if python_tool else None
        self._llm = LLMFacade(llm_tool)
        self._prompt = PromptFacade(prompt_tool)
        
        # Paradigm/model facades
        self._paradigm = ParadigmFacade(paradigm_tool)
        self._model = ModelFacade(model_runner_tool)
        self._compose = ComposeFacade(composition_tool)
        self._perceive = PerceiveFacade(perception_router)
        self._format = FormatFacade(formatter_tool)
        
        # Interaction
        self._input = InputFacade(user_input_tool)
        
        # System
        self._system = SystemFacade(services)
        self._history = HistoryFacade(execution_getter) if execution_getter else None
    
    # =========================================================================
    # Data Access
    # =========================================================================
    
    @property
    def files(self) -> Optional[FilesFacade]:
        """File system operations."""
        return self._files
    
    @property
    def blackboard(self) -> Optional[BlackboardFacade]:
        """Computed concept values."""
        return self._blackboard
    
    @property
    def parser(self) -> Optional[ParserFacade]:
        """NormCode parsing."""
        return self._parser
    
    @property
    def graph(self) -> GraphFacade:
        """Graph structure queries."""
        return self._graph
    
    @property
    def db(self) -> DatabaseFacade:
        """Direct database queries."""
        return self._db
    
    # =========================================================================
    # Execution
    # =========================================================================
    
    @property
    def code(self) -> Optional[CodeFacade]:
        """Python execution."""
        return self._code
    
    @property
    def llm(self) -> LLMFacade:
        """Language model calls."""
        return self._llm
    
    @property
    def prompt(self) -> PromptFacade:
        """Prompt templates."""
        return self._prompt
    
    # =========================================================================
    # Paradigm/Model
    # =========================================================================
    
    @property
    def paradigm(self) -> ParadigmFacade:
        """Paradigm loading."""
        return self._paradigm
    
    @property
    def model(self) -> ModelFacade:
        """Model execution."""
        return self._model
    
    @property
    def compose(self) -> ComposeFacade:
        """Function composition."""
        return self._compose
    
    @property
    def perceive(self) -> PerceiveFacade:
        """Perception routing."""
        return self._perceive
    
    @property
    def format(self) -> FormatFacade:
        """Data formatting."""
        return self._format
    
    # =========================================================================
    # Interaction
    # =========================================================================
    
    @property
    def input(self) -> InputFacade:
        """User input requests."""
        return self._input
    
    # =========================================================================
    # System
    # =========================================================================
    
    @property
    def system(self) -> SystemFacade:
        """System state."""
        return self._system
    
    @property
    def history(self) -> Optional[HistoryFacade]:
        """Execution history."""
        return self._history

