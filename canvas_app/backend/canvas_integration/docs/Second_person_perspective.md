# Second Person Perspective Interface

AI's **private workspace** for direct backend/tool access - runs in parallel, doesn't interfere with what the user sees.

---

## Philosophy

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         SHARED REALITY (Frontend)                       │
│                                                                         │
│   Canvas: [nodes] [edges] [status]    Chat: [messages]                 │
│                                                                         │
└───────────────────────────────────┬─────────────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
                    ▼                               ▼
        ┌───────────────────────┐       ┌───────────────────────┐
        │   "I" (First Person)  │       │  "You" (Second Person)│
        │                       │       │                       │
        │   SHARED STAGE        │       │   PRIVATE WORKSPACE   │
        │   User sees effects   │       │   User sees nothing   │
        │   Changes UI state    │       │   Direct tool access  │
        │                       │       │                       │
        │   me.say("hello") →   │       │   you.files.read() →  │
        │   shows in chat       │       │   returns content     │
        └───────────────────────┘       └───────────────────────┘
```

| | First Person (`me`) | Second Person (`you`) |
|--|---------------------|----------------------|
| **Visibility** | User sees | User doesn't see |
| **State** | Changes shared/UI state | Direct backend/tool access |
| **Purpose** | Act as user on stage | AI's private tool usage |
| **Analogy** | On stage | Backstage |

---

## Why Second Person?

**Problem**: Some operations are tedious through First Person UI navigation, or don't need UI visibility.

| Without "You" (tedious) | With "You" (shortcut) |
|-------------------------|----------------------|
| Open editor → navigate → click file → read | `you.files.read("path")` |
| Click node → open inspector → find value | `you.blackboard.get("X")` |
| Open parser panel → paste → click parse | `you.parser.parse(source)` |
| Find terminal → type → execute → read | `you.code.run(script)` |
| Call LLM and wait for response | `you.llm.call(prompt)` |
| Request user input programmatically | `you.input.request("question")` |

**"You" is direct tool access. Results can flow through "I" for display:**

```python
# Private: Use tools directly (user sees nothing)
content = you.files.read("config.json")
analysis = you.llm.call(f"Analyze this config:\n{content}")

# Public: Show to user (now they see)
me.say(f"Analysis:\n{analysis}")
```

---

## Interface Definition

```python
from typing import Protocol, List, Dict, Any, Optional


class ISecondPersonPerspective(Protocol):
    """
    "You" - AI's private workspace / direct tool access.
    
    All canvas tools are accessible here for direct invocation.
    Does NOT affect shared UI state or what user sees.
    """
    
    # ═══════════════════════════════════════════════════════════════════
    # DATA ACCESS TOOLS
    # ═══════════════════════════════════════════════════════════════════
    
    @property
    def files(self) -> 'IFiles': 
        """File system operations."""
        ...
    
    @property
    def blackboard(self) -> 'IBlackboard': 
        """Computed concept values."""
        ...
    
    @property
    def parser(self) -> 'IParser': 
        """NormCode parsing."""
        ...
    
    @property
    def graph(self) -> 'IGraph': 
        """Graph structure queries."""
        ...
    
    @property
    def db(self) -> 'IDatabase': 
        """Direct database queries (orchestration.db)."""
        ...
    
    # ═══════════════════════════════════════════════════════════════════
    # EXECUTION TOOLS
    # ═══════════════════════════════════════════════════════════════════
    
    @property
    def code(self) -> 'ICode': 
        """Python execution."""
        ...
    
    @property
    def llm(self) -> 'ILLM': 
        """Language model calls."""
        ...
    
    @property
    def prompt(self) -> 'IPrompt': 
        """Prompt template operations."""
        ...
    
    # ═══════════════════════════════════════════════════════════════════
    # PARADIGM/MODEL EXECUTION TOOLS
    # ═══════════════════════════════════════════════════════════════════
    
    @property
    def paradigm(self) -> 'IParadigm': 
        """Paradigm loading."""
        ...
    
    @property
    def model(self) -> 'IModel': 
        """Model/sequence execution."""
        ...
    
    @property
    def compose(self) -> 'ICompose': 
        """Function composition."""
        ...
    
    @property
    def perceive(self) -> 'IPerceive': 
        """Perception routing."""
        ...
    
    @property
    def format(self) -> 'IFormat': 
        """Data formatting."""
        ...
    
    # ═══════════════════════════════════════════════════════════════════
    # INTERACTION TOOLS
    # ═══════════════════════════════════════════════════════════════════
    
    @property
    def input(self) -> 'IInput': 
        """User input requests (blocking)."""
        ...
    
    # ═══════════════════════════════════════════════════════════════════
    # SYSTEM INTROSPECTION
    # ═══════════════════════════════════════════════════════════════════
    
    @property
    def system(self) -> 'ISystem': 
        """System state queries."""
        ...
    
    @property
    def history(self) -> 'IHistory': 
        """Historical data queries."""
        ...
