# Canvas Integration Tool

**One unified tool** that provides the three-perspective interface for canvas interaction.

- **Replaces** `CanvasDisplayTool` and `CanvasChatTool` with new perspective-based implementation
- **Contains** existing tools (`CanvasUserInputTool`, `CanvasParserTool`, `CanvasFileSystemTool`, `CanvasPythonInterpreterTool`) - unchanged, just wrapped and configured through canvas

---

## Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        CanvasIntegrationTool                                │
│                                                                             │
│    REPLACES (new implementation, old kept for backward compatibility):      │
│    ├── CanvasDisplayTool  ─┐                                                │
│    └── CanvasChatTool     ─┴──→  me.* (First Person perspectives)           │
│                                                                             │
│    PROVIDES:                                                                │
│    ├── me   (First Person)  - Shared stage, user sees                       │
│    ├── you  (Second Person) - Private workspace, user doesn't see           │
│    └── it   (Third Person)  - Activity observation                          │
│                                                                             │
│    CONTAINS (existing tools, unchanged, wrapped & configured by canvas):    │
│    ├── CanvasUserInputTool         ─→ you.input.*                           │
│    ├── CanvasParserTool            ─→ you.parser.*                          │
│    ├── CanvasFileSystemTool        ─→ you.files.*                           │
│    ├── CanvasPythonInterpreterTool ─→ you.code.*                            │
│    ├── CanvasLLMTool               ─→ you.llm.*                             │
│    ├── CanvasPromptTool            ─→ you.prompt.*                          │
│    ├── CanvasParadigmTool          ─→ you.paradigm.*                        │
│    ├── CanvasModelRunnerTool       ─→ you.model.*                           │
│    ├── CanvasCompositionTool       ─→ you.compose.*                         │
│    ├── CanvasPerceptionRouter      ─→ you.perceive.*                        │
│    └── CanvasFormatterTool         ─→ you.format.*                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Design Principles

1. **Single Entry Point** - One tool for all canvas interaction
2. **Perspective-Based API** - `canvas.me`, `canvas.you`, `canvas.it`
3. **Reuse Existing Tools** - Contained tools are unchanged, just wrapped
4. **Configuration Through Canvas** - Tool reconfiguration happens via canvas interface
5. **Selective Replacement** - Only replace what needs new implementation (Display, Chat)

---

## Interface

