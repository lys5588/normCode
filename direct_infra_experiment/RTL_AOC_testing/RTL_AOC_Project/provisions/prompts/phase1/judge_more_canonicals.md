# Judge: More Canonicals to Process?

Determine if there are more AOC canonicals to extract from the specification.

## Input

You will receive:
1. **All User Inputs**: Combined ISA spec, MA spec, and intent blocks
2. **Extracted Schemas**: AOC canonicals already extracted

## Task

Judge whether ALL relevant canonicals have been extracted, or if more remain.

## Criteria for Completion

The extraction is COMPLETE (return `true`) when:
- All normative statements ("shall", "must") have been captured
- All trigger-obligation pairs have been identified
- All timing constraints have been documented
- No significant behaviors remain unspecified

The extraction is NOT COMPLETE (return `false`) when:
- There are normative statements not yet captured as canonicals
- There are implicit behaviors that need explicit rules
- There are edge cases or exception handling not yet covered

## Output Format

Return JSON:
```json
{
  "complete": true,
  "reasoning": "All normative statements have been captured as canonicals. The ISA specifies 5 key behaviors, and 5 canonicals have been extracted covering instruction resolution, memory ordering, exception handling, interrupt delivery, and atomic operations."
}
```

Or:
```json
{
  "complete": false,
  "remaining": "The ISA mentions 'precise exceptions' but no canonical covers the ordering requirements for exception delivery."
}
```

## Note

Be thorough but not exhaustive. Focus on architecturally significant behaviors.

