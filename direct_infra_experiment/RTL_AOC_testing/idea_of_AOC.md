Here is a **clean, canonical summary** you can use as the *definitive description* of **AOC** in the role of **DITM**, positioned between **ISA / user intent / microarchitecture (MA)** and **RTL**.

This is written in a **spec-quality style**, not marketing language.

---

# AOC (Action–Obligation Canonicals) as the DITM Layer

## Position in the stack

```
ISA / User Intent / Microarchitecture (MA)
        ↓
AOC — Action–Obligation Canonicals
        ↓
Design-Intent Testing Model (DITM)
        ↓
Test Software / Test Harness
        ↓
RTL Simulation / Formal Tools
        ↓
RTL
```

---

## What AOC is

> **AOC (Action–Obligation Canonicals)** is a canonically complete, intent-level representation that enumerates all architecturally meaningful actions and the obligations they impose, independent of RTL implementation.

AOC defines:

* what triggers matter
* what responses are required
* what timing or ordering constraints apply
* what exceptions override obligations
* what conditions cancel obligations
* what behaviors are forbidden
* what behaviors are explicitly undefined

---

## What AOC is not

AOC is **not**:

* RTL
* a testbench
* a procedural script
* a state machine
* a reference implementation

AOC is:

* a **semantic contract**
* a **test oracle definition**
* a **model-based testing substrate**

---

## Why AOC exists (the core purpose)

ISA / MA / user intent:

* are normative but informal
* contain implicit assumptions
* leave cases underspecified

RTL:

* is concrete but implementation-specific
* encodes *how*, not *why*

> **AOC bridges this gap by making intent explicit, canonical, and testable.**

---

## Core abstraction of AOC

> **The fundamental unit of AOC is an Action–Obligation Canonical (AOC).**

Each canonical explicitly specifies:

* **Trigger**
  A semantically meaningful, observable action (e.g. instruction issued, request observed).

* **Obligation**
  A required response action or effect (e.g. acknowledgment, exception, commit).

* **Timing / Ordering (optional)**
  Bounds or partial-order constraints.

* **Abort / Override**
  Events that cancel or supersede the obligation (e.g. reset).

* **Preconditions / Assumptions**
  Conditions under which the rule applies.

* **Failure Condition**
  What constitutes non-conformance.

* **Undefined Region**
  Conditions where no correctness claim is made. Undefined regions represent intentional absence of architectural commitment and must not be interpreted as permissive correctness.

This structure forces **canonical completeness**: each AOC must explicitly classify all possible outcomes of its trigger as required, forbidden, or undefined.

---

## Role of AOC as DITM

As the **Design-Intent Testing Model**, AOC:

* serves as the **single source of truth for correctness**
* drives automatic test generation
* defines test constraints and exclusions
* generates assertions, monitors, and coverage goals
* enables simulation-based and formal conformance checking
* provides architecturally meaningful failure explanations

---

## Relationship to testing

AOC does not execute and does not simulate behavior.

Instead:

* test software interprets AOC
* test plans are derived from AOC
* RTL simulations are driven and observed according to AOC
* pass/fail is decided strictly by AOC-defined obligations

---

## Key advantages of AOC as DITM

* **ISA-aligned**: mirrors normative language (“must”, “shall”, “unless”)
* **Complete by construction**: no implicit cases
* **Implementation-agnostic**: portable across RTL designs
* **Concurrency-safe**: handles overlapping actions naturally
* **Executable via tooling**: compiles to assertions and tests

---

## One-sentence canonical definition

> **AOC (Action–Obligation Canonicals) is a canonically complete, intent-level specification of action-triggered obligations that serves as the Design-Intent Testing Model (DITM) between ISA/user intent and RTL.**

---

This summary captures **what AOC is**, **where it sits**, and **why it exists**, without overreaching or ambiguity.

If you want, next we can:

* formalize AOC in a minimal DSL
* define criteria for canonical completeness
* or show a full end-to-end flow from ISA text → AOC → failing RTL test