```python
from typing import Protocol, Callable, Dict, Any, Optional
from dataclasses import dataclass


class ICanvasIntegrationTool(Protocol):
    """
    The unified canvas integration tool.
    
    Single entry point for all canvas interaction.
    
    Replaces: CanvasDisplayTool, CanvasChatTool (new implementation)
    Contains: CanvasUserInputTool, CanvasParserTool, CanvasFileSystemTool,
              CanvasPythonInterpreterTool (unchanged, wrapped)
    
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
    
    @property
    def me(self) -> 'IFirstPersonPerspective':
        """First Person - shared stage (user sees everything)."""
        ...
    
    @property
    def you(self) -> 'ISecondPersonPerspective':
        """Second Person - private workspace (user sees nothing)."""
        ...
    
    @property
    def it(self) -> 'IThirdPersonPerspective':
        """Third Person - activity observation (meta-level)."""
        ...
    
    # ═══════════════════════════════════════════════════════════════════
    # CONFIGURATION
    # ═══════════════════════════════════════════════════════════════════
    
    def configure(self, **settings) -> None:
        """
        Configure contained tools and settings.
        
        Args:
            llm_model: Default LLM model
            llm_temperature: Default temperature
            file_base_path: Base path for file operations
            python_timeout: Timeout for Python execution
            parser_format: Default parser format
            ...
        """
        ...
    
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration."""
        ...
    
    # ═══════════════════════════════════════════════════════════════════
    # DIRECT ACCESS TO CONTAINED TOOLS (for backward compatibility)
    # ═══════════════════════════════════════════════════════════════════
    
    @property
    def user_input_tool(self) -> 'CanvasUserInputTool':
        """Direct access to user input tool (prefer you.input.*)."""
        ...
    
    @property
    def parser_tool(self) -> 'CanvasParserTool':
        """Direct access to parser tool (prefer you.parser.*)."""
        ...
    
    @property
    def file_tool(self) -> 'CanvasFileSystemTool':
        """Direct access to file tool (prefer you.files.*)."""
        ...
    
    @property
    def python_tool(self) -> 'CanvasPythonInterpreterTool':
        """Direct access to python tool (prefer you.code.*)."""
        ...
    
    @property
    def llm_tool(self) -> 'CanvasLLMTool':
        """Direct access to LLM tool (prefer you.llm.*)."""
        ...
    
    @property
    def prompt_tool(self) -> 'CanvasPromptTool':
        """Direct access to prompt tool (prefer you.prompt.*)."""
        ...
    
    @property
    def paradigm_tool(self) -> 'CanvasParadigmTool':
        """Direct access to paradigm tool (prefer you.paradigm.*)."""
        ...
    
    @property
    def model_runner_tool(self) -> 'CanvasModelRunnerTool':
        """Direct access to model runner tool (prefer you.model.*)."""
        ...
    
    @property
    def composition_tool(self) -> 'CanvasCompositionTool':
        """Direct access to composition tool (prefer you.compose.*)."""
        ...
    
    @property
    def perception_router(self) -> 'CanvasPerceptionRouter':
        """Direct access to perception router (prefer you.perceive.*)."""
        ...
    
    @property
    def formatter_tool(self) -> 'CanvasFormatterTool':
        """Direct access to formatter tool (prefer you.format.*)."""
        ...
    
    @property
    def db(self) -> 'OrchestratorDB':
        """Direct access to database (prefer you.db.*)."""
        ...
```

---

## Internal Structure

