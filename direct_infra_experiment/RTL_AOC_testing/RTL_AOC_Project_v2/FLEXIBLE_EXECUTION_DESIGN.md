# Flexible Execution Design for NormCode Workflows

**Goal**: Enable NormCode workflows to have flexible entry and exit points, making them usable as dynamic tools in larger systems (chat agents, APIs, interactive sessions).

---

## Current Model

### How It Works Today

```
┌─────────────────────────────────────────────────────────────┐
│  Fixed Entry (Root)                                          │
│       ↓                                                      │
│  Execute ALL Inferences (bottom-up)                          │
│       ↓                                                      │
│  Fixed Exit (Root Output)                                    │
└─────────────────────────────────────────────────────────────┘
```

**Characteristics:**
- Entry: Always the root concept
- Exit: Always the root concept  
- Execution: All inferences run (unless skipped by timing gates)
- Ground concepts: Statically defined in `concept_repo.json` with `is_ground_concept: true`
- Input injection: Only for ground concepts via `inputs.json`

### Current Input Injection Flow

```
inputs.json
    ↓
concept_repo.add_reference(name, data, axes)  // Any concept by name
    ↓
_sync_ground_concept_statuses()               // Marks concepts with data as 'complete'
    ↓
Orchestrator checks: item_status == 'pending' AND is_ready(item)
    ↓
Execute inference  // ← PROBLEM: Runs even if output already has data!
```

---

## Proposed Model: Flexible Entry/Exit

### The Vision

```
┌─────────────────────────────────────────────────────────────┐
│  Flexible Entry: Any concept(s) with provided data          │
│       ↓                                                      │
│  Execute ONLY necessary inferences (minimal subgraph)        │
│       ↓                                                      │
│  Flexible Exit: Any requested target concept(s)              │
└─────────────────────────────────────────────────────────────┘
```

### Example: RTL AOC Workflow

**Scenario 1: Full Workflow**
```
Provided: {ISA file path}, {MA file path}, {trace file path}
Target: {verification report}
→ Executes: Phase 1 + Phase 2 (everything)
```

**Scenario 2: Skip Phase 1**
```
Provided: {AOC definitions} (already have it!)
Target: {verification report}
→ Executes: Phase 2 only
→ Skips: All of Phase 1 (spec loading, user input, extraction loop)
```

**Scenario 3: Just Extract AOCs**
```
Provided: {ISA file path}, {MA file path}
Target: {AOC definitions}
→ Executes: Phase 1 only
→ Skips: Phase 2 (trace verification)
```

**Scenario 4: Verify Single Cycle**
```
Provided: {AOC definitions}, {trace per cycle}, cycle_index=5
Target: {verification} for cycle 5
→ Executes: Single cycle verification
→ Skips: Everything else
```

---

## Implementation: The Gap Analysis

### What Already Works ✅

1. **Input injection is concept-agnostic**
   ```python
   # canvas_app/backend/services/execution/controller.py:490-498
   for name, value in inputs_data.items():
       self.concept_repo.add_reference(name, value['data'], axes)
   # No check for is_ground_concept!
   ```

2. **Status sync checks actual data, not ground flag**
   ```python
   # controller.py:1570-1579
   # "Don't rely on is_ground_concept flag - only the presence of data matters"
   has_reference_data = (concept.reference is not None)
   if has_reference_data:
       blackboard.set_concept_status(concept_name, 'complete')
   ```

3. **Concept-to-inference mapping exists**
   ```python
   # blackboard.py:94
   self.concept_to_flow_index[inferred_concept_name] = flow_index
   ```

### What's Missing ❌

1. **Inference skip when output has data**
   ```python
   # orchestrator.py:736 - Current logic
   if item_status == 'pending' and is_ready(item):
       execute_item(item)  # Runs even if output already complete!
   ```

2. **Target-based execution**
   - No way to say "I only want {AOC definitions}"
   - Always runs until all inferences complete

3. **Subgraph pruning**
   - No mechanism to compute minimal execution path
   - Runs everything regardless of what's needed

---

## Proposed Changes

### Change 1: Skip Inference When Output Has Data (Minimal)

**File**: `infra/_orchest/_orchestrator.py`

**Current** (line ~736):
```python
if self.blackboard.get_item_status(flow_index) == 'pending' and self._is_ready(item):
    new_status = self._execute_item(item)
```

**Proposed**:
```python
if self.blackboard.get_item_status(flow_index) == 'pending' and self._is_ready(item):
    # NEW: Check if output concept already has data
    inferred_concept = item.inference_entry.concept_to_infer.concept_name
    if self.blackboard.get_concept_status(inferred_concept) == 'complete':
        # Output already has data - skip execution
        self.blackboard.set_item_status(flow_index, 'completed')
        self.blackboard.set_item_completion_detail(flow_index, 'provided')
        logging.info(f"[{flow_index}] Skipped - output '{inferred_concept}' already has data")
        continue
    
    new_status = self._execute_item(item)
```

