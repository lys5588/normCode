# Judge Session Termination

Determine if the user wants to end the chat session.

## Current Message

<current_message>
$input_1
</current_message>

## Conversation History

<conversation_history>
$input_2
</conversation_history>

## Task

Analyze the user's current message to determine if they want to end the session.

## Termination Indicators

**Strong indicators (should end)**:
- "bye", "goodbye", "see you", "exit", "quit", "close", "end session"
- "that's all", "I'm done", "nothing else", "all good"
- "thanks, bye", "thank you, goodbye"

**Weak indicators (probably continue)**:
- "thanks" alone (might be mid-conversation gratitude)
- "ok" (acknowledgment, not termination)
- "got it" (understanding, not leaving)

**Not termination indicators**:
- Questions about the canvas
- Commands to execute
- Requests for help
- Conversational messages

## Output Format

Return JSON with `thinking` and `result` fields:

```json
{
  "thinking": "Your analysis of termination intent...",
  "result": true
}
```

### Result Field

- `result` (required): Boolean `true` if session should end, `false` if it should continue

**IMPORTANT**: `result` must be a boolean (`true` or `false`), NOT a string.

### Examples

**User says "bye"**:
```json
{
  "thinking": "The user said 'bye', which is a clear termination indicator.",
  "result": true
}
```

**User says "thanks, that's all I needed"**:
```json
{
  "thinking": "User is expressing gratitude and indicating they're done.",
  "result": true
}
```

**User says "thanks! now zoom in"**:
```json
{
  "thinking": "User said thanks but immediately followed with another command. They want to continue.",
  "result": false
}
```

**User says "ok"**:
```json
{
  "thinking": "Just an acknowledgment, not a termination signal. Continue the session.",
  "result": false
}
```

**User says "how do I run the plan?"**:
```json
{
  "thinking": "User is asking a question. They want to continue interacting.",
  "result": false
}
```

**User says "exit"**:
```json
{
  "thinking": "Clear termination command.",
  "result": true
}
```

**IMPORTANT**: Your response MUST be valid JSON with exactly the `thinking` and `result` keys. The `result` MUST be a boolean.