```python
from tools.user_input_tool import CanvasUserInputTool
from tools.parser_tool import CanvasParserTool
from tools.file_system_tool import CanvasFileSystemTool
from tools.python_interpreter_tool import CanvasPythonInterpreterTool
from tools.llm_tool import CanvasLLMTool
from tools.prompt_tool import CanvasPromptTool
from tools.paradigm_tool import CanvasParadigmTool
from tools.model_runner_tool import CanvasModelRunnerTool
from tools.composition_tool import CanvasCompositionTool
from tools.perception_router_tool import CanvasPerceptionRouter
from tools.formatter_tool import CanvasFormatterTool
from infra._orchest._db import OrchestratorDB


class CanvasIntegrationTool:
    """
    Implementation of the unified canvas integration tool.
    
    - Creates NEW implementation for First Person (replaces Display + Chat)
    - Wraps EXISTING tools for Second Person
    """
    
    def __init__(
        self,
        # External dependencies
        emit_callback: Callable[[str, Dict], None],
        execution_getter: Optional[Callable[[], Any]] = None,
        
        # Services
        project_service: Optional[Any] = None,
        graph_service: Optional[Any] = None,
        execution_service: Optional[Any] = None,
        parser_service: Optional[Any] = None,
        llm_settings_service: Optional[Any] = None,
        
        # Configuration
        config: Optional[Dict[str, Any]] = None
    ):
        # Store dependencies
        self._emit = emit_callback
        self._execution_getter = execution_getter
        self._services = ServiceContainer(
            project=project_service,
            graph=graph_service,
            execution=execution_service,
            parser=parser_service,
            llm_settings=llm_settings_service
        )
        self._config = config or {}
        
        # ═══════════════════════════════════════════════════════════════
        # CONTAINED TOOLS (existing, unchanged)
        # ═══════════════════════════════════════════════════════════════
        self._user_input_tool = CanvasUserInputTool(emit_callback)
        self._parser_tool = CanvasParserTool(parser_service, emit_callback)
        self._file_tool = CanvasFileSystemTool(emit_callback)
        self._python_tool = CanvasPythonInterpreterTool(emit_callback)
        self._llm_tool = CanvasLLMTool(llm_settings_service, emit_callback)
        self._prompt_tool = CanvasPromptTool(emit_callback)
        self._paradigm_tool = CanvasParadigmTool(emit_callback)
        self._model_runner_tool = CanvasModelRunnerTool(emit_callback)
        self._composition_tool = CanvasCompositionTool(emit_callback)
        self._perception_router = CanvasPerceptionRouter(emit_callback)
        self._formatter_tool = CanvasFormatterTool(emit_callback)
        self._db = OrchestratorDB(config.get('db_path', 'orchestration.db'))
        
        # Create event store for Third Person
        self._event_store = EventStore()
        
        # ═══════════════════════════════════════════════════════════════
        # PERSPECTIVES
        # ═══════════════════════════════════════════════════════════════
        
        # First Person: NEW implementation (replaces CanvasDisplayTool + CanvasChatTool)
        self._me = FirstPersonPerspective(
            emit=emit_callback,
            execution_getter=execution_getter,
            services=self._services,
            event_store=self._event_store
        )
        
        # Second Person: Wraps all tools
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
            execution_getter=execution_getter,
            services=self._services,
            db=self._db
        )
        
        # Third Person: New event observation
        self._it = ThirdPersonPerspective(
            event_store=self._event_store
        )
    
    # ═══════════════════════════════════════════════════════════════════
    # PERSPECTIVE PROPERTIES
    # ═══════════════════════════════════════════════════════════════════
    
    @property
    def me(self) -> 'FirstPersonPerspective':
        return self._me
    
    @property
    def you(self) -> 'SecondPersonPerspective':
        return self._you
    
    @property
    def it(self) -> 'ThirdPersonPerspective':
        return self._it
    
    # ═══════════════════════════════════════════════════════════════════
    # DIRECT TOOL ACCESS (backward compatibility)
    # ═══════════════════════════════════════════════════════════════════
    
    @property
    def user_input_tool(self) -> CanvasUserInputTool:
        return self._user_input_tool
    
    @property
    def parser_tool(self) -> CanvasParserTool:
        return self._parser_tool
    
    @property
    def file_tool(self) -> CanvasFileSystemTool:
        return self._file_tool
    
    @property
    def python_tool(self) -> CanvasPythonInterpreterTool:
        return self._python_tool
    
    @property
    def llm_tool(self) -> CanvasLLMTool:
        return self._llm_tool
    
    @property
    def prompt_tool(self) -> CanvasPromptTool:
        return self._prompt_tool
    
    @property
    def paradigm_tool(self) -> CanvasParadigmTool:
        return self._paradigm_tool
    
    @property
    def model_runner_tool(self) -> CanvasModelRunnerTool:
        return self._model_runner_tool
    
    @property
    def composition_tool(self) -> CanvasCompositionTool:
        return self._composition_tool
    
    @property
    def perception_router(self) -> CanvasPerceptionRouter:
        return self._perception_router
    
    @property
    def formatter_tool(self) -> CanvasFormatterTool:
        return self._formatter_tool
    
    @property
    def db(self) -> OrchestratorDB:
        return self._db
    
    # ═══════════════════════════════════════════════════════════════════
    # CONFIGURATION
    # ═══════════════════════════════════════════════════════════════════
    
    def configure(self, **settings) -> None:
        """Update configuration for contained tools."""
        if 'file_base_path' in settings:
            self._file_tool.set_base_path(settings['file_base_path'])
        if 'python_timeout' in settings:
            self._python_tool.set_timeout(settings['python_timeout'])
        # ... configure other tools as needed
        self._config.update(settings)
    
    def get_config(self) -> Dict[str, Any]:
        return self._config.copy()
```

---

## Contained Tools (Existing, Unchanged)

These are the **existing** tools that are wrapped by `CanvasIntegrationTool`.
They are NOT rewritten - just provided and configured through canvas.

