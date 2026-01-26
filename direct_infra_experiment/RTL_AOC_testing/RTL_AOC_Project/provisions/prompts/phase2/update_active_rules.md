# Update Active Rules

Update the set of active AOC rules based on the current cycle's events.

## Input Data

<current_cycle_trace>
$input_1
</current_cycle_trace>

<previous_active_rules>
$input_2
</previous_active_rules>

<aoc_definitions>
$input_3
</aoc_definitions>

## Task

Process the current cycle and update the active rules:

1. **Check for new triggers**: If an event matches an AOC rule's trigger, create a new active instance
2. **Check for obligations met**: If an active rule's obligation is satisfied, mark it SATISFIED
3. **Check for aborts**: If an abort condition occurs, mark affected rules CANCELLED
4. **Check for timeouts**: If deadline exceeded, mark as VIOLATED
5. **Carry forward**: Pending rules continue to next cycle

## Active Rule Instance Structure

```json
{
  "rule_id": "C001_InstrResolution",
  "instance_id": "C001_42",
  "start_cycle": 100,
  "deadline": 10100,
  "status": "PENDING",
  "context": {"iid": "0x42"}
}
```

## Status Values

- `PENDING`: Waiting for obligation or abort
- `SATISFIED`: Obligation met
- `VIOLATED`: Timeout or forbidden event
- `CANCELLED`: Valid abort occurred

## Output Format

Return JSON with `thinking` and `result` fields:
```json
{
  "thinking": "Your analysis - which triggers fired, which obligations were met, etc.",
  "result": {
    "rules": [...],
    "pending": [...],
    "triggered": [...],
    "completed": [...]
  }
}
```

**Important:** Your response MUST be valid JSON with exactly these two top-level keys: `thinking` and `result`.
