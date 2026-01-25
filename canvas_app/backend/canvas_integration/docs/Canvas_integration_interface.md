# Canvas Integration Interface Design

A unified interface for AI to interact with the Canvas App, organized by **perspective**.

---

## The Three Perspectives

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           CANVAS INTEGRATION                                     │
│                                                                                 │
│    ┌─────────────────────────────────────────────────────────────────────┐     │
│    │                        ICanvasIntegration                            │     │
│    │                     (composes all perspectives)                      │     │
│    └─────────────────────────────────────────────────────────────────────┘     │
│                │                    │                    │                      │
│                ▼                    ▼                    ▼                      │
│    ┌───────────────────┐ ┌───────────────────┐ ┌───────────────────┐           │
│    │   First Person    │ │  Second Person    │ │   Third Person    │           │
│    │      ("I")        │ │     ("You")       │ │      ("It")       │           │
│    │                   │ │                   │ │                   │           │
│    │   SHARED STAGE    │ │  DIRECT TOOLS     │ │  ACTIVITY STREAM  │           │
│    │   User sees       │ │ User doesn't see  │ │  Meta-observation │           │
│    │                   │ │                   │ │                   │           │
│    │   • vision        │ │ DATA:             │ │   • events        │           │
│    │   • hands         │ │   files,blackboard│ │   • activity      │           │
│    │   • mind          │ │   parser,graph,db │ │                   │           │
│    │                   │ │ EXEC:             │ │                   │           │
│    │                   │ │   code,llm,prompt │ │                   │           │
│    │                   │ │ MODEL:            │ │                   │           │
│    │                   │ │   paradigm,model  │ │                   │           │
│    │                   │ │   compose,perceive│ │                   │           │
│    │                   │ │ OTHER:            │ │                   │           │
│    │                   │ │   input,system    │ │                   │           │
│    └───────────────────┘ └───────────────────┘ └───────────────────┘           │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

| Perspective | Pronoun | Question | Focus | Visibility |
|-------------|---------|----------|-------|------------|
| **First** | "I" | "What do I see/do?" | Acting on UI | User sees |
| **Second** | "You" | "What is the data?" | Querying backend | User doesn't see |
| **Third** | "It" | "What is happening?" | Observing activity | Meta-level |

---

## Design Principles

1. **Perspective-Based** - Organized by WHO is acting, not WHAT is being done
2. **Clear Visibility** - Know whether user will see the effect
3. **Separation of Concerns** - Each perspective has distinct purpose
4. **Composable** - Use perspectives together for complex tasks
5. **Discoverable** - Clear hierarchy within each perspective

---

## Main Interface

```python
from typing import Protocol


class ICanvasIntegration(Protocol):
    """
    Main entry point for Canvas App integration.
    
    Composes three perspectives:
    - me (First Person): Act as user on shared stage
    - you (Second Person): Private backend queries
    - it (Third Person): Observe system activity
    """
    
    @property
    def me(self) -> 'IFirstPersonPerspective':
        """
        First Person - "I am the user"
        
        Everything here affects what the user sees.
        Use for UI interaction and state changes.
        """
        ...
    
    @property
    def you(self) -> 'ISecondPersonPerspective':
        """
        Second Person - "You are my helper"
        
        Private workspace for backend queries.
        User sees nothing until you show them via `me`.
        """
        ...
    
    @property
    def it(self) -> 'IThirdPersonPerspective':
        """
        Third Person - "What is happening"
        
        Observe system activity and events.
        Meta-level observation of the system.
        """
        ...
```

---

## First Person ("I") - Shared Stage

> **See**: `First_person_perspective.md`

The AI acts **as the user**. Everything is visible to the user.

```python
class IFirstPersonPerspective(Protocol):
    """I am the user. I see what they see. I do what they can do."""
    
    @property
    def vision(self) -> 'IVision':
        """My eyes - what I can see (snapshots, details, state)"""
        ...
    
    @property
    def hands(self) -> 'IHands':
        """My hands - what I can manipulate (click, type, navigate)"""
        ...
    
    @property
    def mind(self) -> 'IMind':
        """My mind - understanding and control (run, configure, query)"""
        ...
    
    # Shortcuts
    def look(self) -> 'UserViewSnapshot': ...
    def click(self, target: str) -> 'ActionResult': ...
    def say(self, message: str) -> 'ActionResult': ...
```

