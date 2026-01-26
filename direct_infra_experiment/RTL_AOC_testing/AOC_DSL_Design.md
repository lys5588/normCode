# AOC DSL Design Proposal

Based on the core abstraction of **Action–Obligation Canonicals (AOC)**, this document proposes a minimal Domain Specific Language (DSL) to represent the canons.

## Goals
- **Readable**: Should look like a specification.
- **Executable**: Should be parseable to drive tests or verification.
- **Canonical**: specific trigger -> specific obligation.

## Proposed Syntax (Python-based Fluent API)

Using Python allows us to leverage existing tooling while keeping the syntax clean.

```python
from aoc_core import Rule, Trigger, Obligation, Constraint

# Example: Simple Request-Acknowledge Protocol
# "If a Request is asserted, an Acknowledge must follow within 10 cycles, unless Reset occurs."

req_ack_rule = (
    Rule("ReqAckProtocol")
    .when(Trigger("REQ_SIGNAL", value=1))
    .require(Obligation("ACK_SIGNAL", value=1))
    .within(Constraint.cycles(10))
    .unless(Trigger("RESET", value=1))
)
```

## Proposed Syntax (YAML/Declarative)

For a purely data-driven approach:

```yaml
rule: ReqAckProtocol
trigger:
  signal: REQ_SIGNAL
  value: 1
obligation:
  signal: ACK_SIGNAL
  value: 1
constraints:
  timing:
    max_latency: 10 cycles
abort:
  signal: RESET
  value: 1
```

## Component Breakdown

1. **Trigger**: The event that initiates the canonical lifecycle.
   - Can be a signal edge, a transaction start, or a complex condition.
2. **Obligation**: The state or event that *must* occur to satisfy the canonical.
3. **Constraints**:
   - **Timing**: Min/Max cycles, absolute time.
   - **Ordering**: Must happen before/after X.
4. **Exceptions (Unless/Abort)**: Conditions that validly terminate the obligation without failure.

## Next Steps for Investigation

1. **Prototype the Python Class Structure**: Create a basic script that defines these classes.
2. ** Simulate a Trace**: Create a mock "Event Stream" (like a waveform dump) and run the Rule against it to check for Pass/Fail/Pending.

---
Let's build a prototype of the Python classes to see if this abstraction holds up against a slightly more complex scenario (e.g. a pipelined bus).
