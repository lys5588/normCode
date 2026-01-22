# Validate AOC Rules

Judge whether the generated AOC rules are valid and complete.

## Input Data

<aoc_definitions>
$input_1
</aoc_definitions>

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

Return JSON with `thinking` and `result` fields:
```json
{
  "thinking": "Your validation analysis - checking each rule for required fields, semantic consistency, etc.",
  "result": {
    "valid": true,
    "issues": [],
    "warnings": [
      "Rule C003 has unbounded timing - consider adding max_cycles for verification"
    ]
  }
}
```

Or if invalid:
```json
{
  "thinking": "Found problems during validation...",
  "result": {
    "valid": false,
    "issues": [
      "Rule C002 is missing trigger field",
      "Rules C004 and C005 have conflicting obligations for same trigger"
    ],
    "warnings": []
  }
}
```

**Important:** Your response MUST be valid JSON with exactly these two top-level keys: `thinking` and `result`.