### Faculties

| Faculty | Purpose | Examples |
|---------|---------|----------|
| `vision` | See UI state | `get_canvas()`, `get_chat()`, `get_execution()` |
| `hands` | Manipulate UI | `click_node()`, `collapse_node()`, `say()` |
| `mind` | Control & understand | `run()`, `pause()`, `get_concept_value()` |

---

## Second Person ("You") - Private Workspace / Direct Tools

> **See**: `Second_person_perspective.md`

AI's private backend/tool access. User sees nothing (except when using input tool).

```python
class ISecondPersonPerspective(Protocol):
    """You are my helper. Direct tool access, parallel, non-interfering."""
    
    # Data access
    @property
    def files(self) -> 'IFiles': ...
    @property
    def blackboard(self) -> 'IBlackboard': ...
    @property
    def parser(self) -> 'IParser': ...
    @property
    def graph(self) -> 'IGraph': ...
    @property
    def db(self) -> 'IDatabase': ...
    
    # Execution
    @property
    def code(self) -> 'ICode': ...
    @property
    def llm(self) -> 'ILLM': ...
    @property
    def prompt(self) -> 'IPrompt': ...
    
    # Paradigm/model
    @property
    def paradigm(self) -> 'IParadigm': ...
    @property
    def model(self) -> 'IModel': ...
    @property
    def compose(self) -> 'ICompose': ...
    @property
    def perceive(self) -> 'IPerceive': ...
    @property
    def format(self) -> 'IFormat': ...
    
    # Interaction
    @property
    def input(self) -> 'IInput': ...
    
    # System
    @property
    def system(self) -> 'ISystem': ...
    @property
    def history(self) -> 'IHistory': ...
```

### Sub-interfaces

| Category | Interface | Purpose | Examples |
|----------|-----------|---------|----------|
| **Data** | `files` | File operations | `read()`, `write()`, `list_dir()` |
| | `blackboard` | Concept values | `get()`, `get_all()`, `get_logs()` |
| | `parser` | NormCode parsing | `parse()`, `serialize()`, `convert()` |
| | `graph` | Graph queries | `get_nodes()`, `get_parents()` |
| | `db` | Database queries | `query()`, `get_runs()`, `get_checkpoints()` |
| **Exec** | `code` | Python execution | `run()`, `run_function()` |
| | `llm` | LLM calls | `call()`, `call_with_messages()` |
| | `prompt` | Prompt templates | `read()`, `substitute()` |
| **Model** | `paradigm` | Paradigm loading | `load()`, `list_paradigms()` |
| | `model` | Model execution | `run_sequence()`, `create_env()` |
| | `compose` | Function composition | `compose()`, `execute_plan()` |
| | `perceive` | Perception routing | `encode_sign()`, `perceive()` |
| | `format` | Data formatting | `format()`, `parse()` |
| **Other** | `input` | User input | `request()`, `request_choice()` |
| | `system` | System state | `get_workers()`, `get_connections()` |
| | `history` | Historical data | `get_trace()`, `get_state_at_cycle()` |

---

## Third Person ("It") - Activity Stream

> **See**: `Third_person_perspective.md`

Observing system activity and behavior over time.

```python
class IThirdPersonPerspective(Protocol):
    """What is happening - observing system activity."""
    
    @property
    def events(self) -> 'IEvents':
        """Event stream observation"""
        ...
    
    @property
    def activity(self) -> 'IActivity':
        """Activity pattern analysis"""
        ...
```

### Sub-interfaces

| Interface | Purpose | Examples |
|-----------|---------|----------|
| `events` | Event stream | `stream()`, `recent()`, `by_type()` |
| `activity` | Activity patterns | `timeline()`, `compare_runs()`, `analyze_sequence()` |

---

## Comparison: Second vs Third Person

Both are "invisible" to the user, but differ in focus:

| Aspect | Second Person (`you.*`) | Third Person (`it.*`) |
|--------|------------------------|----------------------|
| **Focus** | Query DATA/STATE | Observe ACTIVITY/BEHAVIOR |
| **Nature** | Static queries | Dynamic observation |
| **Examples** | Workers list, trace data, logs | Event stream, timeline, patterns |
| **Question** | "What is there?" | "What's happening?" |