```

---

## Data Access Tools

### `you.files` - File Access

```python
class IFiles(Protocol):
    """
    Direct file operations.
    Wraps: CanvasFileSystemTool
    """
    
    def read(self, path: str) -> str:
        """Read file content."""
        ...
    
    def write(self, path: str, content: str) -> str:
        """Write content to file."""
        ...
    
    def read_json(self, path: str) -> Any:
        """Read and parse JSON file."""
        ...
    
    def write_json(self, path: str, data: Any) -> str:
        """Write data as JSON."""
        ...
    
    def list_dir(self, path: str = ".") -> List[str]:
        """List directory contents."""
        ...
    
    def exists(self, path: str) -> bool:
        """Check if path exists."""
        ...
    
    def delete(self, path: str) -> str:
        """Delete file or directory."""
        ...
```

### `you.blackboard` - Concept Values

```python
class IBlackboard(Protocol):
    """
    Direct access to computed values.
    Wraps: ExecutionController
    """
    
    def get(self, concept_name: str) -> Any:
        """Get computed value of a concept."""
        ...
    
    def get_all(self) -> Dict[str, Any]:
        """Get all computed values."""
        ...
    
    def get_status(self, concept_name: str) -> str:
        """Get status: 'pending', 'computed', 'failed', etc."""
        ...
    
    def list_concepts(self) -> List[str]:
        """List all concept names."""
        ...
    
    def get_logs(self, limit: int = 100) -> List[Dict]:
        """Get execution logs."""
        ...
```

### `you.parser` - NormCode Parsing

```python
class IParser(Protocol):
    """
    Direct parsing operations.
    Wraps: CanvasParserTool
    """
    
    def parse(self, content: str, format: str = "ncdn") -> Dict:
        """Parse NormCode to structured JSON."""
        ...
    
    def serialize(self, data: Dict, format: str = "ncdn") -> str:
        """Serialize to NormCode format."""
        ...
    
    def convert(self, content: str, from_fmt: str, to_fmt: str) -> str:
        """Convert between formats."""
        ...
    
    def validate(self, content: str, format: str = "ncdn") -> Dict:
        """Validate NormCode content."""
        ...
```

### `you.graph` - Graph Queries

```python
class IGraph(Protocol):
    """
    Direct graph queries.
    Wraps: GraphService
    """
    
    def get_nodes(self) -> List[Dict]:
        """Get all nodes."""
        ...
    
    def get_edges(self) -> List[Dict]:
        """Get all edges."""
        ...
    
    def get_node(self, node_id: str) -> Dict:
        """Get node by ID."""
        ...
    
    def get_node_by_flow_index(self, flow_index: str) -> Dict:
        """Get node by flow index."""
        ...
    
    def get_children(self, node_id: str) -> List[str]:
        """Get child node IDs."""
        ...
    
    def get_parents(self, node_id: str) -> List[str]:
        """Get parent node IDs."""
        ...