**Impact**: ~10 lines of code. Enables flexible entry points via `inputs.json`.

### Change 2: Mark Source Inference at Injection Time (Alternative)

**File**: `canvas_app/backend/services/execution/controller.py`

**In** `_sync_ground_concept_statuses()`:
```python
if has_reference_data:
    self.orchestrator.blackboard.set_concept_status(concept_name, 'complete')
    
    # NEW: Also mark the source inference as complete
    flow_index = self.orchestrator.blackboard.concept_to_flow_index.get(concept_name)
    if flow_index and self.node_statuses.get(flow_index) == NodeStatus.PENDING:
        self.node_statuses[flow_index] = NodeStatus.COMPLETED
        self.orchestrator.blackboard.set_item_status(flow_index, 'completed')
        self.orchestrator.blackboard.set_item_completion_detail(flow_index, 'injected')
```

### Change 3: Target-Based Execution (Future)

**New Parameter**:
```python
orchestrator.run(
    targets=["{AOC definitions}"],  # Stop when these are complete
    # ... existing params
)
```

**Logic**:
```python
def _all_targets_complete(self) -> bool:
    if not self.targets:
        return False  # No targets = run everything
    return all(
        self.blackboard.get_concept_status(t) == 'complete' 
        for t in self.targets
    )

# In run loop:
while cycle < max_cycles:
    if self._all_targets_complete():
        break  # Done!
    # ... execute cycle
```

### Change 4: Subgraph Pruning (Future)

**New Method**:
```python
def compute_required_subgraph(self, targets: List[str], provided: List[str]) -> Set[str]:
    """
    Given target concepts and provided concepts, compute minimal set of 
    inferences needed.
    """
    required = set()
    queue = list(targets)
    
    while queue:
        concept = queue.pop()
        if concept in provided:
            continue  # Already have it
            
        flow_index = self.blackboard.concept_to_flow_index.get(concept)
        if flow_index:
            required.add(flow_index)
            # Add dependencies to queue
            item = self.waitlist.get_item(flow_index)
            for vc in item.inference_entry.value_concepts:
                queue.append(vc.concept_name)
    
    return required
```

---

## API Design for Tool Usage

### Current API

```python
# Load and run everything
controller.load_repositories(concepts_path, inferences_path, inputs_path)
controller.start_execution()
```

### Proposed API

```python
# Option 1: Simple - Use inputs.json with non-ground concepts
inputs = {
    "{AOC definitions}": {
        "data": [[aoc_data]],
        "axes": ["_none_axis"]
    }
}
controller.load_repositories(concepts_path, inferences_path, inputs=inputs)
controller.start_execution()  # Automatically skips Phase 1

# Option 2: Explicit targets
controller.load_repositories(concepts_path, inferences_path, inputs_path)
controller.start_execution(targets=["{AOC definitions}"])  # Stops after Phase 1

# Option 3: Full control
controller.load_repositories(concepts_path, inferences_path)
controller.inject_values({
    "{AOC definitions}": aoc_data,
    "{trace per cycle}": trace_data
})
controller.start_execution(
    targets=["{verification for cycle 5}"],
    skip_completed=True
)
```

### REST API Extension

```
POST /api/execution/start
{
    "targets": ["{AOC definitions}"],          // Optional: stop when complete
    "provided": {                               // Optional: inject values
        "{ISA spec text}": "... spec content ..."
    },
    "skip_if_complete": true                   // Skip inferences with output data
}
```

---

## Use Cases Enabled

### 1. Chat Agent with Tool Calling

```
User: "I already have these AOC rules. Can you verify this trace?"

Agent:
  1. Parses user intent → needs verification
  2. User provided: AOC rules
  3. Calls workflow with:
     - provided: {AOC definitions}
     - targets: {verification report}
  4. Workflow skips Phase 1, runs Phase 2
  5. Returns verification report
```

### 2. Incremental/Interactive Session

```
Session 1: User uploads specs
  → Run Phase 1 → Save {AOC definitions}

Session 2: User uploads trace
  → Inject saved {AOC definitions}
  → Run Phase 2 only
  
Session 3: User uploads new trace
  → Inject saved {AOC definitions}
  → Run Phase 2 with new trace
```

### 3. Microservice Architecture

```
Service A: AOC Extraction
  - Input: specs
  - Output: {AOC definitions}
  - Runs: Phase 1 only

Service B: Trace Verification  
  - Input: {AOC definitions}, trace
  - Output: {verification report}
  - Runs: Phase 2 only

Orchestrating Service:
  - Chains A → B as needed
  - Can cache AOC definitions
  - Can run B multiple times with different traces
```