---

## Usage Patterns

### Pattern 1: Observe → Act

```python
# Look at current state
snapshot = canvas.me.look()

# Take action based on what we see
if snapshot.execution.status == "paused":
    canvas.me.mind.run()
```

### Pattern 2: Query Privately → Show Publicly

```python
# Gather data privately (user sees nothing)
content = canvas.you.files.read("config.json")
values = canvas.you.blackboard.get_all()

# Show summary to user (now they see)
canvas.me.say(f"Config has {len(content)} bytes, {len(values)} computed values")
```

### Pattern 3: Monitor Activity

```python
# Stream events as they happen
for event in canvas.it.events.stream():
    if event['type'] == 'error':
        # React to errors
        canvas.me.say(f"Error detected: {event['message']}")
```

### Pattern 4: Debug with All Perspectives

```python
def debug_node(node_id: str):
    # First Person: See what user sees
    details = canvas.me.vision.get_node_details(node_id)
    
    # Second Person: Get data directly
    value = canvas.you.blackboard.get(details.concept_name)
    trace = canvas.you.history.get_trace(details.flow_index)
    
    # Third Person: Check what happened
    events = canvas.it.events.by_type("inference:failed", limit=5)
    
    # First Person: Show findings
    canvas.me.say(f"Node {node_id}: {details.label}")
    canvas.me.say(f"Value: {value}")
    canvas.me.say(f"Recent failures: {len(events)}")
    canvas.me.hands.highlight_branch(node_id)
```

---

## Complete Interface Summary

```
ICanvasIntegration
├── me: IFirstPersonPerspective      # SHARED STAGE (user sees)
│   ├── vision: IVision              # See UI state
│   │   ├── get_full_snapshot()
│   │   ├── get_canvas()
│   │   ├── get_chat()
│   │   ├── get_panels()
│   │   ├── get_execution()
│   │   ├── get_logs()
│   │   ├── get_project()
│   │   ├── get_node_details(id)
│   │   ├── get_visible_nodes()
│   │   └── get_selected_nodes()
│   │
│   ├── hands: IHands                # Manipulate UI
│   │   ├── click_node(id)
│   │   ├── select_nodes(ids)
│   │   ├── collapse_node(id)
│   │   ├── expand_node(id)
│   │   ├── zoom_in/out/to()
│   │   ├── pan(dx, dy)
│   │   ├── fit_view()
│   │   ├── center_on_node(id)
│   │   ├── open/close/toggle_panel()
│   │   ├── say(message)
│   │   ├── respond_to_prompt(response)
│   │   ├── toggle_breakpoint(id)
│   │   └── ... (35+ methods)
│   │
│   ├── mind: IMind                  # Control & understand
│   │   ├── run()
│   │   ├── pause()
│   │   ├── step()
│   │   ├── stop()
│   │   ├── restart()
│   │   ├── set_run_mode(mode)
│   │   ├── set_layout_mode(mode)
│   │   ├── get_concept_value(name)
│   │   ├── override_value(name, value)
│   │   └── ... (20+ methods)
│   │
│   └── shortcuts
│       ├── look() → vision.get_full_snapshot()
│       ├── click(id) → hands.click_node(id)
│       └── say(msg) → hands.say(msg)
│
├── you: ISecondPersonPerspective    # PRIVATE WORKSPACE / DIRECT TOOLS
│   │
│   ├── [DATA ACCESS]
│   ├── files: IFiles                # CanvasFileSystemTool
│   │   ├── read(path), write(path, content)
│   │   ├── read_json(path), write_json(path, data)
│   │   └── list_dir(path), exists(path), delete(path)
│   ├── blackboard: IBlackboard      # ExecutionController
│   │   ├── get(name), get_all(), get_status(name)
│   │   └── list_concepts(), get_logs(limit)
│   ├── parser: IParser              # CanvasParserTool
│   │   └── parse(), serialize(), convert(), validate()
│   ├── graph: IGraph                # GraphService
│   │   └── get_nodes(), get_edges(), get_node(), get_parents()
│   ├── db: IDatabase                # OrchestratorDB
│   │   ├── query(sql), get_runs(), get_run_metadata()
│   │   └── get_executions(), get_checkpoints()
│   │
│   ├── [EXECUTION]
│   ├── code: ICode                  # CanvasPythonInterpreterTool
│   │   └── run(code, inputs), run_function(code, name, params)
│   ├── llm: ILLM                    # CanvasLLMTool
│   │   └── call(prompt), call_with_messages(), get_available_models()
│   ├── prompt: IPrompt              # CanvasPromptTool
│   │   └── read(path), substitute(template, **kwargs)
│   │
│   ├── [PARADIGM/MODEL]
│   ├── paradigm: IParadigm          # CanvasParadigmTool
│   │   └── load(name), list_paradigms(), list_manifest()
│   ├── model: IModel                # CanvasModelRunnerTool
│   │   └── create_env(), run_sequence(), execute_affordance()
│   ├── compose: ICompose            # CanvasCompositionTool
│   │   └── compose(plan), execute_plan(plan, input)
│   ├── perceive: IPerceive          # CanvasPerceptionRouter
│   │   └── encode_sign(), decode_sign(), perceive(), transform()
│   ├── format: IFormat              # CanvasFormatterTool
│   │   └── format(data, type), parse(content, type)
│   │
│   ├── [INTERACTION]
│   ├── input: IInput                # CanvasUserInputTool
│   │   └── request(prompt), request_choice(), request_confirmation()
│   │
│   ├── [SYSTEM]
│   ├── system: ISystem              # WorkerRegistry, connections
│   │   └── get_workers(), get_connections(), get_tool_calls()
│   └── history: IHistory            # Execution logs, state
│       └── get_trace(flow_index), get_state_at_cycle(cycle)
│
└── it: IThirdPersonPerspective      # ACTIVITY STREAM (meta-observation)
    ├── events: IEvents
    │   ├── stream(filter)
    │   ├── recent(limit)
    │   ├── between(start, end)
    │   └── by_type(type, limit)
    │
    └── activity: IActivity
        ├── timeline(limit)
        ├── compare_runs(id1, id2)
        ├── analyze_sequence(flow_index)
        └── get_patterns()
```

