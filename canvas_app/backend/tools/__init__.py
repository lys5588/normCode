"""
Canvas App Tools - Custom tool implementations for the Canvas application.

These tools integrate with the Canvas app's WebSocket-based architecture
to provide real-time feedback and human-in-the-loop capabilities.

Tools:
- CanvasUserInputTool: WebSocket-based user input for human-in-the-loop
- CanvasFileSystemTool: File system with WebSocket notifications
- CanvasLLMTool: LLM with WebSocket notifications for prompts/responses
- CanvasPythonInterpreterTool: Python execution with WebSocket notifications
- CanvasPromptTool: Prompt template tool with WebSocket notifications
- CanvasChatTool: Chat interface for compiler-user interaction
- CanvasDisplayTool: Display artifacts on the Canvas (source, structure, graph)
- CanvasFormatterTool: Data formatting and parsing for paradigm composition
- CanvasCompositionTool: Function composition for paradigm execution
- CanvasParserTool: NormCode parsing and serialization tool
- CanvasParadigmTool: Domain-specific paradigm loading tool
- CanvasModelRunnerTool: Model/paradigm execution tool
"""

from .user_input_tool import CanvasUserInputTool
from .file_system_tool import CanvasFileSystemTool
from .llm_tool import CanvasLLMTool, get_available_llm_models
from .python_interpreter_tool import CanvasPythonInterpreterTool
from .prompt_tool import CanvasPromptTool
from .chat_tool import CanvasChatTool
from .canvas_tool import CanvasDisplayTool
from .formatter_tool import CanvasFormatterTool
from .composition_tool import CanvasCompositionTool
from .parser_tool import CanvasParserTool
from .paradigm_tool import CanvasParadigmTool, create_canvas_paradigm_tool
from .model_runner_tool import CanvasModelRunnerTool, CanvasModelEnv, CanvasModelSequenceRunner
from .perception_router_tool import CanvasPerceptionRouter, PerceptualSign

__all__ = [
    # Core tools
    "CanvasUserInputTool",
    "CanvasFileSystemTool",
    "CanvasLLMTool",
    "CanvasPythonInterpreterTool",
    "CanvasPromptTool",
    "CanvasChatTool",
    "CanvasDisplayTool",
    "CanvasFormatterTool",
    "CanvasCompositionTool",
    "CanvasParserTool",
    # Paradigm/model execution tools
    "CanvasParadigmTool",
    "create_canvas_paradigm_tool",
    "CanvasModelRunnerTool",
    "CanvasModelEnv",
    "CanvasModelSequenceRunner",
    # Perception
    "CanvasPerceptionRouter",
    "PerceptualSign",
    # Helpers
    "get_available_llm_models",
]