### 4. Debugging/Development

```
# Test just the verification logic
inject: {AOC definitions} = mock_aoc_data
inject: {trace per cycle} = test_trace
target: {verification}
→ Runs only the verification step
```

---

## Implementation Roadmap

### Phase A: Minimal Change (1-2 days)
- [ ] Add output-has-data check in orchestrator
- [ ] Add 'provided' / 'injected' completion detail
- [ ] Test with RTL AOC workflow

### Phase B: Canvas App Integration (2-3 days)
- [ ] UI for injecting concept values at runtime
- [ ] Show "provided" badge on injected nodes
- [ ] Allow selecting target concepts

### Phase C: API Extension (3-5 days)
- [ ] Add `targets` parameter to execution API
- [ ] Add `provided` parameter for runtime injection
- [ ] Add `skip_if_complete` flag
- [ ] Update WebSocket events for partial execution

### Phase D: Subgraph Optimization (Future)
- [ ] Compute minimal execution path
- [ ] Skip irrelevant branches entirely
- [ ] Show execution plan before running

---

## Questions to Resolve

1. **Status naming**: Should we use `'provided'`, `'injected'`, or `'precomputed'`?

2. **Inference vs Concept**: When output has data, do we:
   - Mark inference as `'completed'` with detail `'provided'`?
   - Mark inference as `'skipped'` with detail `'output_provided'`?
   - Create new status `'bypassed'`?

3. **Validation**: Should we validate injected data matches expected shape/type?

4. **UI feedback**: How to show which parts were skipped vs executed?

5. **Determinism**: If same inputs injected, should we guarantee same skip pattern?

---

---

## Part 2: Built-in Project as Workflow Tool

### Current Architecture

The Canvas App has a chat interface driven by **built-in projects**:

```
canvas_app/built_in_projects/
├── canvas_assistant/                # Current: Chat-driven assistant
│   ├── canvas_assistant.normcode-canvas.json
│   ├── repos/
│   │   ├── chat.concept.json
│   │   └── chat.inference.json
│   └── provisions/
│       ├── paradigms/
│       │   ├── c_ChatRead-o_Literal.json
│       │   ├── h_Response-c_ChatWrite-o_Status.json
│       │   └── h_Command-c_CanvasExecute-o_Status.json
│       └── prompts/
└── README.md
```

**The Canvas Assistant pattern**:
```
User Message → c_ChatRead → LLM (classify) → c_CanvasExecute → h_ChatWrite → Response
                    ↓
              Loop until termination
```

### The Vision: Workflow Tool Assistant

A new built-in project that can use **NormCode workflows as tools**:

```
canvas_app/built_in_projects/
├── canvas_assistant/           # Current: Canvas commands
└── workflow_assistant/         # NEW: Workflow execution
    ├── workflow_assistant.normcode-canvas.json
    ├── repos/
    │   ├── workflow.concept.json
    │   └── workflow.inference.json
    └── provisions/
        ├── paradigms/
        │   ├── c_ChatRead-o_Literal.json
        │   ├── h_Response-c_ChatWrite-o_Status.json
        │   ├── c_WorkflowDiscover-o_List.json      # NEW
        │   ├── h_Intent-c_WorkflowMatch-o_Config.json  # NEW
        │   └── h_Config-c_WorkflowExecute-o_Result.json # NEW
        └── prompts/
            ├── understand_intent.md
            ├── extract_provided_values.md
            └── format_result.md
```

### New Paradigms Needed

#### 1. `c_WorkflowDiscover-o_List`

**Purpose**: Discover available workflows from registered projects

```json
{
  "metadata": {
    "description": "Discover available NormCode workflows from project registry",
    "inputs": {},
    "outputs": {
      "type": "List",
      "description": "List of workflow metadata (id, name, inputs, outputs)"
    }
  },
  "env_spec": {
    "tools": [{
      "tool_name": "workflow_registry",
      "affordances": [{
        "affordance_name": "list_workflows",
        "call_code": "result = tool.list_workflows()"
      }]
    }]
  }
}
```

**Returns**:
```json
[
  {
    "id": "rtl_aoc_v2",
    "name": "RTL AOC Verification",
    "description": "...",
    "entry_points": [
      "{ISA file path}",
      "{AOC definitions}",  // Can skip Phase 1 if provided
      "{trace per cycle}"   // Can skip trace loading if provided
    ],
    "outputs": [
      "{AOC definitions}",
      "{verification report}"
    ]
  }
]
```

#### 2. `h_Intent-c_WorkflowMatch-o_Config`

**Purpose**: Match user intent to a workflow + determine provided values

