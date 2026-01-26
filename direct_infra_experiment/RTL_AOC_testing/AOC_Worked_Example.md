# AOC Worked Example: From ISA to Failing RTL Trace

This document demonstrates the full flow of using Action–Obligation Canonicals (AOC):
1.  **ISA Source**: The Normative User Intent.
2.  **AOC Definition**: The specific Intent-Level rules derived from the ISA.
3.  **Failing RTL Trace**: A hypothetical simulation trace that violates the rule.

---

## Example 1: Instruction Resolution (C001)

### 1. ISA Normative Text
> "Each issued instruction **shall** resolve to exactly one of: **Architectural commit**, ... or **Trap**...
> A microarchitectural flush ... **may cancel** younger in-flight instructions..."

### 2. AOC Definition (Python DSL)

```python
# C001: Every issued instruction must eventually commit or trap, unless flushed.
instr_resolution_rule = (
    Rule("C001_InstrResolution")
    # Trigger: When an instruction is officially issued to the backend
    .when(Trigger("instr_issued"))
    
    # Obligation: It must either commit OR trap
    .require(
        AnyOf(
            Obligation("commit"),
            Obligation("trap_taken")
        )
    )
    
    # Constraints: Must happen for the SAME instruction ID (implicit in real binding)
    # No strict cycle limit in ISA, but let's assume a "liveness" timeout for verification
    .within(Constraint.cycles(10000)) 
    
    # Abort: If a flush occurs that targets this instruction (or older)
    .unless(Trigger("flush_event"))
)
```

*(Note: In a full implementation, `Trigger` would bind variables like `iid`, and `Obligation` would require `match(iid)`.)*

### 3. Failing RTL Trace

**Scenario**: An instruction enters the pipeline but gets "lost" (dropped from the scheduler without committing or flushing) due to a bug in the issue queue full-logic.

| Time | Signal | Value | Note | AOC Monitor State |
| :--- | :--- | :--- | :--- | :--- |
| 100 | `instr_issued` | `iid=0x42, op=ADD` | Instruction enters. | **TRIGGERED**: Expect commit/trap for 0x42. |
| 105 | `instr_issued` | `iid=0x43, op=SUB` | Younger instr. | **TRIGGERED**: Expect commit/trap for 0x43. |
| ... | ... | ... | *Pipeline running...* | Pending... |
| 200 | `commit` | `iid=0x41` | Older instr finishes. | Ignored (not tracking 0x41). |
| 300 | `commit` | `iid=0x43` | **BUG**: 0x43 commits! | **SATISFIED** for 0x43. |
| ... | ... | ... | *0x42 is still missing* | 0x42 is still **PENDING**. |
| 10100| *Timeout* | | Cycle 100+10000 | **VIOLATION**: Rule C001 failed for iid=0x42. |

**Failure Analysis**:
The AOC monitor reports a **Liveness Violation**. Expected `commit` or `trap` for `iid=0x42`, but timeout occurred. No `flush_event` was observed covering `iid=0x42`.
*RTL Bug*: The scheduler treated 0x42 as valid but the execution unit ready-bit was never set, causing it to hang indefinitely while younger instructions bypassed it (if OOO allowed).

---

## Example 2: LR/SC Atomicity (C003)

### 1. ISA Normative Text
> "If `SC` returns **success**, then no conflicting write to the reservation granule shall have become architecturally visible between the `LR` and the `SC`."

### 2. AOC Definition

```python
# C003: SC Success implies no intervening conflicting write.
# Modeled here as: If SC Succeeds, we check the history between LR and SC.
# OR alternatively: If a Conflicting Write occurs after LR, the SC MUST Fail.

sc_atomicity_rule = (
    Rule("C003_SC_Atomicity")
    # Trigger: A specific Load-Reserved sets a reservation
    .when(Trigger("LR_executed", binds=["granule"]))
    
    # Obligation: If a conflicting store happens next...
    .if_followed_by(Trigger("store_visible", match_binds=["granule"]))
    
    # Then: The subsequent SC must fail
    .require(Obligation("SC_result", value="FAILURE", match_binds=["granule"]))
)
```

### 3. Failing RTL Trace

**Scenario**: The coherence controller fails to invalidate the reservation when a snoop/invalidation arrives from another core.

| Time | Signal | Value | Note | AOC Monitor State |
| :--- | :--- | :--- | :--- | :--- |
| 10 | `LR_executed` | `addr=0x100` | Core A does LR. | **TRIGGERED**: Tracking granule 0x100. |
| 15 | `bus_write` | `addr=0x100` | Core B writes 0x100. | Visible conflict observed. |
| 20 | `SC_executed` | `addr=0x100` | Core A does SC. | Awaiting result... |
| 21 | `SC_result` | **SUCCESS** | **BUG**: SC succeeded! | **VIOLATION**: C003. |

**Failure Analysis**:
The AOC observed `LR` -> `Conflicting Write` -> `SC Success`.
This is a **Safety Violation**. The obligation was that if a conflicting write occurred, SC *must* fail.
*RTL Bug*: The `resv_kill_valid` signal from the snooper was disconnected or masked, so the LSU thought the reservation was still valid.

---

## Summary

These examples show how AOC acts as a rigorous **Contract Check**:
1.  It is derived purely from the **English ISA text**.
2.  It creates executable **Monitors**.
3.  It produces clear **Verification Failures** without needing to know *how* the RTL implements the logic (e.g. valid bits, linked lists, or matrices).
