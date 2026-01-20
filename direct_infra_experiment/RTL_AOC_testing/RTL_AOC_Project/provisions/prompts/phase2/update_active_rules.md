# Update Active Rules

Update the set of active AOC rules based on the current cycle's events.

## Input

You will receive:
1. **Current Cycle Trace**: Events that occurred in this cycle
2. **Previous Active Rules**: Active rule instances from prior cycle
3. **AOC Definitions**: The static set of all AOC rules

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

Return JSON:
```json
{
  "rules": [...],
  "pending": [...],
  "triggered": [...],
  "completed": [...]
}
```