```json
{
  "metadata": {
    "description": "Match user intent to workflow and extract provided values",
    "inputs": {
      "vertical": {
        "workflows": "Available workflows from discovery"
      },
      "horizontal": {
        "user_message": "User's request",
        "conversation_context": "Previous messages"
      }
    },
    "outputs": {
      "type": "Config",
      "description": "Workflow config with provided values and targets"
    }
  }
}
```

**Example Output**:
```json
{
  "workflow_id": "rtl_aoc_v2",
  "provided": {
    "{AOC definitions}": "...user provided AOC...",
    "{trace file path}": "/uploads/trace.json"
  },
  "targets": ["{verification report}"],
  "skip_phases": ["Phase 1"]
}
```

#### 3. `h_Config-c_WorkflowExecute-o_Result`

**Purpose**: Execute workflow with flexible entry/exit points

```json
{
  "metadata": {
    "description": "Execute a workflow with provided values and target concepts",
    "inputs": {
      "horizontal": {
        "config": "Workflow configuration from matcher"
      }
    },
    "outputs": {
      "type": "Result",
      "description": "Execution result with target concept values"
    }
  },
  "env_spec": {
    "tools": [{
      "tool_name": "workflow_executor",
      "affordances": [{
        "affordance_name": "execute",
        "call_code": "result = tool.execute(config)"
      }]
    }]
  }
}
```

### The Workflow Assistant Plan (`.ncds`)

```ncds
/: Workflow Assistant - Uses NormCode workflows as tools

:<: session ends
    <= return session ends 
        <= if termination condition is met

    <- available workflows
        <= discover available workflows      /: c_WorkflowDiscover

    <- on-going messages 
        <= initiate the on-going messages

    <- all results
        <= for every on-going message

            <= return the result

            <- new message 
                <= :>(chat): user gives a new message 

            /: Understand what the user wants
            <- workflow config
                <= match user intent to workflow and extract values
                <- new message
                <- conversation history
                <- available workflows

            /: Execute if workflow matched
            <- execution result
                <= execute workflow with flexible entry
                    <= if workflow was matched
                    <* workflow was matched?
                <- workflow config

            /: Format and respond
            <- response 
                <= format execution result as chat response
                <- execution result
                <- workflow config

            <- response given
                <= :(chat): send response to user
                <- response

            <- termination condition is met
                <= judge if should terminate
                <- response 
        <- on-going messages
```

### Interaction Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ User: "I have these AOC rules already. Can you verify this     │
│        trace file I uploaded?"                                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ c_WorkflowDiscover → List of workflows including RTL AOC        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ h_Intent-c_WorkflowMatch:                                       │
│   - User wants: RTL verification                                │
│   - Provided: AOC rules (from message), trace file (upload)     │
│   - Target: verification report                                 │
│   - Config: skip Phase 1, run Phase 2                           │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ h_Config-c_WorkflowExecute:                                     │
│   - Load RTL AOC workflow                                       │
│   - Inject: {AOC definitions}, {trace file path}                │
│   - Execute Phase 2 only (Phase 1 skipped)                      │
│   - Return: {verification report}                               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ Assistant: "I've verified your trace against the AOC rules.     │
│             Here's the report: [verification results]"          │
└─────────────────────────────────────────────────────────────────┘
```

### Backend Support Needed

#### 1. WorkflowRegistry Tool

```python
class WorkflowRegistryTool:
    """Tool for discovering available workflows."""
    
    def list_workflows(self) -> List[WorkflowMetadata]:
        """
        Scan project registry for workflows.
        
        Returns workflow metadata including:
        - Entry points (concepts that can be injected)
        - Output concepts (what can be requested)
        - Description and documentation
        """
        workflows = []
        for project in project_registry.get_all():
            if project.is_workflow():
                workflows.append(self._extract_metadata(project))
        return workflows
    
    def _extract_metadata(self, project) -> WorkflowMetadata:
        """Extract entry points and outputs from workflow structure."""
        # Analyze concept_repo to find:
        # - Ground concepts (natural entry points)
        # - Non-ground concepts with no dependencies (potential entry points)
        # - Root concept (natural output)
        # - Other output concepts (potential targets)
        pass
```

#### 2. WorkflowExecutor Tool

```python
class WorkflowExecutorTool:
    """Tool for executing workflows with flexible entry/exit."""
    
    def execute(self, config: WorkflowConfig) -> WorkflowResult:
        """
        Execute a workflow with provided values and targets.
        
        1. Load the workflow project
        2. Inject provided values
        3. Set target concepts
        4. Execute (skips inferences with output data)
        5. Return target concept values
        """
        # Load project
        controller = ExecutionController()
        controller.load_repositories(
            config.concepts_path,
            config.inferences_path,
            inputs=config.provided  # Inject provided values
        )
        
        # Execute with targets
        controller.start_execution(
            targets=config.targets,
            skip_if_complete=True
        )
        
        # Extract results
        return self._extract_results(controller, config.targets)
