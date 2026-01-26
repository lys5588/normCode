# Microarchitecture Specification v2 (Sample)

This is a sample microarchitecture specification for demonstrating AOC extraction.

## Pipeline Structure

- 6-stage in-order pipeline
- Issue queue depth: 8 entries
- ROB (Reorder Buffer) depth: 32 entries
- Maximum instructions in flight: 32

## Timing Constraints

- Maximum cycles for instruction resolution: 10,000 (liveness bound for verification)
- Memory access latency: 1-100 cycles
- Cache hit latency: 2 cycles
- Cache miss latency: 20-100 cycles

## Flush Behavior

- Pipeline flush clears all speculative state
- ROB flush invalidates all uncommitted instructions
- Flush sources: branch misprediction, exception, CSR write

## Reservation Station Behavior

- LR sets reservation on cache line granule
- Reservation cleared by: matching SC, snoop invalidate, context switch
- Reservation timeout: none (indefinite until cleared)

## Exception Priority

1. External interrupt (highest)
2. Instruction access fault
3. Illegal instruction
4. Breakpoint
5. Load/Store access fault
6. Environment call (lowest)

