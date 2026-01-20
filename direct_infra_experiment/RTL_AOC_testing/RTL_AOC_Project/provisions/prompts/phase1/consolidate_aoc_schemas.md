# Consolidate AOC Schemas

Clean up and consolidate all extracted AOC schemas into a unified definition.

## Input

You will receive:
- **AOC Schemas Extracted So Far**: List of all individual AOC canonicals

## Task

1. **Remove duplicates**: Merge any overlapping canonicals
2. **Resolve conflicts**: If canonicals contradict, flag for review
3. **Normalize IDs**: Ensure consistent naming (C001, C002, ...)
4. **Add metadata**: Version, extraction date, source references
5. **Validate completeness**: Check all intent types are covered

## Output Format

Return JSON:
```json
{
  "version": "1.0",
  "extracted_date": "2026-01-20",
  "rules": [
    {
      "id": "C001_InstrResolution",
      "trigger": {...},
      "obligation": {...},
      "timing": {...},
      "abort": {...}
    },
    ...
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
```

## Quality Checks

- [ ] No duplicate triggers
- [ ] All obligations are testable
- [ ] Timing constraints are bounded
- [ ] Abort conditions are well-defined