```

### File Upload Integration

The workflow assistant needs to handle file uploads:

```
User uploads: trace.json
     ↓
System: Stores at /uploads/session_123/trace.json
     ↓
User: "Verify this trace"
     ↓
Matcher: Recognizes uploaded file → maps to {trace file path}
     ↓
Executor: Injects {trace file path} = "/uploads/session_123/trace.json"
```

---

## Part 3: Two-Level Injection Model

### The Problem

For complex workflows, users need to inject data at different levels:

1. **File-level**: Change which files the workflow reads
2. **Concept-level**: Provide computed values directly (skip computation)

### Current Project Structure

```
rtl_aoc_project_v2/
├── inputs.json                      # Ground concept values
├── provisions/
│   └── inputs/                      # INPUT FILES
│       ├── specs/
│       │   ├── isa_v1.md            # ← User can replace this
│       │   └── uarch_v2.md          # ← User can replace this
│       └── trace/
│           └── rtl_trace.json       # ← User can replace this
├── repos/
│   ├── concept_repo.json
│   └── inference_repo.json
└── rtlaocprojectv2.normcode-canvas.json
```

### Level 1: File Injection (Change inputs.json paths)

**Use case**: User has their own spec files or trace file

```
Current inputs.json:
  "{trace file path}": "provisions/inputs/trace/rtl_trace.json"

User uploads: my_trace.json
          ↓
System stores: provisions/inputs/trace/my_trace.json  (or session folder)
          ↓
System updates inputs.json:
  "{trace file path}": "provisions/inputs/trace/my_trace.json"
          ↓
Workflow runs normally, but reads user's file
```

**Implementation**:
```python
class WorkflowExecutorTool:
    def update_file_inputs(self, project_path: Path, file_mappings: dict):
        """
        Update inputs.json with new file paths.
        
        Args:
            file_mappings: {
                "{trace file path}": "/uploads/session_123/my_trace.json",
                "{ISA file path}": "/uploads/session_123/my_isa.md"
            }
        """
        inputs_path = project_path / "inputs.json"
        inputs = json.load(open(inputs_path))
        
        for concept_name, file_path in file_mappings.items():
            if concept_name in inputs:
                inputs[concept_name]["data"] = [[file_path]]
        
        json.dump(inputs, open(inputs_path, 'w'))
```

**Effect**: The workflow runs all phases, but reads from different files.

### Level 2: Concept Injection (Skip upstream computation)

**Use case**: User has pre-computed intermediate results

```
User already has AOC definitions (maybe from a previous run or another tool)
          ↓
User pastes: {"aoc_rules": [...], "canonical_forms": [...]}
          ↓
System injects directly into {AOC definitions} concept
          ↓
Workflow skips Phase 1, runs only Phase 2 (verification)
```

**Implementation** (using the flexible execution from Part 1):
```python
class WorkflowExecutorTool:
    def inject_concept_values(self, project_path: Path, concept_values: dict):
        """
        Inject values directly into concepts (not just ground concepts).
        
        Args:
            concept_values: {
                "{AOC definitions}": {"aoc_rules": [...], "canonical_forms": [...]},
                "{trace per cycle}": [{"cycle": 1, "events": [...]}, ...]
            }
        """
        # Load concept repo
        concepts = json.load(open(project_path / "repos/concept_repo.json"))
        
        for concept_name, value in concept_values.items():
            # Find concept and set its reference data
            concepts[concept_name]["reference_data"] = {
                "data": [[value]],
                "axes": ["_none_axis"]
            }
        
        json.dump(concepts, open(project_path / "repos/concept_repo.json", 'w'))
