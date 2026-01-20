# ISA Specification v1 (Sample)

This is a sample ISA specification for demonstrating AOC extraction.

## Section 1: Instruction Resolution

> Each issued instruction **shall** resolve to exactly one of:
> - **Architectural commit** — instruction completes and becomes visible
> - **Trap** — exception or interrupt causes architectural state change
> 
> A microarchitectural flush or pipeline reset **may cancel** younger in-flight instructions without violating this requirement.

## Section 2: Memory Ordering

> All memory operations to the same address **shall** appear to execute in program order from the perspective of other observers.
>
> Stores **must** become visible to subsequent loads within a bounded time.

## Section 3: Atomic Operations

> If a Store-Conditional (`SC`) instruction returns **success**, then no conflicting write to the reservation granule **shall** have become architecturally visible between the paired `LR` and the `SC`.
>
> A conflicting write **must** cause the `SC` to return failure.

## Section 4: Exception Handling

> When an exception occurs, the processor **shall** save the return address and cause in the appropriate CSRs before transferring control to the exception handler.
>
> Exceptions **must** be precise: all instructions before the faulting instruction have committed, and no instructions after have committed.

## Section 5: Interrupt Delivery

> When an enabled interrupt is pending, it **shall** be taken at the next instruction boundary, unless the processor is executing a critical section marked by interrupt-disable instructions.

