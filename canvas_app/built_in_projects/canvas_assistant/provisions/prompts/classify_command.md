# Classify User Message as Canvas Command

You are an assistant that interprets user messages and classifies them as canvas commands.

## User Message

<user_message>
$input_1
</user_message>

## Available Commands Schema

<command_schema>
$input_2
</command_schema>

## Conversation Context (v2.0)

<context_summary>
$input_3
</context_summary>

## Task

Analyze the user message and determine:
1. What canvas operation they want to perform
2. Extract any parameters mentioned
3. Assess confidence in your interpretation

## Command Categories

### Navigation Commands
- `zoom_in`, `zoom_out`, `zoom_to` - Adjust view zoom
- `pan` - Move the view
- `fit_view` - Fit all nodes in viewport
- `center_on_node` - Focus on specific node

### Selection Commands
- `click_node`, `select_nodes` - Select nodes
- `deselect_all` - Clear selections

### Structure Commands
- `collapse_node`, `expand_node`, `toggle_collapse` - Node collapse state
- `collapse_all`, `expand_all`, `collapse_to_level` - Bulk collapse
- `highlight_branch`, `clear_highlight` - Branch highlighting

### Execution Commands
- `run`, `step`, `pause`, `stop` - Execution control
- `add_breakpoint`, `remove_breakpoint`, `clear_all_breakpoints` - Breakpoints

### Panel Commands
- `open_panel`, `close_panel`, `toggle_panel`, `focus_panel` - Panel management

### Query Commands
- `query_project`, `query_execution`, `query_graph` - State queries
- `query_value`, `query_node`, `query_logs` - Data queries

### Chat Commands
- `chat` - Conversational message (no canvas action needed)

## Output Format

Return JSON with `thinking` and `result` fields:

```json
{
  "thinking": "Your analysis of what the user wants...",
  "result": {
    "type": "command_type",
    "params": {
      "param1": "value1"
    },
    "confidence": 0.95
  }
}
```

### Result Fields

- `type` (required): The command type from the schema, or `"chat"` for conversational messages
- `params` (required): Object with command parameters, or `{}` if none
- `confidence` (required): Number 0-1 indicating interpretation confidence

### Examples

**User**: "zoom in a bit"
```json
{
  "thinking": "User wants to zoom in on the canvas view.",
  "result": {
    "type": "zoom_in",
    "params": {"amount": 0.1},
    "confidence": 0.98
  }
}
```

**User**: "show me node 1.3"
```json
{
  "thinking": "User wants to focus on a specific node. I'll center the view on it.",
  "result": {
    "type": "center_on_node",
    "params": {"node_id": "1.3"},
    "confidence": 0.92
  }
}
```

**User**: "hello, how are you?"
```json
{
  "thinking": "This is a conversational greeting, not a canvas command.",
  "result": {
    "type": "chat",
    "params": {},
    "confidence": 0.99
  }
}
```

**User**: "collapse everything"
```json
{
  "thinking": "User wants to collapse all nodes in the graph.",
  "result": {
    "type": "collapse_all",
    "params": {},
    "confidence": 0.95
  }
}
```

**User**: "run the plan"
```json
{
  "thinking": "User wants to start execution of the loaded plan.",
  "result": {
    "type": "run",
    "params": {},
    "confidence": 0.97
  }
}
```

**IMPORTANT**: Your response MUST be valid JSON with exactly the `thinking` and `result` keys.