```

**Effect**: Upstream inferences are skipped because their output concepts already have data.

### Hybrid Injection Strategy

In practice, users will use BOTH levels:

| What User Provides | Injection Level | Effect |
|-------------------|-----------------|--------|
| New trace file | Level 1 (file) | Runs full workflow with different file |
| Pre-computed AOC schemas | Level 2 (concept) | Skips Phase 1, runs Phase 2 |
| New ISA spec file + existing trace cycles | Level 1 (file) + Level 2 (concept) | Runs Phase 1 only, uses provided cycles |

### The Workflow Matcher's Job

The `h_Intent-c_WorkflowMatch` paradigm needs to determine:

```json
{
  "workflow_id": "rtl_aoc_v2",
  
  "file_injections": {
    "_comment": "Level 1: Replace file paths in inputs.json",
    "{trace file path}": "/uploads/session/user_trace.json"
  },
  
  "concept_injections": {
    "_comment": "Level 2: Inject values directly, skip computation",
    "{AOC definitions}": {"aoc_rules": [...], "canonical_forms": [...]}
  },
  
  "targets": ["{verification report}"]
}
```

### Project File System API

To support file management, we need new capabilities:

```python
class WorkflowFileSystemTool:
    """Tool for managing workflow project files."""
    
    def upload_file(self, project_id: str, file_content: bytes, 
                    destination: str) -> str:
        """
        Upload a file to the project's provisions/inputs folder.
        
        Args:
            project_id: The workflow project ID
            file_content: The file bytes
            destination: Relative path like "specs/my_isa.md" or "trace/my_trace.json"
            
        Returns:
            Full path to the stored file
        """
        project_path = self.get_project_path(project_id)
        full_path = project_path / "provisions" / "inputs" / destination
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_bytes(file_content)
        return str(full_path)
    
    def list_input_files(self, project_id: str) -> dict:
        """
        List all input files in a project.
        
        Returns:
            {
                "specs": ["isa_v1.md", "uarch_v2.md"],
                "trace": ["rtl_trace.json"]
            }
        """
        pass
    
    def read_input_file(self, project_id: str, file_path: str) -> str:
        """Read an input file's content."""
        pass
    
    def update_inputs_json(self, project_id: str, updates: dict):
        """Update inputs.json with new values/paths."""
        pass
```

### Session-Scoped vs Project-Scoped Storage

Two options for where uploaded files go:

**Option A: Session-Scoped (Temporary)**
```
/sessions/abc123/uploads/
├── my_trace.json
└── my_spec.md
```
- Pros: Clean up after session ends, no project modification
- Cons: Files don't persist, can't be reused

**Option B: Project-Scoped (Persistent)**
```
rtl_aoc_project_v2/
└── provisions/inputs/
    ├── specs/
    │   └── my_isa.md        ← User's file added here
    └── trace/
        └── my_trace.json    ← User's file added here
```
- Pros: Files persist, can be reused, natural project organization
- Cons: Modifies project, needs cleanup strategy

**Recommended: Hybrid**
- Default: Session-scoped (temporary)
- User can explicitly "save to project" to make persistent
- Session ends → temp files cleaned up, but user's saved files remain

### File Upload UI Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ [Chat Panel]                                                    │
│                                                                 │
│ User: I want to verify this trace                               │
│ [📎 Attach] my_simulation.json (uploaded)                       │
│                                                                 │
│ Assistant: I see you've uploaded a trace file. Which workflow   │
│ would you like to use?                                          │
│ • RTL AOC Verification (recommended for this file type)         │
│ • Custom verification flow                                      │
│                                                                 │
│ User: Use RTL AOC                                                │
│                                                                 │
│ Assistant: Running RTL AOC Verification with your trace...      │
│ [Progress indicator]                                            │
│ Phase 1: Using existing AOC definitions                         │
│ Phase 2: Verifying 150 cycles... ████████░░ 80%                 │
│                                                                 │
│ Assistant: Verification complete!                               │
│ ✅ 148 cycles passed                                            │
│ ⚠️  2 cycles with warnings (cycles 45, 89)                      │
│ [📄 View Full Report] [💾 Save to Project]                      │
└─────────────────────────────────────────────────────────────────┘
```

### Conversation State

The assistant maintains state across messages:

```json
{
  "session_id": "abc123",
  "uploaded_files": {
    "trace.json": "/uploads/abc123/trace.json",
    "isa_spec.md": "/uploads/abc123/isa_spec.md"
  },
  "extracted_values": {
    "{AOC definitions}": "...from previous message..."
  },
  "workflow_context": {
    "last_workflow": "rtl_aoc_v2",
    "last_result": "..."
  }
}
```

---

---

## Part 4: Generic Tool Injection Architecture

### Current Tool Categories

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         TOOL ARCHITECTURE                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────────────┐     ┌──────────────────────────┐          │
│  │   INDEPENDENT TOOLS      │     │   CANVAS-INTEGRATED TOOLS│          │
│  │                          │     │                          │          │
│  │  Created via ToolFactory │     │  Created via CanvasToolSet│         │
│  │  - LLM                   │     │  - ChatTool              │          │
│  │  - FileSystem            │     │  - CanvasTool            │          │
│  │  - PythonInterpreter     │     │  - UserInputTool         │          │
│  │  - Paradigm              │     │  - ParserTool            │          │
│  │                          │     │                          │          │
│  │  Dependencies:           │     │  Dependencies:           │          │
│  │  - Config/settings only  │     │  - emit_callback         │          │
│  │                          │     │  - execution_getter      │          │
│  │                          │     │  - service imports       │          │
│  └──────────────────────────┘     └──────────────────────────┘          │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### The Problem: Ad-Hoc Context Passing

