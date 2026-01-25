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
│   ├── c_CanvasIntegration-Vision-GetChat-o_Literal.json
│   ├── c_CanvasIntegration-Hands-Say-o_Status.json
│   └── c_CanvasIntegration-Hands-ExecuteCommand-o_Status.json
│
└── README.md                                   # This file
```

## Paradigm Reference

### Canvas Integration Paradigms (v2.0)

| Paradigm | Perspective | Faculty | Method | Purpose |
|----------|-------------|---------|--------|---------|
| `c_CanvasIntegration-Vision-GetChat-o_Literal` | me | vision | `get_chat()` | Block and wait for user message |
| `c_CanvasIntegration-Hands-Say-o_Status` | me | hands | `say()` | Send message/status to user |
| `c_CanvasIntegration-Hands-ExecuteCommand-o_Status` | me | hands | `*` | Execute parsed canvas command |

### LLM Paradigms (Standard)

These use the standard LLM paradigms from `infra/_agent/_models/_paradigms/`:

| Paradigm | Purpose |
|----------|---------|
| `v_PromptLocation-h_Literal-c_GenerateThinkJson-o_Literal` | Classify command, generate response |
| `v_PromptLocation-h_Literal-c_GenerateThinkJson-o_Boolean` | Judge termination |

## Body Faculties Required

### `canvas_integration` Faculty

The unified Canvas Integration Tool with three perspectives:

```python
canvas = CanvasIntegrationTool(...)

# First Person - user sees
canvas.me.vision.get_chat()      # Block for message
canvas.me.hands.say(message)     # Send message
canvas.me.hands.click_node(id)   # Canvas actions

# Second Person - user doesn't see
canvas.you.files.read(path)      # Private file access
canvas.you.llm.call(prompt)      # Private LLM call

# Third Person - observe
canvas.it.events.recent()        # Activity observation
```

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
/: STEP 3: Summarize conversation context (v2.0)
<= ::(summarize on-going messages for context using {1})
    | %{norm_input}: v_PromptLocation-h_Literal-c_GenerateThinkJson-o_Literal
    | %{v_input_provision}: provisions/prompts/summarize_context.md
    | %{body_faculty}: llm

/: STEP 4: Notify chat with context summary
<= ::(notify chat with context summary using {1})
    | %{norm_input}: c_CanvasIntegration-Hands-Say-o_Status
    | %{body_faculty}: canvas_integration
    | %{method}: me.hands.say
    | %{message_template}: "📋 Context: {context_summary.user_intent}"

/: STEP 5: Classify message with context
<= ::(classify user message as canvas command using {1}, {2}, and {3})
    | %{norm_input}: v_PromptLocation-h_Literal-c_GenerateThinkJson-o_Literal
    | %{v_input_provision}: provisions/prompts/classify_command.md
    | %{body_faculty}: llm
```
