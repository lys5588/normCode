# Judge: More Canonicals to Process?

Determine if there are more AOC canonicals to extract from the specification.

## Input Data

<user_inputs>
$input_1
</user_inputs>

## Task

Judge whether ALL relevant canonicals have been extracted, or if more remain.

Review the specifications and intent blocks above. Consider what AOC canonicals would be needed to fully specify the normative behavior.

## Criteria for Completion

The extraction is COMPLETE (return `true` for "complete") when:
- All normative statements ("shall", "must") have been captured
- All trigger-obligation pairs have been identified
- All timing constraints have been documented
- No significant behaviors remain unspecified

The extraction is NOT COMPLETE (return `false` for "complete") when:
- There are normative statements not yet captured as canonicals
- There are implicit behaviors that need explicit rules
- There are edge cases or exception handling not yet covered

## Output Format

Return JSON with `thinking` and `result` fields:
```json
{
  "thinking": "Your analysis of what's been covered and what might remain...",
  "result": {
    "complete": true,
    "reasoning": "All normative statements have been captured as canonicals. The ISA specifies 5 key behaviors, and 5 canonicals have been extracted covering instruction resolution, memory ordering, exception handling, interrupt delivery, and atomic operations."
  }
}
```

Or if more canonicals remain:
```json
{
  "thinking": "Analyzing spec coverage...",
  "result": {
    "complete": false,
    "remaining": "The ISA mentions 'precise exceptions' but no canonical covers the ordering requirements for exception delivery."
  }
}
```

**Important:** Your response MUST be valid JSON with exactly these two top-level keys: `thinking` and `result`.

## Note

Be thorough but not exhaustive. Focus on architecturally significant behaviors.