Current canvas-integrated tools get context through different mechanisms:
- `emit_callback` passed as constructor parameter
- `execution_getter` passed as constructor parameter  
- Services accessed via imports (`from services.project_service import project_service`)

This makes it hard to:
1. Add new canvas-integrated tools (what context do they need?)
2. Test tools in isolation (need to mock imports)
3. Share state between tools (each imports separately)

### Proposed: `CanvasAppContext` Pattern

```python
@dataclass
class CanvasAppContext:
    """
    Unified context available to all canvas-integrated tools.
    
    This is the "app context" that contains references to all
    services and callbacks that tools might need.
    """
    # Core callbacks
    emit_callback: Callable[[str, Dict], None]
    emit_threadsafe: Callable[[str, Dict], None]
    
    # Execution access
    execution_getter: Callable[[], Optional["ExecutionController"]]
    execution_registry: "ExecutionControllerRegistry"
    
    # Services
    project_service: "ProjectService"
    graph_service: "GraphService"
    chat_service: "ChatControllerService"
    
    # NEW: Workflow system
    workflow_registry: Optional["WorkflowRegistry"] = None
    workflow_executor: Optional["WorkflowExecutor"] = None
    
    # File management
    file_upload_service: Optional["FileUploadService"] = None
    
    # Session state
    session_id: Optional[str] = None
    session_state: Dict[str, Any] = field(default_factory=dict)
```

### Base Class for Canvas-Integrated Tools

```python
class CanvasIntegratedTool(ABC):
    """
    Base class for tools that need Canvas App context.
    
    Subclasses declare their dependencies and get them from context.
    """
    
    # Declare what this tool needs from context
    REQUIRED_DEPS: List[str] = []  # e.g., ["emit_callback", "execution_getter"]
    OPTIONAL_DEPS: List[str] = []  # e.g., ["workflow_registry"]
    
    def __init__(self, context: CanvasAppContext):
        self._context = context
        self._validate_dependencies()
    
    def _validate_dependencies(self):
        """Ensure required dependencies are available."""
        for dep in self.REQUIRED_DEPS:
            if getattr(self._context, dep, None) is None:
                raise ValueError(f"{self.__class__.__name__} requires '{dep}' in context")
    
    # Convenient accessors
    def _emit(self, event_type: str, data: Dict):
        if self._context.emit_callback:
            self._context.emit_callback(event_type, data)
    
    def _get_execution_controller(self) -> Optional["ExecutionController"]:
        if self._context.execution_getter:
            return self._context.execution_getter()
        return None
```

### Refactored Tools

```python
class CanvasChatTool(CanvasIntegratedTool):
    """Chat tool with explicit dependencies."""
    
    REQUIRED_DEPS = ["emit_callback"]
    
    def read_message(self) -> str:
        # Use context
        ...
    
    def write_message(self, message: str):
        self._emit("chat:message", {"content": message})


class CanvasDisplayTool(CanvasIntegratedTool):
    """Canvas display/query tool with explicit dependencies."""
    
    REQUIRED_DEPS = ["emit_callback", "execution_getter"]
    OPTIONAL_DEPS = ["project_service", "graph_service"]
    
    def get_project_info(self) -> Dict:
        controller = self._get_execution_controller()
        project_service = self._context.project_service
        ...


class WorkflowExecutorTool(CanvasIntegratedTool):
    """NEW: Workflow execution tool."""
    
    REQUIRED_DEPS = ["execution_registry", "workflow_registry"]
    OPTIONAL_DEPS = ["emit_callback", "file_upload_service"]
    
    def list_workflows(self) -> List[WorkflowMetadata]:
        return self._context.workflow_registry.list_all()
    
    def execute(self, config: WorkflowConfig) -> WorkflowResult:
        # Load project
        project_path = self._context.workflow_registry.get_path(config.workflow_id)
        
        # Create controller
        controller = ExecutionController(project_path)
        
        # Inject values (both file and concept level)
        self._inject_values(controller, config)
        
        # Execute
        controller.start_execution(targets=config.targets)
        
        # Return results
        return self._extract_results(controller, config.targets)
```

### Generic Tool Set Creation