---

## Implementation

Each perspective wraps existing infrastructure:

| Perspective | Wraps |
|-------------|-------|
| First Person (`me`) | WebSocket events, frontend state |
| Second Person (`you`) | All canvas tools (15+), services, database |
| Third Person (`it`) | Event store, activity logs |

```python
class CanvasIntegration:
    """Concrete implementation."""
    
    def __init__(
        self,
        emit_callback: Callable,
        frontend_state: FrontendStateProvider,
        tools: CanvasToolSet,
        services: ServiceContainer,
        event_store: EventStore
    ):
        self._me = FirstPersonPerspective(emit_callback, frontend_state)
        self._you = SecondPersonPerspective(tools, services)
        self._it = ThirdPersonPerspective(event_store)
    
    @property
    def me(self) -> IFirstPersonPerspective:
        return self._me
    
    @property
    def you(self) -> ISecondPersonPerspective:
        return self._you
    
    @property
    def it(self) -> IThirdPersonPerspective:
        return self._it
```

---

## Migration Path

1. **Phase 1**: Define interfaces (✓ this document)
2. **Phase 2**: Implement `FirstPersonPerspective` wrapping WebSocket/frontend
3. **Phase 3**: Implement `SecondPersonPerspective` wrapping existing tools
4. **Phase 4**: Implement `ThirdPersonPerspective` wrapping event store
5. **Phase 5**: Update tool injection to provide `ICanvasIntegration`
6. **Phase 6**: Migrate existing code to use new interfaces

---

## Benefits

| Benefit | Description |
|---------|-------------|
| **Clarity** | Know immediately if user will see the effect |
| **Composability** | Mix perspectives for complex tasks |
| **Testability** | Mock each perspective independently |
| **Discoverability** | IDE autocomplete shows all capabilities |
| **Maintainability** | Clear boundaries between concerns |

---

## Related Documents

- `First_person_perspective.md` - Detailed First Person interface
- `Second_person_perspective.md` - Detailed Second Person interface
- `Third_person_perspective.md` - Detailed Third Person interface
- `CANVAS_INTEGRATION_INVENTORY.md` - Existing capabilities inventory

---
