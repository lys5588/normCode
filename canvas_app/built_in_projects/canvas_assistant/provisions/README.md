# Canvas Assistant v2.0 Provisions

Resources for the Canvas Assistant NormCode plan with Canvas Integration Tool support and context-aware processing.

## Directory Structure

```
provisions/
├── prompts/                                    # LLM prompt templates
│   ├── summarize_context.md                    # Distill conversation context (v2.0)
│   ├── classify_command.md                     # Parse user message → command (with context)
│   ├── generate_response.md                    # Generate user-facing response (with context)
│   └── judge_terminate.md                      # Judge if session should end
│
├── schemas/                                    # JSON schemas
│   └── canvas_commands.json                    # Valid canvas command schema
│
├── paradigms/                                  # Execution paradigms
│   ├── c_CanvasIntegrationGetChat-o_Literal.json        # Block & wait for message
│   ├── h_Literal-c_CanvasIntegrationSay-o_LiteralStatus.json      # Permanent chat message
│   ├── h_Literal-c_CanvasIntegrationNotify-o_LiteralStatus.json   # Temporary notification
│   ├── h_Literal-c_CanvasIntegrationExecute-o_LiteralStatus.json  # Execute command
│   └── h_LiteralPath-c_ReadFile-o_Literal.json                    # Read file from path
│
└── README.md                                   # This file
```

## Paradigm Reference

### Canvas Integration Paradigms (v2.0)

| Paradigm | Method | Purpose | Persists in Chat? |
|----------|--------|---------|-------------------|
| `c_CanvasIntegrationGetChat-o_Literal` | `me.vision.wait_for_message()` | Block and wait for user message | N/A |
| `h_Literal-c_CanvasIntegrationSay-o_LiteralStatus` | `me.hands.say()` | Send **permanent** message to user | ✅ Yes |
| `h_Literal-c_CanvasIntegrationNotify-o_LiteralStatus` | `me.hands.notify()` | Send **temporary** notification/status | ❌ No |
| `h_Literal-c_CanvasIntegrationExecute-o_LiteralStatus` | `me.hands.execute_command()` | Execute parsed canvas command | N/A |

### Message Types

**Permanent Messages (`say`):**
- Final assistant responses
- Important information user needs to reference
- Actual conversation content

**Temporary Notifications (`notify`):**
- Status updates: "🔍 Understanding your request..."
- Progress indicators: "⚙️ Executing command..."
- Ephemeral feedback: "💭 Generating response..."
- Context summaries that aren't core conversation

### LLM Paradigms (Standard)

These use the standard LLM paradigms from `infra/_agent/_models/_paradigms/`:

| Paradigm | Purpose |
|----------|---------|
| `v_PromptLocation-h_Literal-c_GenerateThinkJson-o_Literal` | Classify command, generate response, summarize context |
| `v_PromptLocation-h_Literal-c_GenerateThinkJson-o_Boolean` | Judge termination |

## Body Faculties Required

### `canvas_integration` Faculty

The unified Canvas Integration Tool with three perspectives:

```python
canvas = CanvasIntegrationTool(...)

# First Person - user sees
canvas.me.vision.wait_for_message()  # Block for message (NEW)
canvas.me.vision.get_chat()          # Get chat snapshot
canvas.me.hands.say(message)         # Send permanent message
canvas.me.hands.notify(message)      # Send temporary notification (NEW)
canvas.me.hands.status("thinking")   # Convenience status helper (NEW)
canvas.me.hands.execute_command(cmd) # Execute canvas command
canvas.me.hands.click_node(id)       # Canvas actions

# Second Person - user doesn't see
canvas.you.files.read(path)          # Private file access
canvas.you.llm.call(prompt)          # Private LLM call

# Third Person - observe
canvas.it.events.recent()            # Activity observation
```

### Hands Methods Summary

| Method | Purpose | Persists? |
|--------|---------|-----------|
| `say(message)` | Send permanent conversation message | ✅ Yes |
| `notify(message, type)` | Send temporary notification | ❌ No |
| `status(type, message?)` | Convenience for common status types | ❌ No |
| `execute_command(cmd)` | Execute canvas/execution command | N/A |

### `llm` Faculty

Standard language model inference for classification, generation, and judgement.

## Prompt Template Variables

All variables use `$input_x` format wrapped in descriptive XML tags:

```markdown
<xml_tag_name>
$input_x
</xml_tag_name>
```

### `summarize_context.md` (v2.0 - NEW)
| Variable | XML Tag | Description |
|----------|---------|-------------|
| `$input_1` | `<conversation_history>` | Packed list of messages |
| **Output** | - | `{key_points: [], last_actions: [], user_intent: str}` |

### `classify_command.md` (with context)
| Variable | XML Tag | Description |
|----------|---------|-------------|
| `$input_1` | `<user_message>` | User message text |
| `$input_2` | `<command_schema>` | Command schema JSON |
| `$input_3` | `<context_summary>` | Context from summarize_context |

### `generate_response.md` (with context)
| Variable | XML Tag | Description |
|----------|---------|-------------|
| `$input_1` | `<user_message>` | User message |
| `$input_2` | `<command_result>` | Command execution status |
| `$input_3` | `<context_summary>` | Context for coherent replies |

### `judge_terminate.md`
| Variable | XML Tag | Description |
|----------|---------|-------------|
| `$input_1` | `<current_message>` | Current user message |
| `$input_2` | `<conversation_history>` | Packed list of messages |

## Output Format Requirements

All prompts using `c_GenerateThinkJson` MUST specify:

```markdown
## Output Format

Return JSON with `thinking` and `result` fields:
```json
{
  "thinking": "Your analysis...",
  "result": { /* actual output */ }
}
```

For judgements, `result` should be `true` or `false` (boolean, not string).
```

## Usage in _.pf.ncd

```ncd
/: STEP 2: Emit thinking status (TEMPORARY - use notify)
<= ::(emit thinking status to user)
    | %{norm_input}: h_Literal-c_CanvasIntegrationNotify-o_LiteralStatus
    | %{body_faculty}: canvas_integration
    | %{method}: me.hands.notify
    | %{message}: "🔍 Understanding your request..."

/: STEP 3: Summarize conversation context (v2.0)
<= ::(summarize on-going messages for context using {1})
    | %{norm_input}: v_PromptLocation-h_Literal-c_GenerateThinkJson-o_Literal
    | %{v_input_provision}: provisions/prompts/summarize_context.md
    | %{body_faculty}: llm

/: STEP 11: Send FINAL response (PERMANENT - use say)
<= ::(send response to chat using {1})
    | %{norm_input}: h_Literal-c_CanvasIntegrationSay-o_LiteralStatus
    | %{body_faculty}: canvas_integration
    | %{method}: me.hands.say
```