```python
class CanvasToolSet:
    """
    Container for canvas-integrated tools.
    
    Automatically creates tools based on registered tool classes.
    """
    
    # Tool registry: tool_name -> (tool_class, is_optional)
    TOOL_REGISTRY = {
        "chat": (CanvasChatTool, False),
        "canvas": (CanvasDisplayTool, False),
        "user_input": (CanvasUserInputTool, False),
        "parser": (CanvasParserTool, False),
        "workflow": (WorkflowExecutorTool, True),  # Optional, only if workflow registry available
    }
    
    def __init__(self, context: CanvasAppContext):
        self._context = context
        self._tools: Dict[str, CanvasIntegratedTool] = {}
        self._create_tools()
    
    def _create_tools(self):
        """Create all registered tools that have their dependencies available."""
        for name, (tool_class, is_optional) in self.TOOL_REGISTRY.items():
            try:
                self._tools[name] = tool_class(self._context)
            except ValueError as e:
                if is_optional:
                    logger.debug(f"Optional tool '{name}' not created: {e}")
                else:
                    raise
    
    def inject_into_body(self, body: Any):
        """Inject all created tools into a Body instance."""
        for name, tool in self._tools.items():
            setattr(body, name, tool)
    
    def get_tool(self, name: str) -> Optional[CanvasIntegratedTool]:
        return self._tools.get(name)
    
    @classmethod
    def register_tool(cls, name: str, tool_class: Type[CanvasIntegratedTool], optional: bool = True):
        """Register a new tool type (for extensions)."""
        cls.TOOL_REGISTRY[name] = (tool_class, optional)
```

### Benefits of This Pattern

| Aspect | Before | After |
|--------|--------|-------|
| **Adding new tool** | Pass specific params, import services | Declare deps, receive context |
| **Testing** | Mock imports | Mock context object |
| **Dependency visibility** | Hidden in code | Declared in `REQUIRED_DEPS` |
| **Optional features** | Hard to make graceful | `OPTIONAL_DEPS` + try/except |
| **Sharing state** | Reimport singletons | Share via context |

### Integration with WorkflowAssistant

The Workflow Assistant built-in project would use tools that all receive the same context:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    WORKFLOW ASSISTANT PLAN                               │
│                                                                          │
│  ┌─────────────┐   ┌───────────────┐   ┌───────────────────────────┐   │
│  │  ChatTool   │   │ WorkflowTool  │   │   CanvasTool              │   │
│  │  (read msg) │   │ (execute)     │   │   (display results)       │   │
│  └──────┬──────┘   └───────┬───────┘   └─────────────┬─────────────┘   │
│         │                  │                         │                  │
│         └──────────────────┴─────────────────────────┘                  │
│                            │                                            │
│                   ┌────────▼────────┐                                   │
│                   │ CanvasAppContext│                                   │
│                   │ - emit_callback │                                   │
│                   │ - exec_getter   │                                   │
│                   │ - workflow_reg  │                                   │
│                   │ - file_upload   │                                   │
│                   └─────────────────┘                                   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

All tools share the same context, so:
- ChatTool can read messages
- WorkflowTool can discover and execute workflows
- CanvasTool can display results
- All use the same `emit_callback` for WebSocket events
- All can access `workflow_registry` for available workflows

---

## Implementation Roadmap (Updated)

### Phase A: Core Execution Changes (1-2 days)
- [ ] Add output-has-data check in orchestrator
- [ ] Add 'provided' completion detail
- [ ] Test with RTL AOC workflow manually

### Phase B: Workflow Registry (2-3 days)
- [ ] Create WorkflowRegistryTool
- [ ] Extract metadata from projects (entry points, outputs)
- [ ] API endpoint: `GET /api/workflows`

### Phase C: Workflow Executor (3-4 days)
- [ ] Create WorkflowExecutorTool
- [ ] Implement Level 1: File injection (update inputs.json paths)
- [ ] Implement Level 2: Concept injection (direct value injection)
- [ ] Implement flexible exit (targets parameter)
- [ ] API endpoint: `POST /api/workflows/{id}/execute`

### Phase D: Workflow File System (2-3 days)
- [ ] Create WorkflowFileSystemTool
- [ ] Session-scoped upload storage
- [ ] Project file listing and reading
- [ ] "Save to project" persistence option
- [ ] API endpoints: `POST /api/workflows/{id}/files`, `GET /api/workflows/{id}/files`

### Phase E: Workflow Assistant Project (1 week)
- [ ] Create paradigms (discover, match, execute, file upload)
- [ ] Create prompts for intent matching
- [ ] Build workflow_assistant NormCode plan
- [ ] File attachment handling in chat
- [ ] Test end-to-end flow

---

## Related Documents

- [NormCode Execution Documentation](../../../documentation/current/3_execution/README.md)
- [Canvas App Tools Documentation](../../../documentation/current/5_tools/README.md)
- [Compilation Pipeline](../../../documentation/current/4_compilation/README.md)
- [Canvas Assistant](../../../canvas_app/built_in_projects/canvas_assistant/README.md)

---

**Status**: Design Document  
**Created**: January 2026  
**Author**: Discussion between User and Claude

