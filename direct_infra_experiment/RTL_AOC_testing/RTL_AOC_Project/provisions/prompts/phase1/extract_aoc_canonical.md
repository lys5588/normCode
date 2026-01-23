# Extract AOC Canonical

Extract one Action-Obligation Canonical (AOC) rule from the specification.

## Input Data

<user_inputs>
$input_1
</user_inputs>

<previously_extracted_schemas>
$input_2
</previously_extracted_schemas>

**Note:** Ignore any entries with `"__placeholder__": true` - these are system placeholders.

## AOC Definition

An AOC is an executable rule in the form:
```
Trigger(signal, binds=[vars]) → Obligation(signal, match_binds=[vars]) [within cycles] [unless abort]
```

Key principle: **Triggers bind variables, Obligations match them for correlation.**

## Task

Extract ONE new canonical NOT already in `<previously_extracted_schemas>`.

## Required Output Structure

```json
{
  "thinking": "Which spec section, normative language found, why this canonical matters...",
  "result": {
    "id": "C001_InstrResolution",
    "category": "liveness|safety|atomicity|ordering|interrupt|flush",
    "trigger": {
      "signal": "instr_issued",
      "binds": ["iid"],
      "description": "When an instruction is issued"
    },
    "obligation": {
      "type": "any_of|all_of|must|conditional|forbidden",
      "conditions": [
        {"signal": "commit", "match_binds": ["iid"]},
        {"signal": "trap_taken", "match_binds": ["iid"]}
      ]
    },
    "timing": {
      "max_cycles": 10000,
      "min_cycles": 0
    },
    "abort": {
      "signal": "flush_event",
      "match_binds": ["iid"]
    },
    "failure_condition": "Timeout without commit, trap, or flush for instruction iid"
  }
}
```

## Binding Variables (Critical for Correlation)

Choose appropriate binding variables:
- `iid`: Instruction ID (for instruction lifecycle rules)
- `addr`: Memory address (for memory ordering rules)
- `granule`: Cache line granule (for atomicity/LR-SC rules)
- `hart_id`: Hart/core ID (for multi-core rules)
- `exception_code`: Exception type (for exception handling)

## Obligation Types

- `any_of`: At least ONE condition must be satisfied
- `all_of`: ALL conditions must be satisfied  
- `must`: Single required condition
- `conditional`: "If X happens after trigger, then Y must follow"
- `forbidden`: Condition must NOT occur (safety property)

## Categories

- `liveness`: Something must eventually happen (e.g., instr → commit)
- `safety`: Bad state must never occur (e.g., no stale reads)
- `atomicity`: Multi-step must be atomic (e.g., LR-SC)
- `ordering`: Events in specific order (e.g., program order)
- `interrupt`: Interrupt delivery requirements
- `flush`: Pipeline cleanup requirements

## Extraction Guidelines

1. Look for normative language: "shall", "must", "required", "may cancel"
2. Identify **trigger signals** (observable events that start tracking)
3. Identify **obligation signals** (what must happen in response)
4. Extract **timing bounds** from microarchitecture spec if available
5. Identify **abort conditions** (valid ways to cancel obligation)
6. Always include **binds** and **match_binds** for correlation

## CRITICAL: Avoid Duplicates

**Before extracting, check `<previously_extracted_schemas>` for:**
- Same trigger signal → SKIP
- Same obligation behavior with different wording → SKIP  
- Same category already well-covered → SKIP

**Expected unique canonicals per typical spec:**
| Category | Count | Example |
|----------|-------|---------|
| Instruction lifecycle | 1 | issued → commit/trap |
| Memory ordering | 1 | store → visible |
| Atomic operations | 1-2 | LR → SC correlation |
| Exception handling | 1 | exception → precise |
| Interrupt delivery | 1 | pending → taken |
| Flush behavior | 1 | flush → cleanup |

**Total: 5-8 unique canonicals, NOT 20+**

**If no new canonical found, return:**
```json
{
  "thinking": "All normative behaviors covered: [list what's covered]...",
  "result": null
}
```

**Important:** Response MUST be valid JSON with exactly two keys: `thinking` and `result`.
