# Canvas Assistant - Gap Analysis

This document identifies gaps between the current Canvas Assistant implementation and the new **Canvas Integration Tool** architecture (three-perspective interface).

---

## Summary

| Area | Current State | Required State | Priority |
|------|---------------|----------------|----------|
| **Schema** | Flat command types | Perspective-organized commands | 🔴 High |
| **Prompts** | Old vocabulary | New perspective-based vocabulary | 🔴 High |
| **Agent Config** | Legacy tool config | Canvas Integration Tool config | 🟡 Medium |
| **README** | References old tools | References new architecture | 🟢 Low |

---

## 1. Schema Gaps (`provisions/schemas/canvas_commands.json`)

### 1.1 Missing Commands

The current schema is missing these commands from the new architecture:

#### Structure Commands (NEW)
| Command | Description | Maps to |
|---------|-------------|---------|
| `collapse_node` | Collapse a node (hide descendants) | `me.hands.collapse_node()` |
| `expand_node` | Expand a collapsed node | `me.hands.expand_node()` |
| `toggle_collapse` | Toggle collapse state | `me.hands.toggle_collapse()` |
| `collapse_all` | Collapse all parent nodes | `me.hands.collapse_all()` |
| `expand_all` | Expand all collapsed nodes | `me.hands.expand_all()` |
| `collapse_to_level` | Collapse to specific depth | `me.hands.collapse_to_level()` |

#### Highlight Commands (NEW)
| Command | Description | Maps to |
|---------|-------------|---------|
| `highlight_branch` | Highlight ancestors + descendants | `me.hands.highlight_branch()` |
| `clear_highlight` | Clear branch highlighting | `me.hands.clear_highlight()` |

#### Selection Commands (UPDATED)
| Command | Description | Maps to |
|---------|-------------|---------|
| `select_nodes` | Select multiple nodes | `me.hands.select_nodes()` |
| `deselect_all` | Clear all selections | `me.hands.deselect_all()` |

#### Panel Commands (NEW)
| Command | Description | Maps to |
|---------|-------------|---------|
| `open_panel` | Open a panel (chat, agent, log, etc.) | `me.hands.open_panel()` |
| `close_panel` | Close a panel | `me.hands.close_panel()` |
| `toggle_panel` | Toggle panel visibility | `me.hands.toggle_panel()` |
| `focus_panel` | Focus a panel | `me.hands.focus_panel()` |

#### Chat Action Commands (NEW)
| Command | Description | Maps to |
|---------|-------------|---------|
| `type_in_chat` | Type text in chat input | `me.hands.type_in_chat()` |
| `clear_chat_input` | Clear chat input field | `me.hands.clear_chat_input()` |
| `send_chat_message` | Send current chat input | `me.hands.send_chat_message()` |
| `respond_to_prompt` | Respond to pending input request | `me.hands.respond_to_prompt()` |
| `select_prompt_option` | Select from prompt options | `me.hands.select_prompt_option()` |

#### Node Interaction Commands (NEW)
| Command | Description | Maps to |
|---------|-------------|---------|
| `double_click_node` | Double-click node (open details) | `me.hands.double_click_node()` |
| `right_click_node` | Right-click node (context menu) | `me.hands.right_click_node()` |
| `hover_node` | Hover over node (tooltip) | `me.hands.hover_node()` |
| `drag_node` | Drag node to position | `me.hands.drag_node()` |

#### Keyboard Commands (NEW)
| Command | Description | Maps to |
|---------|-------------|---------|
| `click_button` | Click UI button by ID | `me.hands.click_button()` |
| `press_key` | Press keyboard key | `me.hands.press_key()` |
| `keyboard_shortcut` | Execute keyboard shortcut | `me.hands.keyboard_shortcut()` |

### 1.2 Missing Perspective Organization

Current schema has flat structure. New architecture organizes by perspective:

```
CURRENT:                          NEW:
─────────────────                 ─────────────────
type: "select_node"               perspective: "first_person"
type: "zoom_in"                   faculty: "hands"
type: "query_value"               action: "click_node"
                                  
                                  OR for queries:
                                  perspective: "first_person"
                                  faculty: "vision"
                                  action: "get_canvas"
```

**Recommendation**: Add `perspective` and `faculty` fields to schema, or maintain command mapping table.

### 1.3 Command Mapping Table Needed

```json
{
  "command_mappings": {
    "select_node": { "perspective": "me", "faculty": "hands", "method": "click_node" },
    "zoom_in": { "perspective": "me", "faculty": "hands", "method": "zoom_in" },
    "query_value": { "perspective": "me", "faculty": "mind", "method": "get_concept_value" },
    "query_execution": { "perspective": "me", "faculty": "vision", "method": "get_execution" },
    ...
  }
}
```

---

## 2. Prompt Gaps

### 2.1 `classify_command.md` - Major Update Needed

**Current Issues:**
- Uses old command vocabulary (`select_node`, `query_project`)
- No awareness of three perspectives
- Doesn't explain the me/you/it distinction

**Required Updates:**

1. **Add perspective awareness section:**
```markdown
## Perspective Mapping

Commands map to three perspectives:

### First Person (`me.*`) - User sees the effect
- **Vision** (queries): get_canvas, get_execution, get_node_details
- **Hands** (actions): click_node, collapse_node, zoom_in, open_panel
- **Mind** (control): run, pause, step, get_concept_value

### Second Person (`you.*`) - Private tool access
- files.read(), blackboard.get(), parser.parse()
- code.run(), llm.call(), prompt.substitute()

### Third Person (`it.*`) - Activity observation
- events.recent(), activity.timeline()
```

2. **Update command categories to match faculties:**
```markdown
### me.hands Actions (User sees)
- select_node → me.hands.click_node()
- collapse_node → me.hands.collapse_node()
- open_panel → me.hands.open_panel()
- ...

### me.vision Queries (User sees)
- query_graph → me.vision.get_canvas()
- query_execution → me.vision.get_execution()
- ...

### me.mind Control (User sees)
- run → me.mind.run()
- pause → me.mind.pause()
- ...
```

3. **Add new command examples:**
```markdown
**User**: "Collapse the entire graph"
{
  "type": "collapse_all",
  "perspective": "me",
  "faculty": "hands",
  "params": {},
  "confidence": 0.95
}

**User**: "Open the agent panel"
{
  "type": "open_panel",
  "perspective": "me",
  "faculty": "hands",
  "params": { "panel": "agent" },
  "confidence": 0.98
}

**User**: "Highlight the branch containing node 1.3"
{
  "type": "highlight_branch",
  "perspective": "me",
  "faculty": "hands",
  "params": { "node_id": "1.3" },
  "confidence": 0.92
}
```

### 2.2 `generate_response.md` - Minor Update Needed

**Current Issues:**
- References may not align with new command vocabulary

**Required Updates:**
- Update example commands to use new vocabulary
- Add examples for new command types (collapse, panel, highlight)

### 2.3 `judge_terminate.md` - No Changes Needed

This prompt handles session termination logic which is independent of the command architecture.

---

## 3. Agent Config Gaps (`compiler.agent.json`)

### 3.1 Current Structure

```json
{
  "tools": {
    "llm": { "model": "qwen-plus" },
    "paradigm": { "dir": "provisions/paradigms" },
    "file_system": { "enabled": true },
    "python_interpreter": { "enabled": false },
    "user_input": { "enabled": true }
  }
}
```

### 3.2 Required Structure

Add `canvas_integration` tool configuration:

```json
{
  "tools": {
    "llm": { "model": "qwen-plus" },
    "paradigm": { "dir": "provisions/paradigms" },
    "file_system": { "enabled": true },
    "python_interpreter": { "enabled": false },
    "user_input": { "enabled": true },
    "canvas_integration": {
      "enabled": true,
      "perspectives": {
        "first_person": true,   // me.* - Vision, Hands, Mind
        "second_person": true,  // you.* - Direct tool access
        "third_person": true    // it.* - Activity observation
      }
    }
  }
}
```

