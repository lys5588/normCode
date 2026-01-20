# Validate AOC Rules

Judge whether the generated AOC rules are valid and complete.

## Input

You will receive:
- **AOC Definitions**: The consolidated AOC schema

## Task

Validate the AOC rules for:

1. **Syntactic validity**: Are all required fields present?
2. **Semantic consistency**: Do rules make sense?
3. **Testability**: Can each rule be verified against a trace?
4. **Completeness**: Are there obvious gaps?
5. **No contradictions**: Do any rules conflict?

## Validation Criteria

### Required Fields per Rule
- `id`: Unique identifier
- `trigger`: Non-empty trigger condition
- `obligation`: At least one obligation
- `timing` or `abort`: At least one completion condition

### Semantic Checks
- Trigger and obligation are different events
- Timing constraints are positive numbers
- Abort conditions don't overlap with obligations

### Testability
- Signals are observable in RTL trace
- Conditions can be matched programmatically

## Output Format

Return JSON:
```json
{
  "valid": true,
  "issues": [],
  "warnings": [
    "Rule C003 has unbounded timing - consider adding max_cycles for verification"
  ]
}
```

Or if invalid:
```json
{
  "valid": false,
  "issues": [
    "Rule C002 is missing trigger field",
    "Rules C004 and C005 have conflicting obligations for same trigger"
  ],
  "warnings": []
}
```

