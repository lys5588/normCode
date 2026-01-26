# RTL AOC Testing — NormCode for Hardware Verification

This folder demonstrates using **NormCode** to express **Action-Obligation Canonicals (AOC)** for RTL (Register-Transfer Level) hardware verification.

## What is AOC?

**AOC (Action-Obligation Canonicals)** is a canonically complete, intent-level specification that bridges the gap between:
- **ISA / User Intent** (normative but informal)
- **RTL** (concrete but implementation-specific)

Each AOC canonical explicitly specifies:

| Component | Description | Example |
|-----------|-------------|---------|
| **Trigger** | Observable action that initiates the canonical | Instruction issued |
| **Obligation** | Required response/effect | Commit or trap |
| **Timing** | Bounds or ordering constraints | Within 100 cycles |
| **Abort** | Events that validly cancel the obligation | Reset, flush |

> AOC makes intent **explicit, canonical, and testable** without encoding implementation details.

## Why NormCode for Verification?

NormCode's design principles align perfectly with verification requirements:

1. **Data Isolation** — Each verification step sees only explicitly passed inputs
2. **Auditability** — Every intermediate state is inspectable
3. **Structured Workflows** — Multi-phase pipelines with clear dependencies
4. **LLM Integration** — Semantic steps can extract rules from natural language specs

## Files in This Folder

### NormCode Plans (`.ncds`)

| File | Purpose |
|------|---------|
| `handmake_normcode_for_specs_to_AOC.ncds` | **Phase 1**: Extract AOC schemas from ISA/MA specifications |
| `handmake_normcode_for_AOC_to_test.ncds` | **Phase 2**: Apply AOC rules to RTL traces for verification |
| `combined_Normcode_for_spec_AOC_testing.ncds` | **Full Pipeline**: Both phases combined with control flow |

### Documentation

| File | Purpose |
|------|---------|
| `idea_of_AOC.md` | Core concept and positioning of AOC as DITM layer |
| `AOC_DSL_Design.md` | DSL design proposal (Python fluent API + YAML) |
| `AOC_Worked_Example.md` | End-to-end examples from ISA text to failing RTL trace |

### Implementation

| File | Purpose |
|------|---------|
| `aoc_prototype.py` | Python prototype of AOC monitor with `Rule`, `Signal`, `Event` classes |

---

## The Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                     PHASE 1: Spec → AOC                     │
├─────────────────────────────────────────────────────────────┤
│  ISA Spec Text ─┐                                           │
│                 ├─→ User Clarification ─→ Extract AOC ─┐    │
│  MA Spec Text ──┘    (Intent Blocks)       per Canon   │    │
│                                                        ↓    │
│                                            {AOC Definitions}│
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   PHASE 2: AOC → Test                       │
├─────────────────────────────────────────────────────────────┤
│  {AOC Definitions} ─→ Validate ─→ <AOC is valid>           │
│                                                             │
│  RTL Trace ─→ Split to Cycles ─→ ┌────────────────────┐    │
│                                  │  For Each Cycle:   │    │
│                                  │  • Update Active   │    │
│                                  │  • Verify Trace    │    │
│                                  └────────────────────┘    │
│                                           ↓                 │
│                              {Verification per Cycle}       │
└─────────────────────────────────────────────────────────────┘
                              ↓
                    {Verification Report}
```

---

## NormCode Patterns Used

### Phase 1: Extracting AOC from Specs

```ncds
/: Load external files
<* {ISA Spec Text}
    <= ::({Load File})
    <* {File Path} %:{location_string}("specs/isa_v1.md")

/: Get user clarification (external input)
<* {Intent Blocks}
    <= :>:(user clarification of the inputted specs)
    <- {ISA Spec Text}
    <- {MA Spec Text}

/: Group inputs together
<* [All user inputs]
    <= &[{}] %>[{ISA}, {MA}, {Intent Blocks}]
