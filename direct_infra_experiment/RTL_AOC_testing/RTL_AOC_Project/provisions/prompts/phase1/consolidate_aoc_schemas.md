# Consolidate AOC Schemas

Clean up and consolidate all extracted AOC schemas into a unified definition.

## Input Data

<extracted_schemas>
$input_1
</extracted_schemas>

**Note:** Ignore any entries with `"__placeholder__": true` - these are system placeholders, not real schemas.

## Task

1. **Filter placeholders**: Remove any entries with `"__placeholder__": true`
2. **Remove duplicates**: Merge any overlapping canonicals
2. **Resolve conflicts**: If canonicals contradict, flag for review
3. **Normalize IDs**: Ensure consistent naming (C001, C002, ...)
4. **Add metadata**: Version, extraction date, source references
5. **Validate completeness**: Check all intent types are covered

## Output Format

Return JSON with `thinking` and `result` fields:
```json
{
  "thinking": "Your consolidation analysis - duplicates found, conflicts resolved, etc.",
  "result": {
    "version": "1.0",
    "extracted_date": "2026-01-22",
    "rules": [
      {
        "id": "C001_InstrResolution",
        "trigger": {...},
        "obligation": {...},
        "timing": {...},
        "abort": {...}
      }
    ],
    "metadata": {
      "total_rules": 5,
      "coverage": {
        "liveness": 2,
        "safety": 1,
        "atomicity": 1,
        "ordering": 1
      },
      "sources": ["ISA v1", "uarch v2"]
    }
  }
}
```

**Important:** Your response MUST be valid JSON with exactly these two top-level keys: `thinking` and `result`.

## Quality Checks

- [ ] No duplicate triggers
- [ ] All obligations are testable
- [ ] Timing constraints are bounded
- [ ] Abort conditions are well-defined