| Tool | Accessed Via | Notes |
|------|--------------|-------|
| `CanvasUserInputTool` | `you.input.*` | Blocking user input |
| `CanvasParserTool` | `you.parser.*` | NormCode parsing |
| `CanvasFileSystemTool` | `you.files.*` | File operations |
| `CanvasPythonInterpreterTool` | `you.code.*` | Python execution |
| `CanvasLLMTool` | `you.llm.*` | LLM calls |
| `CanvasPromptTool` | `you.prompt.*` | Prompt templates |
| `CanvasParadigmTool` | `you.paradigm.*` | Paradigm loading |
| `CanvasModelRunnerTool` | `you.model.*` | Model/sequence execution |
| `CanvasCompositionTool` | `you.compose.*` | Function composition |
| `CanvasPerceptionRouter` | `you.perceive.*` | Perception routing |
| `CanvasFormatterTool` | `you.format.*` | Data formatting |

These tools can theoretically work elsewhere (outside canvas), but when used through 
`CanvasIntegrationTool`, they are configured by canvas settings.

---

## Perspective Implementations

### FirstPersonPerspective (NEW - replaces CanvasDisplayTool + CanvasChatTool)

```python
class FirstPersonPerspective:
    """
    "I am the user" - shared stage.
    
    NEW IMPLEMENTATION that replaces:
    - CanvasDisplayTool (display_source, highlight, query_*, execute_command, etc.)
    - CanvasChatTool (write_message for display purposes)
    
    Note: User input (blocking requests) is accessed via Second Person (you.input.*),
    not First Person, because it's a direct tool call rather than UI navigation.
    """
    
    def __init__(
        self,
        emit: Callable,
        execution_getter: Callable,
        services: ServiceContainer,
        event_store: EventStore
    ):
        self._emit = emit
        self._execution_getter = execution_getter
        self._services = services
        self._event_store = event_store
        
        self._vision = Vision(emit, execution_getter, services)
        self._hands = Hands(emit, execution_getter, services, event_store)
        self._mind = Mind(emit, execution_getter, services)
    
    @property
    def vision(self) -> 'Vision':
        return self._vision
    
    @property
    def hands(self) -> 'Hands':
        return self._hands
    
    @property
    def mind(self) -> 'Mind':
        return self._mind
    
    # Shortcuts
    def look(self) -> 'UserViewSnapshot':
        return self._vision.get_full_snapshot()
    
    def click(self, target: str) -> 'ActionResult':
        return self._hands.click_node(target)
    
    def say(self, message: str) -> 'ActionResult':
        return self._hands.say(message)
```

### SecondPersonPerspective (Wraps All Tools)

```python
class SecondPersonPerspective:
    """
    "You are my helper" - private workspace / direct tool access.
    
    WRAPS ALL CANVAS TOOLS - does not reimplement them.
    Facades provide a cleaner API but delegate to actual tools.
    """
    
    def __init__(
        self,
        # All canvas tools
        file_tool: CanvasFileSystemTool,
        python_tool: CanvasPythonInterpreterTool,
        parser_tool: CanvasParserTool,
        llm_tool: CanvasLLMTool,
        prompt_tool: CanvasPromptTool,
        paradigm_tool: CanvasParadigmTool,
        model_runner_tool: CanvasModelRunnerTool,
        composition_tool: CanvasCompositionTool,
        perception_router: CanvasPerceptionRouter,
        formatter_tool: CanvasFormatterTool,
        user_input_tool: CanvasUserInputTool,
        # Services
        execution_getter: Callable,
        services: ServiceContainer,
        db: OrchestratorDB
    ):
        # Data access facades
        self._files = FilesFacade(file_tool)
        self._parser = ParserFacade(parser_tool)
        self._blackboard = BlackboardFacade(execution_getter)
        self._graph = GraphFacade(services.graph)
        self._db = DatabaseFacade(db)
        
        # Execution facades
        self._code = CodeFacade(python_tool)
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
        self._history = HistoryFacade(execution_getter)
    
    # Data access
    @property
    def files(self) -> 'FilesFacade': return self._files
    @property
    def parser(self) -> 'ParserFacade': return self._parser
    @property
    def blackboard(self) -> 'BlackboardFacade': return self._blackboard
    @property
    def graph(self) -> 'GraphFacade': return self._graph
    @property
    def db(self) -> 'DatabaseFacade': return self._db
    
    # Execution
    @property
    def code(self) -> 'CodeFacade': return self._code
    @property
    def llm(self) -> 'LLMFacade': return self._llm
    @property
    def prompt(self) -> 'PromptFacade': return self._prompt
    
    # Paradigm/model
    @property
    def paradigm(self) -> 'ParadigmFacade': return self._paradigm
    @property
    def model(self) -> 'ModelFacade': return self._model
    @property
    def compose(self) -> 'ComposeFacade': return self._compose
    @property
    def perceive(self) -> 'PerceiveFacade': return self._perceive
    @property
    def format(self) -> 'FormatFacade': return self._format
    
    # Interaction
    @property
    def input(self) -> 'InputFacade': return self._input
    
    # System
    @property
    def system(self) -> 'SystemFacade': return self._system
    @property
    def history(self) -> 'HistoryFacade': return self._history
```

