# Extract AOC Canonical

Extract one Action-Obligation Canonical (AOC) rule from the specification.

## Input

You will receive:
1. **All User Inputs**: Combined ISA spec, MA spec, and intent blocks
2. **Previously Extracted Schemas**: AOC canonicals already extracted

## Task

Identify and extract ONE new canonical that has not been extracted yet.

An AOC canonical has:
- **id**: Unique identifier (e.g., "C001_InstrResolution")
- **trigger**: The event that starts the obligation (e.g., instruction issued)
- **obligation**: What must happen (e.g., commit or trap)
- **timing**: Time/ordering constraints (e.g., within 100 cycles)
- **abort**: Events that validly cancel the obligation (e.g., flush)

## Output Format

Return JSON:
```json
{
  "id": "C001_InstrResolution",
  "trigger": {
    "signal": "instr_issued",
    "description": "When an instruction is officially issued to the backend"
  },
  "obligation": {
    "type": "any_of",
    "conditions": [
      {"signal": "commit", "description": "Instruction commits"},
      {"signal": "trap_taken", "description": "Trap is taken"}
    ]
  },
  "timing": {
    "max_cycles": 10000,
    "description": "Liveness timeout for verification"
  },
  "abort": {
    "signal": "flush_event",
    "description": "Microarchitectural flush cancels younger instructions"
  }
}
```

## Guidelines

1. Look for normative language: "shall", "must", "required"
2. Identify action-response pairs
3. Note timing constraints
4. Identify valid cancellation events
5. Don't repeat already-extracted canonicals