```

### `you.db` - Database Queries

```python
class IDatabase(Protocol):
    """
    Direct database queries for orchestration.db.
    Wraps: OrchestratorDB (infra/_orchest/_db.py)
    
    Tables available:
    - executions: execution records (run_id, cycle, flow_index, status, etc.)
    - logs: detailed execution logs
    - checkpoints: state snapshots (run_id, cycle, inference_count, state_json)
    - run_metadata: run configuration and environment
    """
    
    def query(self, sql: str, params: tuple = ()) -> List[Dict]:
        """Execute raw SQL query (SELECT only for safety)."""
        ...
    
    def get_runs(self) -> List[Dict]:
        """List all runs in the database."""
        ...
    
    def get_run_metadata(self, run_id: str) -> Dict:
        """Get metadata for a specific run."""
        ...
    
    def get_executions(
        self, 
        run_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """Get execution records, optionally filtered by run_id."""
        ...
    
    def get_execution_logs(self, execution_id: int) -> List[str]:
        """Get logs for a specific execution."""
        ...
    
    def get_checkpoints(
        self, 
        run_id: Optional[str] = None,
        cycle: Optional[int] = None
    ) -> List[Dict]:
        """Get checkpoints, optionally filtered."""
        ...
    
    def get_checkpoint_state(
        self, 
        run_id: str, 
        cycle: int, 
        inference_count: int = 0
    ) -> Dict:
        """Get full state from a specific checkpoint."""
        ...
    
    def get_tables(self) -> List[str]:
        """List all tables in the database."""
        ...
    
    def get_table_schema(self, table_name: str) -> List[Dict]:
        """Get schema (columns) for a table."""
        ...
    
    def get_table_count(self, table_name: str) -> int:
        """Get row count for a table."""
        ...
```

---

## Execution Tools

### `you.code` - Python Execution

```python
class ICode(Protocol):
    """
    Direct Python execution.
    Wraps: CanvasPythonInterpreterTool
    """
    
    def run(self, code: str, inputs: Dict[str, Any] = None) -> Any:
        """Execute Python code, return result."""
        ...
    
    def run_function(
        self, 
        code: str, 
        function_name: str, 
        params: Dict[str, Any] = None
    ) -> Any:
        """Execute a specific function."""
        ...
```

### `you.llm` - Language Model

```python
class ILLM(Protocol):
    """
    Direct LLM calls.
    Wraps: CanvasLLMTool
    """
    
    def call(
        self, 
        prompt: str, 
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """Call LLM with prompt, return response."""
        ...
    
    def call_with_messages(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None
    ) -> str:
        """Call LLM with message list."""
        ...
    
    def get_available_models(self) -> List[str]:
        """List available LLM models."""
        ...
```

### `you.prompt` - Prompt Templates

```python
class IPrompt(Protocol):
    """
    Prompt template operations.
    Wraps: CanvasPromptTool
    """
    
    def read(self, path: str) -> str:
        """Read prompt template from file."""
        ...
    
    def substitute(self, template: str, **kwargs) -> str:
        """Substitute variables in template."""
        ...
    
    def load_and_substitute(self, path: str, **kwargs) -> str:
        """Load template and substitute variables."""
        ...
```

---

## Paradigm/Model Execution Tools

### `you.paradigm` - Paradigm Loading

```python
class IParadigm(Protocol):
    """
    Paradigm loading and management.
    Wraps: CanvasParadigmTool
    """
    
    def load(self, paradigm_name: str) -> Any:
        """Load a paradigm by name."""
        ...
    
    def list_paradigms(self) -> List[str]:
        """List available paradigm names."""
        ...
    
    def list_manifest(self) -> str:
        """Get paradigm manifest with descriptions."""
        ...
```

### `you.model` - Model/Sequence Execution

```python
class IModel(Protocol):
    """
    Model environment and sequence execution.
    Wraps: CanvasModelRunnerTool
    """
    
    def create_env(self, states: Any, spec: Any) -> Any:
        """Create a model environment for executing affordances."""
        ...
    
    def run_sequence(self, states: Any, sequence_spec: Any) -> Dict[str, Any]:
        """Execute a sequence and return results."""
        ...
    
    def execute_affordance(
        self, 
        env: Any, 
        affordance: str, 
        params: Dict[str, Any] = None
    ) -> Any:
        """Execute a single affordance."""
        ...
```

### `you.compose` - Function Composition

```python
class ICompose(Protocol):
    """
    Function composition for paradigm execution.
    Wraps: CanvasCompositionTool
    """
    
    def compose(
        self, 
        plan: List[Dict[str, Any]], 
        return_key: Optional[str] = None
    ) -> Callable:
        """Create composed function from execution plan."""
        ...
    
    def execute_plan(
        self, 
        plan: List[Dict[str, Any]], 
        initial_input: Dict[str, Any]
    ) -> Any:
        """Execute plan directly with input."""
        ...
```

### `you.perceive` - Perception Routing

```python
class IPerceive(Protocol):
    """
    Perception routing and transformation.
    Wraps: CanvasPerceptionRouter
    """
    
    def encode_sign(self, content: Any, norm: Optional[str] = None) -> str:
        """Create a perceptual sign from content."""
        ...
    
    def decode_sign(self, token: str) -> Optional[Dict]:
        """Decode a perceptual sign."""
        ...
    
    def perceive(self, token: Any, body: Any) -> Any:
        """Apply perception to transform token using body faculties."""
        ...
    
    def transform(self, token: Any, config: Dict, body: Any) -> Any:
        """Apply transformation based on config."""
        ...
```

### `you.format` - Data Formatting

```python
class IFormat(Protocol):
    """
    Data formatting and parsing.
    Wraps: CanvasFormatterTool
    """
    
    def format(self, data: Any, format_type: str) -> str:
        """Format data to string representation."""
        ...
    
    def parse(self, content: str, format_type: str) -> Any:
        """Parse string to data structure."""
        ...
```

---

## Interaction Tools

### `you.input` - User Input

```python
class IInput(Protocol):
    """
    Direct user input requests.
    Wraps: CanvasUserInputTool
    
    Note: This DOES interact with user (shows input dialog),
    but the request itself is a direct tool call, not UI navigation.
    """
    
    def request(
        self, 
        prompt: str, 
        input_type: str = "text",
        default: Optional[str] = None,
        timeout: Optional[float] = None
    ) -> str:
        """Request input from user (blocking)."""
        ...
    
    def request_choice(
        self, 
        prompt: str, 
        choices: List[str],
        default: Optional[str] = None
    ) -> str:
        """Request choice from user."""
        ...
    
    def request_confirmation(
        self, 
        prompt: str, 
        default: bool = False
    ) -> bool:
        """Request yes/no confirmation."""
        ...
```

---

## System Introspection

### `you.system` - System State

```python
class ISystem(Protocol):
    """
    System-level state queries.
    Wraps: Workers, connections, tool registry
    
    Note: For OBSERVING activity/events, use Third Person (it.*)
    """
    
    def get_workers(self) -> List[Dict]:
        """Get active orchestrator workers."""
        ...
    
    def get_connections(self) -> List[Dict]:
        """Get active WebSocket connections."""
        ...
    
    def get_tool_calls(self, limit: int = 100) -> List[Dict]:
        """Get record of tool invocations."""
        ...
    
    def get_registered_tools(self) -> List[str]:
        """Get list of registered tool types."""
        ...
```

### `you.history` - Historical Data

```python
class IHistory(Protocol):
    """
    Historical data queries.
    Wraps: Execution logs, state snapshots
    
    Note: For OBSERVING activity patterns/timelines, use Third Person (it.*)
    """
    
    def get_trace(self, flow_index: str) -> Dict:
        """Full execution trace for a node."""
        ...
    
    def get_state_at_cycle(self, cycle: int) -> Dict:
        """Snapshot of blackboard at a specific cycle."""
        ...
```

---

## Usage Examples

```python
class CanvasAI:
    me: IFirstPersonPerspective   # Shared stage (user sees)
    you: ISecondPersonPerspective  # Private workspace (direct tools)
    
    
    def investigate_error(self):
        """AI uses tools privately, then shows relevant info."""
        
        # PRIVATE: Gather information using tools directly
        logs = you.blackboard.get_logs(limit=50)
        errors = [l for l in logs if l['level'] == 'error']
        
        all_values = you.blackboard.get_all()
        failed = [k for k, v in all_values.items() if v is None]
        
        # PUBLIC: Show findings
        me.say(f"Found {len(errors)} errors, {len(failed)} failed concepts")
        if errors:
            me.hands.center_on_node(errors[0]['flow_index'])
    
    
    def analyze_with_llm(self, file_path: str):
        """Use LLM directly to analyze file."""
        
        # PRIVATE: Read and analyze using tools
        content = you.files.read(file_path)
        analysis = you.llm.call(f"Analyze this code:\n```\n{content}\n```")
        
        # PUBLIC: Show analysis
        me.say(f"Analysis of {file_path}:\n{analysis}")
    
    
    def execute_paradigm(self, paradigm_name: str, input_data: Dict):
        """Execute a paradigm directly."""
        
        # PRIVATE: Load and execute paradigm
        paradigm = you.paradigm.load(paradigm_name)
        result = you.model.run_sequence(states, paradigm.sequence_spec)
        
        # PUBLIC: Show result
        me.say(f"Paradigm '{paradigm_name}' completed")
        me.say(f"Result: {result}")
    
    
    def interactive_debug(self, node_id: str):
        """Use input tool to get user clarification."""
        
        # Get node info
        node = you.graph.get_node(node_id)
        value = you.blackboard.get(node['concept_name'])
        
        # Show what we know
        me.say(f"Node: {node['label']}, Value: {value}")
        
        # Ask user for input (shows dialog, but tool call is direct)
        action = you.input.request_choice(
            "What should I do?",
            choices=["Recompute", "Edit value", "Skip", "Cancel"]
        )
        
        # Take action based on response
        if action == "Recompute":
            me.mind.run_from(node_id)
        elif action == "Edit value":
            new_value = you.input.request("Enter new value:")
            me.hands.set_override(node_id, new_value)
    
    
    def investigate_database(self, run_id: Optional[str] = None):
        """Investigate execution history in the database."""
        
        # PRIVATE: Query database directly
        runs = you.db.get_runs()
        me.say(f"Found {len(runs)} runs in database")
        
        if run_id:
            # Get specific run details
            metadata = you.db.get_run_metadata(run_id)
            executions = you.db.get_executions(run_id=run_id, limit=20)
            checkpoints = you.db.get_checkpoints(run_id=run_id)
            
            me.say(f"Run {run_id}:")
            me.say(f"  - {len(executions)} executions")
            me.say(f"  - {len(checkpoints)} checkpoints")
            
            # Find failed executions
            failed = [e for e in executions if e['status'] == 'failed']
            if failed:
                me.say(f"  - {len(failed)} failures:")
                for f in failed[:5]:
                    me.say(f"    - {f['flow_index']}: {f['inference_type']}")
        
        # Custom SQL query for advanced investigation
        recent_errors = you.db.query(
            "SELECT flow_index, status, timestamp FROM executions "
            "WHERE status = 'failed' ORDER BY timestamp DESC LIMIT 10"
        )
        if recent_errors:
            me.say(f"Recent errors: {len(recent_errors)}")
    
    
    def compare_checkpoints(self, run_id: str, cycle1: int, cycle2: int):
        """Compare two checkpoints to see what changed."""
        
        # PRIVATE: Get checkpoint states
        state1 = you.db.get_checkpoint_state(run_id, cycle1)
        state2 = you.db.get_checkpoint_state(run_id, cycle2)
        
        # Compare blackboards
        bb1 = state1.get('blackboard', {})
        bb2 = state2.get('blackboard', {})
        
        changed = []
        for key in set(bb1.keys()) | set(bb2.keys()):
            if bb1.get(key) != bb2.get(key):
                changed.append(key)
        
        # PUBLIC: Show differences
        me.say(f"Changes between cycle {cycle1} and {cycle2}:")
        me.say(f"  {len(changed)} concepts changed: {changed[:10]}")
```

---

## Implementation Mapping

All underlying components **already exist** as canvas tools:

| Shortcut | Wraps | Location |
|----------|-------|----------|
| `you.files.*` | `CanvasFileSystemTool` | `tools/file_system_tool.py` |
| `you.code.*` | `CanvasPythonInterpreterTool` | `tools/python_interpreter_tool.py` |
| `you.parser.*` | `CanvasParserTool` | `tools/parser_tool.py` |
| `you.llm.*` | `CanvasLLMTool` | `tools/llm_tool.py` |
| `you.prompt.*` | `CanvasPromptTool` | `tools/prompt_tool.py` |
| `you.paradigm.*` | `CanvasParadigmTool` | `tools/paradigm_tool.py` |
| `you.model.*` | `CanvasModelRunnerTool` | `tools/model_runner_tool.py` |
| `you.compose.*` | `CanvasCompositionTool` | `tools/composition_tool.py` |
| `you.perceive.*` | `CanvasPerceptionRouter` | `tools/perception_router_tool.py` |
| `you.format.*` | `CanvasFormatterTool` | `tools/formatter_tool.py` |
| `you.input.*` | `CanvasUserInputTool` | `tools/user_input_tool.py` |
| `you.blackboard.*` | `ExecutionController` | `services/execution/controller.py` |
| `you.graph.*` | `GraphService` | `services/graph_service.py` |
| `you.db.*` | `OrchestratorDB` | `infra/_orchest/_db.py` |
| `you.system.*` | Worker registry, connections | `services/execution/` |
| `you.history.*` | Execution logs, state snapshots | `services/execution/controller.py` |

**Implementation**: Thin facade wrapping existing tools/services.

```python
class SecondPersonPerspective:
    """Implementation - wraps all canvas tools."""
    
    def __init__(
        self, 
        # Canvas tools
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
        controller: ExecutionController,
        graph_service: GraphService,
        worker_registry: WorkerRegistry,
        db: OrchestratorDB  # Database access
    ):
        # Data access
        self.files = FilesFacade(file_tool)
        self.parser = ParserFacade(parser_tool)
        self.graph = GraphFacade(graph_service)
        self.blackboard = BlackboardFacade(controller)
        self.db = DatabaseFacade(db)  # Direct DB queries
        
        # Execution
        self.code = CodeFacade(python_tool)
        self.llm = LLMFacade(llm_tool)
        self.prompt = PromptFacade(prompt_tool)
        
        # Paradigm/model
        self.paradigm = ParadigmFacade(paradigm_tool)
        self.model = ModelFacade(model_runner_tool)
        self.compose = ComposeFacade(composition_tool)
        self.perceive = PerceiveFacade(perception_router)
        self.format = FormatFacade(formatter_tool)
        
        # Interaction
        self.input = InputFacade(user_input_tool)
        
        # System
        self.system = SystemFacade(worker_registry)
        self.history = HistoryFacade(controller)
```

---

## Summary

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│   "I" (First Person)                "You" (Second Person)                   │
│   ─────────────────                 ──────────────────────                   │
│   SHARED STAGE                      PRIVATE WORKSPACE / DIRECT TOOLS        │
│   User sees everything              User sees nothing (except input)        │
│   Changes UI state                  Direct tool access                      │
│                                                                              │
│   me.vision.*  (see UI)             DATA ACCESS:                            │
│   me.hands.*   (interact)             you.files.*      (file operations)    │
│   me.mind.*    (control)              you.blackboard.* (computed values)    │
│   me.say()     (chat)                 you.parser.*     (NormCode parsing)   │
│                                       you.graph.*      (graph queries)      │
│                                       you.db.*         (database queries)   │
│                                                                              │
│                                     EXECUTION:                               │
│                                       you.code.*       (Python execution)   │
│                                       you.llm.*        (LLM calls)          │
│                                       you.prompt.*     (prompt templates)   │
│                                                                              │
│                                     PARADIGM/MODEL:                          │
│                                       you.paradigm.*   (load paradigms)     │
│                                       you.model.*      (run sequences)      │
│                                       you.compose.*    (function compose)   │
│                                       you.perceive.*   (perception route)   │
│                                       you.format.*     (data formatting)    │
│                                                                              │
│                                     INTERACTION:                             │
│                                       you.input.*      (user input)         │
│                                                                              │
│                                     SYSTEM:                                  │
│                                       you.system.*     (system state)       │
│                                       you.history.*    (trace data)         │
│                                                                              │
│   See also: Third Person (it.*) for observing activity/events              │
│                                                                              │
│   Pattern: you.* → process privately → me.say(result)                       │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

**"You" is AI's direct tool access. "I" is the shared stage.**

---