### ThirdPersonPerspective (New)

```python
class ThirdPersonPerspective:
    """
    "What is happening" - activity observation.
    
    NEW implementation for observing system events and activity patterns.
    """
    
    def __init__(self, event_store: EventStore):
        self._event_store = event_store
        self._events = EventsFacade(event_store)
        self._activity = ActivityFacade(event_store)
    
    @property
    def events(self) -> 'EventsFacade':
        return self._events
    
    @property
    def activity(self) -> 'ActivityFacade':
        return self._activity
```

---

## Facades (Thin Wrappers)

Facades provide a cleaner API but delegate to existing tools.

### FilesFacade

```python
class FilesFacade:
    """
    Thin wrapper around CanvasFileSystemTool.
    Provides cleaner API but delegates all work to existing tool.
    """
    
    def __init__(self, tool: CanvasFileSystemTool):
        self._tool = tool
    
    def read(self, path: str) -> str:
        return self._tool.read_file(path)
    
    def write(self, path: str, content: str) -> str:
        return self._tool.write_file(path, content)
    
    def read_json(self, path: str) -> Any:
        return self._tool.read_json(path)
    
    def write_json(self, path: str, data: Any) -> str:
        return self._tool.write_json(path, data)
    
    def list_dir(self, path: str = ".") -> List[str]:
        return self._tool.list_directory(path)
    
    def exists(self, path: str) -> bool:
        return self._tool.exists(path)
    
    def delete(self, path: str) -> str:
        return self._tool.delete(path)
```

### CodeFacade

```python
class CodeFacade:
    """
    Thin wrapper around CanvasPythonInterpreterTool.
    """
    
    def __init__(self, tool: CanvasPythonInterpreterTool):
        self._tool = tool
    
    def run(self, code: str, inputs: Dict[str, Any] = None) -> Any:
        return self._tool.execute(code, inputs)
    
    def run_function(self, code: str, function_name: str, params: Dict = None) -> Any:
        return self._tool.execute_function(code, function_name, params)
```

### ParserFacade

```python
class ParserFacade:
    """
    Thin wrapper around CanvasParserTool.
    """
    
    def __init__(self, tool: CanvasParserTool):
        self._tool = tool
    
    def parse(self, content: str, format: str = "ncdn") -> Dict:
        if format == "ncdn":
            return self._tool.parse_ncdn(content)
        return self._tool.parse_ncd(content)
    
    def serialize(self, data: Dict, format: str = "ncdn") -> str:
        if format == "ncdn":
            return self._tool.serialize_to_ncdn(data)
        return self._tool.serialize_to_ncd_ncn(data)
    
    def convert(self, content: str, from_fmt: str, to_fmt: str) -> str:
        return self._tool.convert_format(content, from_fmt, to_fmt)
    
    def validate(self, content: str, format: str = "ncdn") -> Dict:
        return self._tool.validate(content, format)
```

---

## Event Store (New)