---

## 4. README Gaps

### 4.1 Current References

```markdown
1. Reads user input via **ChatTool** 
2. Can execute canvas commands via **CanvasDisplayTool**
```

### 4.2 Required Updates

```markdown
1. Reads user input via **CanvasIntegrationTool** (`me.vision.get_chat()`)
2. Can execute canvas commands via **CanvasIntegrationTool** (`me.hands.*`)
3. Queries state via **CanvasIntegrationTool** (`me.vision.*`, `me.mind.*`)
4. Uses private tools via **CanvasIntegrationTool** (`you.*`)
```

---

## 5. Action Items

### Phase 1: Schema Update (High Priority)

- [ ] Add missing commands to `canvas_commands.json`:
  - [ ] Structure commands (collapse/expand/highlight)
  - [ ] Panel commands
  - [ ] Chat action commands
  - [ ] Node interaction commands
  - [ ] Keyboard commands
- [ ] Add `command_mappings` section mapping to perspectives/faculties
- [ ] Update `help_text` with new command categories

### Phase 2: Prompt Updates (High Priority)

- [ ] Update `classify_command.md`:
  - [ ] Add perspective mapping section
  - [ ] Update command categories to match faculties
  - [ ] Add examples for all new commands
  - [ ] Update output format to include perspective/faculty
- [ ] Update `generate_response.md`:
  - [ ] Add examples for new command responses

### Phase 3: Agent Config Update (Medium Priority)

- [ ] Add `canvas_integration` tool config to `compiler.agent.json`
- [ ] Consider perspective-specific agent profiles

### Phase 4: Documentation Update (Low Priority)

- [ ] Update `README.md` with new architecture references
- [ ] Add diagram showing perspective-based interaction

---

## 6. Command Vocabulary Mapping (Reference)

| Old Command | New Method | Perspective | Faculty |
|-------------|------------|-------------|---------|
| `select_node` | `click_node` | me | hands |
| `zoom_in` | `zoom_in` | me | hands |
| `zoom_out` | `zoom_out` | me | hands |
| `fit_view` | `fit_view` | me | hands |
| `center_on` | `center_on_node` | me | hands |
| `run` | `run` | me | mind |
| `step` | `step` | me | mind |
| `pause` | `pause` | me | mind |
| `stop` | `stop` | me | mind |
| `set_breakpoint` | `add_breakpoint` | me | hands |
| `clear_breakpoint` | `remove_breakpoint` | me | hands |
| `query_project` | `get_project` | me | vision |
| `query_execution` | `get_execution` | me | vision |
| `query_graph` | `get_canvas` | me | vision |
| `query_value` | `get_concept_value` | me | mind |
| `query_node` | `get_node_details` | me | vision |
| `query_logs` | `get_logs` | me | vision |
| --- NEW --- | | | |
| `collapse_node` | `collapse_node` | me | hands |
| `expand_node` | `expand_node` | me | hands |
| `collapse_all` | `collapse_all` | me | hands |
| `expand_all` | `expand_all` | me | hands |
| `highlight_branch` | `highlight_branch` | me | hands |
| `clear_highlight` | `clear_highlight` | me | hands |
| `open_panel` | `open_panel` | me | hands |
| `close_panel` | `close_panel` | me | hands |
| `toggle_panel` | `toggle_panel` | me | hands |

---

## 7. Notes

- The three-perspective design provides clearer semantics:
  - **me.*** = User will see the effect (shared stage)
  - **you.*** = User won't see (private tool access)
  - **it.*** = Activity observation (meta-level)

- The Canvas Assistant primarily uses **First Person** perspective since it interacts with the user through the shared UI.

- **Second Person** tools (`you.*`) can be used for background operations like reading files, calling LLMs, etc. without affecting the visible UI state.

- Commands classified as `chat` remain conversational and don't map to canvas operations.

---

*Generated: 2026-01-25*
*Reference: canvas_app/backend/canvas_integration/docs/*

