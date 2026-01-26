# Verify Cycle

Verify the current cycle's trace against active AOC rules.

## Input Data

<current_cycle_trace>
$input_1
</current_cycle_trace>

<active_rules>
$input_2
</active_rules>

## Task

Produce a verification result for this cycle:

1. **Check all active rules**: Are any violated?
2. **Report status**: PASS, FAIL, or PENDING
3. **List violations**: Any rules that transitioned to VIOLATED
4. **Snapshot active rules**: Current state for audit trail

## Output Format

Return JSON with `thinking` and `result` fields:
```json
{
  "thinking": "Your cycle verification analysis...",
  "result": {
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
}
```

Or for a violation:
```json
{
  "thinking": "Found violation during cycle check...",
  "result": {
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
}
```

**Important:** Your response MUST be valid JSON with exactly these two top-level keys: `thinking` and `result`.

## Verification Outcome

- **PASS**: No violations this cycle
- **FAIL**: At least one rule violated
- **PENDING**: Rules still active, no violations yet
