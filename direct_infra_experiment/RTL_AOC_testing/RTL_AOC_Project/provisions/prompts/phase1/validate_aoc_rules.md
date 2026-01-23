# Validate AOC Rules

Judge whether the generated AOC rules are valid, complete, and executable.

## Input Data

<aoc_definitions>
$input_1
</aoc_definitions>

## Task

Validate the AOC rules for correctness and completeness. Return `true` if ALL rules pass validation, `false` if ANY rule fails.

## Validation Checklist

### 1. Required Fields (ALL must be present)
Each rule MUST have:
- [ ] `id`: Unique identifier (e.g., "C001_InstrResolution")
- [ ] `category`: One of: liveness, safety, atomicity, ordering, interrupt, flush
- [ ] `trigger.signal`: Observable trigger signal name
- [ ] `trigger.binds`: Array of binding variables (e.g., ["iid"])
- [ ] `obligation.type`: One of: any_of, all_of, must, conditional, forbidden
- [ ] `obligation.conditions`: Array with at least one condition
- [ ] `failure_condition`: Description of what constitutes violation

### 2. Correlation (Critical for Executability)
- [ ] Every `trigger.binds` variable MUST appear in `obligation.conditions[].match_binds`
- [ ] Without correlation, the rule cannot track which response matches which trigger

### 3. Semantic Consistency
- [ ] Trigger and obligation are different signals
- [ ] Timing constraints (if present) are non-negative numbers
- [ ] Abort conditions don't overlap with obligation conditions
- [ ] Category matches the rule behavior (liveness = something must happen, safety = something must NOT happen)

### 4. Testability
- [ ] Signal names are concrete and observable (not prose like "something happens")
- [ ] Conditions can be matched against an event stream programmatically
- [ ] Binding variables are clearly defined

### 5. Coverage
Typical spec should have:
- At least 1 liveness rule (e.g., instruction resolution)
- At least 1 ordering rule (e.g., memory ordering)
- At least 1 atomicity rule (e.g., LR-SC) if applicable

## Output Format

Return JSON with `thinking` and `result` fields.

**If ALL rules are valid:**
```json
{
  "thinking": "Validation complete. Checked 6 rules:\n- C001_InstrResolution: PASS (has iid binding, any_of obligation with match_binds)\n- C002_MemoryOrdering: PASS (has addr binding, proper ordering semantics)\n- ... [detailed per-rule analysis]\nAll required fields present. All correlations valid. Coverage adequate.",
  "result": true
}
```

**If ANY rule is invalid:**
```json
{
  "thinking": "Validation failed. Issues found:\n- C002_MemoryOrdering: FAIL - missing trigger.binds (cannot correlate response to trigger)\n- C004_Exception: FAIL - obligation.conditions[0] missing match_binds\n- WARNING: No atomicity rules found (may be acceptable if spec doesn't cover LR-SC)",
  "result": false
}
```

## Common Issues to Check

| Issue | Why It Fails | Example |
|-------|--------------|---------|
| Missing `binds` | Cannot track which response matches which trigger | `trigger: {signal: "issued"}` without `binds: ["iid"]` |
| Missing `match_binds` | Obligation can't correlate to trigger | `conditions: [{signal: "commit"}]` without `match_binds: ["iid"]` |
| Prose descriptions | Not executable against trace | `signal: "something bad happens"` |
| Wrong category | Misleading classification | Liveness rule labeled as safety |
| Unbounded timing | May cause verification timeout | `max_cycles: null` for liveness rule |

**Important:** Your response MUST be valid JSON with exactly two keys: `thinking` and `result` (boolean).