```python
from collections import deque
from datetime import datetime
from typing import Iterator, Dict, List
import threading


class EventStore:
    """
    Event store for Third Person observation.
    
    Captures events emitted by the tool for later analysis.
    """
    
    def __init__(self, max_events: int = 10000):
        self._events: deque = deque(maxlen=max_events)
        self._lock = threading.Lock()
        self._subscribers: List[Callable] = []
    
    def record(self, event_type: str, data: Dict) -> None:
        """Record an event (called by emit wrapper)."""
        event = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        with self._lock:
            self._events.append(event)
        
        for subscriber in self._subscribers:
            subscriber(event)
    
    def recent(self, limit: int = 100) -> List[Dict]:
        with self._lock:
            return list(self._events)[-limit:]
    
    def by_type(self, event_type: str, limit: int = 100) -> List[Dict]:
        with self._lock:
            matching = [e for e in self._events if e["type"] == event_type]
            return matching[-limit:]
    
    def stream(self, filter: Dict = None) -> Iterator[Dict]:
        queue = []
        
        def on_event(event):
            if filter is None or self._matches_filter(event, filter):
                queue.append(event)
        
        self._subscribers.append(on_event)
        try:
            while True:
                if queue:
                    yield queue.pop(0)
                else:
                    import time
                    time.sleep(0.01)
        finally:
            self._subscribers.remove(on_event)
```

---

## Injection

### Before (Multiple Tools)

```python
def inject_canvas_tools(body, emit_callback, execution_getter):
    body.tools.canvas = CanvasDisplayTool(emit_callback, execution_getter)
    body.tools.chat = CanvasChatTool(emit_callback)
    body.tools.user_input = CanvasUserInputTool(emit_callback)
    body.tools.parser = CanvasParserTool(parser_service)
    body.tools.files = CanvasFileSystemTool(emit_callback)
    body.tools.python = CanvasPythonInterpreterTool(emit_callback)
    # ... plus many more individual tools
```

### After (Single Tool)

```python
def inject_canvas_integration(
    body,
    emit_callback: Callable,
    execution_getter: Callable = None,
    services: Dict = None,
    config: Dict = None
) -> CanvasIntegrationTool:
    """
    Inject the unified canvas integration tool.
    """
    canvas = CanvasIntegrationTool(
        emit_callback=emit_callback,
        execution_getter=execution_getter,
        project_service=services.get('project'),
        graph_service=services.get('graph'),
        execution_service=services.get('execution'),
        parser_service=services.get('parser'),
        llm_settings_service=services.get('llm_settings'),
        config=config
    )
    
    # Single injection point
    body.canvas = canvas
    
    # Backward compatibility: also expose contained tools directly
    body.tools.user_input = canvas.user_input_tool
    body.tools.parser = canvas.parser_tool
    body.tools.files = canvas.file_tool
    body.tools.python = canvas.python_tool
    body.tools.llm = canvas.llm_tool
    body.tools.prompt = canvas.prompt_tool
    body.tools.paradigm = canvas.paradigm_tool
    body.tools.model_runner = canvas.model_runner_tool
    body.tools.composition = canvas.composition_tool
    body.tools.perception = canvas.perception_router
    body.tools.formatter = canvas.formatter_tool
    
    return canvas
```

---

## Usage Examples

### Example 1: Basic Interaction

```python
canvas = body.canvas

# Look at the app
snapshot = canvas.me.look()
print(snapshot.to_text())

# Click a node
canvas.me.click("1.3")

# Say something
canvas.me.say("I'm analyzing node 1.3")
```

### Example 2: Private Investigation

```python
canvas = body.canvas

# Show status (TEMPORARY - auto-dismisses, not in chat history)
canvas.me.hands.notify("🔍 Analyzing project...", "thinking")

# Gather data privately (user sees nothing)
config = canvas.you.files.read("project.json")
value = canvas.you.blackboard.get("ResultConcept")
trace = canvas.you.history.get_trace("1.3")

# Update status
canvas.me.hands.status("executing")  # Shows "⚙️ Executing command..."

# Analyze
issues = []
if value is None:
    issues.append("ResultConcept has no value")

# Show findings (PERMANENT - stays in chat history)
canvas.me.say(f"Investigation complete. Found {len(issues)} issues.")
```

