# Consolidate AOC Schemas

Transform extracted AOC schemas into executable, canonically complete Action–Obligation Canonicals.

## Input Data

<extracted_schemas>
$input_1
</extracted_schemas>

**Note:** Ignore any entries with `"__placeholder__": true` - these are system placeholders.

## AOC Design Principles

AOC (Action–Obligation Canonicals) must be:
- **Executable**: Parseable to drive tests or verification monitors
- **Canonical**: Specific trigger → specific obligation with explicit outcomes
- **Complete**: Each AOC classifies all outcomes as required, forbidden, or undefined

## Target DSL Structure

Each AOC rule follows this Python-executable pattern:

```python
Rule("C001_InstrResolution")
    .when(Signal("instr_issued", binds=["iid"]))  # Trigger with bindings
    .require(AnyOf(
        Signal("commit", match_binds=["iid"]),    # Obligation must match binding
        Signal("trap_taken", match_binds=["iid"])
    ))
    .within(cycles=10000)                          # Timing constraint
    .unless(Signal("flush_event", match_binds=["iid"]))  # Abort condition
```

## Task

1. **Filter placeholders**: Remove `"__placeholder__": true` entries
2. **Deduplicate**: Merge overlapping canonicals by ID prefix
3. **Normalize to DSL format**: Convert each rule to the executable structure below
4. **Add bindings**: Identify correlation variables (e.g., `iid` for instruction, `addr`/`granule` for memory)
5. **Validate completeness**: Each trigger must have explicit obligation, timing, and abort

## Required Output Structure

```json
{
  "thinking": "Analysis of deduplication, binding inference, and completeness checks...",
  "result": {
    "version": "1.0",
    "extracted_date": "2026-01-23",
    "rules": [
      {
        "id": "C001_InstrResolution",
        "category": "liveness",
        "trigger": {
          "signal": "instr_issued",
          "binds": ["iid"],
          "description": "When an instruction is issued to the backend"
        },
        "obligation": {
          "type": "any_of",
          "conditions": [
            {"signal": "commit", "match_binds": ["iid"]},
            {"signal": "trap_taken", "match_binds": ["iid"]}
          ]
        },
        "timing": {
          "max_cycles": 10000,
          "min_cycles": 0,
          "description": "Liveness timeout for verification"
        },
        "abort": {
          "signal": "flush_event",
          "match_binds": ["iid"],
          "description": "Microarchitectural flush cancels the obligation"
        },
        "failure_condition": "Timeout without commit, trap, or flush",
        "undefined": null
      },
      {
        "id": "C002_MemoryOrdering",
        "category": "ordering",
        "trigger": {
          "signal": "store_executed",
          "binds": ["addr"],
          "description": "When a store is executed"
        },
        "obligation": {
          "type": "must",
          "conditions": [
            {"signal": "visible_to_subsequent_load", "match_binds": ["addr"]}
          ]
        },
        "timing": {
          "max_cycles": 100,
          "description": "Store must become visible within bounded time"
        },
        "abort": null,
        "failure_condition": "Subsequent load to same address sees stale value after timeout",
        "undefined": null
      },
      {
        "id": "C003_AtomicSC",
        "category": "atomicity",
        "trigger": {
          "signal": "LR_executed",
          "binds": ["granule"],
          "description": "Load-Reserved sets a reservation"
        },
        "obligation": {
          "type": "conditional",
          "condition": {"signal": "conflicting_write", "match_binds": ["granule"]},
          "then": {"signal": "SC_result", "value": "FAILURE", "match_binds": ["granule"]},
          "description": "If conflicting write observed, SC must fail"
        },
        "timing": {
          "max_cycles": null,
          "description": "Must hold until SC completes"
        },
        "abort": null,
        "failure_condition": "SC returns SUCCESS after conflicting write",
        "undefined": null
      }
    ],
    "metadata": {
      "total_rules": 6,
      "coverage": {
        "liveness": ["C001"],
        "safety": ["C004"],
        "atomicity": ["C003"],
        "ordering": ["C002"],
        "interrupt": ["C005"],
        "flush": ["C006"]
      },
      "binding_variables": {
        "iid": "Instruction ID for correlation",
        "addr": "Memory address for ordering",
        "granule": "Cache line granule for atomicity"
      }
    }
  }
}
```

## Obligation Types

- `any_of`: Obligation satisfied by ANY matching condition
- `all_of`: ALL conditions must be satisfied
- `must`: Single required condition
- `conditional`: If X happens, then Y must follow
- `forbidden`: Condition must NOT occur

## Categories

- `liveness`: Something must eventually happen
- `safety`: Bad state must never occur
- `atomicity`: Multi-step operations must be atomic
- `ordering`: Events must occur in specific order
- `interrupt`: Interrupt handling requirements
- `flush`: Pipeline cleanup requirements

## Quality Checklist

- [ ] Every trigger has `binds` for correlation variables
- [ ] Every obligation uses `match_binds` to correlate with trigger
- [ ] Timing constraints have numeric `max_cycles` (or explicit null if unbounded)
- [ ] Signals are concrete, observable names (not prose)
- [ ] Each rule has explicit `failure_condition`
- [ ] Duplicates merged (e.g., multiple "memory ordering" rules combined)

**Important:** Your response MUST be valid JSON with exactly two top-level keys: `thinking` and `result`.
