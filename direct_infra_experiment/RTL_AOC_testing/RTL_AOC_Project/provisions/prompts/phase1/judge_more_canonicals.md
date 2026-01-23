# Judge: More Canonicals to Process?

Determine if there are more AOC canonicals to extract from the specification.

## Input Data

### Original Specifications
<user_inputs>
$input_1
</user_inputs>

### Previously Extracted Canonicals
<extracted_schemas>
$input_2
</extracted_schemas>

**Note:** Ignore any entries with `"__placeholder__": true` - these are system placeholders, not real schemas.

## Task

Judge whether ALL relevant canonicals have been extracted, or if more remain.

**Compare** the extracted canonicals against the original specifications. Identify any normative statements ("shall", "must") that have NOT yet been captured.

## Criteria for Completion

**Return `complete: true` when ANY of these conditions are met:**

1. **All normative statements covered**: Each "shall"/"must" in the spec has a corresponding canonical
2. **Sufficient coverage**: 5-10 unique canonicals typically cover a complete ISA/uArch spec
3. **Duplicates detected**: If the extracted list contains duplicates/variations of the same behavior, STOP (extraction is spinning)
4. **No new unique behavior**: If you cannot identify any normative statement NOT already covered

**Return `complete: false` ONLY when:**
- There is a SPECIFIC, UNIQUE normative statement not yet captured
- You can name the exact section and requirement that needs a canonical

## CRITICAL: Detect Duplicates

**Review the extracted schemas for duplicates:**
- Multiple canonicals with same trigger signal (e.g., multiple "memory_operation_issued") = DUPLICATES
- Canonicals describing the same behavior with different IDs = DUPLICATES
- If you see duplicates, return `complete: true` - the extraction is spinning and should stop

**Expected canonical count:**
- Small spec (5 sections): 5-8 canonicals
- Medium spec (10 sections): 8-12 canonicals
- If you see 15+ canonicals, there are likely duplicates - return `complete: true`

## Output Format

Return JSON with `thinking` and `result` fields.

**IMPORTANT**: The `result` field must be a BOOLEAN (`true` or `false`), not an object!

If extraction is COMPLETE (no more unique canonicals needed):
```json
{
  "thinking": "All 5 spec sections are covered: instruction resolution (C001), memory ordering (C002), atomic ops (C003), exceptions (C004), interrupts (C005). 6 canonicals extracted, no duplicates. COMPLETE.",
  "result": true
}
```

If more canonicals remain (and you can name a SPECIFIC uncovered requirement):
```json
{
  "thinking": "Only 3 canonicals extracted. Missing coverage for: exception handling (Section 4) and interrupt delivery (Section 5).",
  "result": false
}
```

**CRITICAL**: 
- `result` must be `true` or `false` (boolean), NOT an object
- Return `true` if you see duplicates or 8+ canonicals
- Return `true` if all spec sections have corresponding canonicals

## Note

Be thorough but not exhaustive. Focus on architecturally significant behaviors.
