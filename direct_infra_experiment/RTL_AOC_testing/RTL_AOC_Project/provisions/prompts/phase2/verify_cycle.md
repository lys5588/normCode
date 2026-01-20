# Verify Cycle

Verify the current cycle's trace against active AOC rules.

## Input

You will receive:
1. **Current Cycle Trace**: Events that occurred in this cycle
2. **Active Rules**: Current set of active rule instances with their status

## Task

Produce a verification result for this cycle:

1. **Check all active rules**: Are any violated?
2. **Report status**: PASS, FAIL, or PENDING
3. **List violations**: Any rules that transitioned to VIOLATED
4. **Snapshot active rules**: Current state for audit trail

## Output Format

Return JSON:
```json
{
  "cycle_num": 100,
  "status": "PASS",
  "violations": [],
  "active_rules": [
    {
      "rule_id": "C001_InstrResolution",
      "instance_id": "C001_42",
      "status": "PENDING",
      "cycles_remaining": 50
    }
  ],
  "events_processed": 3
}
```

Or for a violation:
```json
{
  "cycle_num": 10100,
  "status": "FAIL",
  "violations": [
    {
      "rule_id": "C001_InstrResolution",
      "instance_id": "C001_42",
      "type": "TIMEOUT",
      "description": "Instruction 0x42 did not commit or trap within 10000 cycles"
    }
  ],
  "active_rules": [...],
  "events_processed": 2
}
```

## Verification Outcome

- **PASS**: No violations this cycle
- **FAIL**: At least one rule violated
- **PENDING**: Rules still active, no violations yet