### Example 3: Using All Second Person Tools

```python
canvas = body.canvas

# Data access
config = canvas.you.files.read("config.json")
value = canvas.you.blackboard.get("X")
runs = canvas.you.db.get_runs()

# Execution  
analysis = canvas.you.llm.call("Analyze: " + config)
code_result = canvas.you.code.run("return x + 1", {"x": 5})

# Model/paradigm
paradigm = canvas.you.paradigm.load("my_paradigm")
result = canvas.you.model.run_sequence(states, spec)

# User input (direct tool call)
answer = canvas.you.input.request("What should I do?")
choice = canvas.you.input.request_choice("Pick one:", ["A", "B", "C"])

# Show results (First Person)
canvas.me.say(f"Analysis: {analysis}")
```

### Example 4: Direct Tool Access (Backward Compatibility)

```python
canvas = body.canvas

# Preferred: through perspectives
content = canvas.you.files.read("config.json")

# Also available: direct tool access
content = canvas.file_tool.read_file("config.json")

# Or through body.tools (if exposed)
content = body.tools.files.read_file("config.json")
```

---

## Migration Guide

### What Changes

| Old | New | Status |
|-----|-----|--------|
| `CanvasDisplayTool` | `canvas.me.vision.*`, `canvas.me.hands.*`, `canvas.me.mind.*` | **REPLACED** (new impl) |
| `CanvasChatTool` | `canvas.me.say()`, `canvas.me.hands.*` | **REPLACED** (new impl) |
| `CanvasUserInputTool` | `canvas.you.input.*` or `canvas.user_input_tool` | **KEPT** (wrapped) |
| `CanvasParserTool` | `canvas.you.parser.*` or `canvas.parser_tool` | **KEPT** (wrapped) |
| `CanvasFileSystemTool` | `canvas.you.files.*` or `canvas.file_tool` | **KEPT** (wrapped) |
| `CanvasPythonInterpreterTool` | `canvas.you.code.*` or `canvas.python_tool` | **KEPT** (wrapped) |
| `CanvasLLMTool` | `canvas.you.llm.*` or `canvas.llm_tool` | **KEPT** (wrapped) |
| `CanvasPromptTool` | `canvas.you.prompt.*` or `canvas.prompt_tool` | **KEPT** (wrapped) |
| `CanvasParadigmTool` | `canvas.you.paradigm.*` or `canvas.paradigm_tool` | **KEPT** (wrapped) |
| `CanvasModelRunnerTool` | `canvas.you.model.*` or `canvas.model_runner_tool` | **KEPT** (wrapped) |
| `CanvasCompositionTool` | `canvas.you.compose.*` or `canvas.composition_tool` | **KEPT** (wrapped) |
| `CanvasPerceptionRouter` | `canvas.you.perceive.*` or `canvas.perception_router` | **KEPT** (wrapped) |
| `CanvasFormatterTool` | `canvas.you.format.*` or `canvas.formatter_tool` | **KEPT** (wrapped) |

### Migration Examples

```python
# OLD: CanvasDisplayTool
canvas.display_source(code)          → canvas.me.hands.show_source(code)
canvas.query_project()               → canvas.me.vision.get_project()
canvas.execute_command("run")        → canvas.me.mind.run()
canvas.highlight("1.3")              → canvas.me.hands.highlight_node("1.3")

# OLD: CanvasChatTool
chat.write_message(msg)              → canvas.me.say(msg)           # Permanent message
chat.read_input(prompt)              → canvas.you.input.request(prompt)

# NEW: Temporary notifications (2026-01-26)
# Use notify() for ephemeral status updates that don't clutter chat history
canvas.me.hands.notify("🔍 Thinking...")      # Temporary, auto-dismisses
canvas.me.hands.status("executing")           # Convenience method with defaults
canvas.me.hands.say("Here is the result!")    # Permanent, stays in history

# OLD: CanvasParserTool (unchanged, just new access path)
parser.parse_ncdn(content)           → canvas.you.parser.parse(content)
                                     OR canvas.parser_tool.parse_ncdn(content)

# OLD: CanvasFileSystemTool (unchanged, just new access path)
files.read_file(path)                → canvas.you.files.read(path)
                                     OR canvas.file_tool.read_file(path)

# OLD: CanvasPythonInterpreterTool (unchanged, just new access path)
python.execute(code)                 → canvas.you.code.run(code)
                                     OR canvas.python_tool.execute(code)
```