```

### Iterative Extraction with Termination

```ncds
/: Loop until no more canonicals
<* {AOC schemas per canonical}
    <= *. %>({counter}) %*({Current counter})
    
        /: Extract one canonical per iteration
        <- {the new AOC}
            <= ::(extract a new action-obligation canonical)
            <- [All user inputs]
            <- {all AOC schemas up to now}
        
        /: Check termination condition
        <* <no more canonicals>
            <= ::(judge if more canonicals)<ALL True>
        
        /: Continue unless done (negated timing)
        <* {counters}
            <= $+ ({%(n)})
                <= @:! (<no more canonicals>)
```

### Phase 2: Verification Loop with State Carry

```ncds
/: Loop over trace cycles, carrying active rules forward
<- {verification per cycle}
    <= *. %>({Trace per cycle}) %*({Current Cycle}) %^({Previous Active Rules}) %@(1)
    
        /: Update active rules based on current cycle
        <- {Active Rules}
            <= ::(update active rules)<ALL Valid>
            <- {current cycle trace}
            <- {Previous Active Rules}
            <- {AOC Definitions}
        
        /: Verify this cycle
        <- {verification}
            <= ::(verify trace per cycle)
            <- {current cycle trace}
            <- {Active Rules}
    
    /: Carry state between iterations
    <* {Previous Active Rules}<$({Active Rules})*-1>
```

---

## Python Prototype

The `aoc_prototype.py` implements the AOC monitor that the NormCode workflow would invoke:

```python
# Define a rule
r_c001 = (
    Rule("C001_InstrResolution")
    .when(Signal("instr_issued", binds=["iid"]))
    .require(AnyOf(
        Signal("commit", match_binds=["iid"]),
        Signal("trap", match_binds=["iid"])
    ))
    .within(100)
    .unless(Signal("flush_event"))
)

# Process events
monitor = AOCMonitor()
monitor.add_rule(r_c001)
monitor.process_event(Event("instr_issued", {"iid": 0x42}, time=100))
```

### Running the Prototype

```bash
python aoc_prototype.py
```

This runs two demo scenarios:
1. **Instruction Resolution** — Detects a "lost" instruction that never commits
2. **LR/SC Binding** — Validates load-reserved/store-conditional pairs

---

## Worked Examples

From `AOC_Worked_Example.md`:

### Example 1: Lost Instruction (Liveness Violation)

| Time | Signal | Value | AOC Monitor State |
|------|--------|-------|-------------------|
| 100 | `instr_issued` | `iid=0x42` | **TRIGGERED**: Expect commit/trap for 0x42 |
| 105 | `instr_issued` | `iid=0x43` | **TRIGGERED**: Expect commit/trap for 0x43 |
| 300 | `commit` | `iid=0x43` | **SATISFIED** for 0x43. 0x42 still pending |
| 10100 | *Timeout* | | **VIOLATION**: Rule C001 failed for iid=0x42 |

### Example 2: SC Atomicity (Safety Violation)

| Time | Signal | Value | AOC Monitor State |
|------|--------|-------|-------------------|
| 10 | `LR_executed` | `addr=0x100` | **TRIGGERED**: Tracking granule 0x100 |
| 15 | `bus_write` | `addr=0x100` | Conflict observed |
| 21 | `SC_result` | **SUCCESS** | **VIOLATION**: SC should have failed |

---

## Relationship to NormCode

This example demonstrates several key NormCode capabilities:

| Capability | How It's Used |
|------------|---------------|
| **Multi-phase workflows** | Spec→AOC, then AOC→Test |
| **Looping with carry** | State (active rules) passed between iterations |
| **Conditional termination** | "Unless" pattern with negated timing |
| **Judgements** | Validation checks with truth assertions |
| **External inputs** | File loading, user clarification |
| **Data isolation** | Each step sees only explicitly passed data |

---

## Status

This is an **experimental prototype** exploring:
- How NormCode expresses verification workflows
- Integration between LLM-based extraction and deterministic verification
- The AOC abstraction for RTL testing

The NormCode plans (`.ncds`) are **draft format** — they would need compilation to `.ncd` for execution in the Canvas App.

---

## References

- [NormCode Documentation](../../documentation/current/)
- [NormCode Overview](../../documentation/current/1_intro/overview.md)
- [Complete Syntax Reference](../../documentation/current/2_grammar/complete_syntax_reference.md)