---

## File Structure

```
canvas_app/backend/
├── canvas_integration/
│   ├── __init__.py
│   ├── tool.py                    # CanvasIntegrationTool
│   ├── perspectives/
│   │   ├── __init__.py
│   │   ├── first_person.py        # FirstPersonPerspective (NEW)
│   │   ├── second_person.py       # SecondPersonPerspective (wraps existing)
│   │   └── third_person.py        # ThirdPersonPerspective (NEW)
│   ├── faculties/
│   │   ├── __init__.py
│   │   ├── vision.py              # Vision faculty (NEW)
│   │   ├── hands.py               # Hands faculty (NEW)
│   │   └── mind.py                # Mind faculty (NEW)
│   ├── facades/
│   │   ├── __init__.py
│   │   ├── files.py               # FilesFacade (wraps existing tool)
│   │   ├── code.py                # CodeFacade (wraps existing tool)
│   │   ├── parser.py              # ParserFacade (wraps existing tool)
│   │   ├── blackboard.py          # BlackboardFacade
│   │   ├── graph.py               # GraphFacade
│   │   ├── system.py              # SystemFacade
│   │   ├── history.py             # HistoryFacade
│   │   ├── events.py              # EventsFacade (NEW)
│   │   └── activity.py            # ActivityFacade (NEW)
│   ├── event_store.py             # EventStore (NEW)
│   ├── types.py                   # Data types, snapshots, results
│   └── injection.py               # inject_canvas_integration()
│
├── tools/                         # EXISTING TOOLS (kept, not deprecated)
│   ├── canvas_tool.py             # CanvasDisplayTool (kept for backward compat)
│   ├── chat_tool.py               # CanvasChatTool (kept for backward compat)
│   ├── user_input_tool.py         # CanvasUserInputTool (USED by canvas integration)
│   ├── parser_tool.py             # CanvasParserTool (USED by canvas integration)
│   ├── file_system_tool.py        # CanvasFileSystemTool (USED by canvas integration)
│   └── python_interpreter_tool.py # CanvasPythonInterpreterTool (USED by canvas integration)
```

---

## Summary

| Aspect | Value |
|--------|-------|
| **Entry Point** | Single: `CanvasIntegrationTool` |
| **API** | `canvas.me` / `canvas.you` / `canvas.it` |
| **Replaces** | `CanvasDisplayTool`, `CanvasChatTool` (new implementation) |
| **Contains** | 11 tools (UserInput, Parser, FileSystem, Python, LLM, Prompt, Paradigm, ModelRunner, Composition, Perception, Formatter) + Database |
| **Configuration** | Via `canvas.configure(...)` |
| **Backward Compat** | Direct tool access via `canvas.*_tool` properties |

### Chat Message Types (2026-01-26)

| Method | Persists? | Use For | WebSocket Event |
|--------|-----------|---------|-----------------|
| `canvas.me.hands.say(msg)` | ✅ Yes | Actual responses | `chat:message` |
| `canvas.me.hands.notify(msg, type)` | ❌ No | Status updates | `chat:notification` |
| `canvas.me.hands.status(type)` | ❌ No | Common statuses | `chat:status` |

Status types: `"thinking"`, `"executing"`, `"generating"`, `"success"`, `"error"`, `"info"`, `"warning"`

---

## Related Documents

- `CANVAS_INTEGRATION_INTERFACE.md` - Overall interface design
- `First_person_perspective.md` - Detailed First Person interface
- `Second_person_perspective.md` - Detailed Second Person interface
- `Third_person_perspective.md` - Detailed Third Person interface

---
