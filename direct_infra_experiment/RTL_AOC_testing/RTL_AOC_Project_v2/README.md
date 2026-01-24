# RTL_AOC_Project

A NormCode Canvas App project for RTL verification using Action-Obligation Canonicals (AOC).

## Project Files

| File | Format | Description |
|------|--------|-------------|
| `_.instruction.txt` | Natural Language | Original task description - the starting point |
| `_.ncds` | Draft NormCode | Derived structure using natural language operations |
| `_.semi_formal.ncds` | Semi-Formal NormCode | With syntactic operators (`$.`, `*.`, `@:!`, etc.) |
| `_.pf.ncd` | Post-Formalized | Complete with flow indices, types, paradigms, provisions |
| `provisions/` | Resources | Prompts, scripts, input files for execution |

## Compilation Pipeline

```
_.instruction.txt     Natural language task description
        ↓
    Derivation        (manual or LLM-assisted)
        ↓
    _.ncds            Draft structure with hierarchy
        ↓
   Formalization      (adds operators, types, flow indices)
        ↓
_.semi_formal.ncds    Semi-formal with syntactic operators
        ↓
  Post-Formalization  (adds paradigms, provisions, axes)
        ↓
    _.pf.ncd          Post-formalized with execution annotations
        ↓
   Activation         (Canvas App compiler)
        ↓
   .ncd + repos       Executable format
```

## Workflow Overview

### Phase 1: AOC Schema Generation

1. **Load specs**: ISA and microarchitecture specification files
2. **User clarification**: Decompose specs into atomic intent blocks
3. **Iterative extraction**: Extract AOC canonicals one by one until done
4. **Validation**: Judge if generated AOC rules are valid

### Phase 2: RTL Trace Verification

1. **Load trace**: RTL simulation output
2. **Split to cycles**: Discrete verification units
3. **Per-cycle loop**:
   - Update active rules based on current cycle
   - Verify cycle against active rules
   - Carry active rules to next iteration
4. **Report**: Combine all results

## Key Patterns Used

### Self-Terminating Loop (Phase 1)
```ncds
<- counters
    <= append next counter to counters
        <= if session should NOT end         /: @:! timing gate
        <* no more canonicals to process?
```
Loop continues until judgement returns True.

### State Carry (Phase 2)
```ncds
<* previous active rules carried from active rules
```
Active rules state flows from iteration N to iteration N+1.

### Conditional Execution
```ncds
<= return the verification result for this iteration
    <= only if AOC is valid                  /: @:' timing gate
    <* AOC is valid?
```
Verification only proceeds if AOC validation passed.

## Running This Project

1. Open Canvas App
2. Load project from this folder
3. Compile `_.ncds` or `_.pf.ncd`
4. Spec files are in `provisions/inputs/specs/`:
   - `provisions/inputs/specs/isa_v1.md`
   - `provisions/inputs/specs/uarch_v2.md`
5. Trace file is in `provisions/inputs/trace/`:
   - `provisions/inputs/trace/rtl_trace.json`
6. Execute the workflow

## Dependencies

- Canvas App (for compilation and execution)
- LLM provider (for semantic operations)
- Spec files (ISA, microarchitecture)
- RTL simulation trace

## Related Documentation

- [AOC Concept](../idea_of_AOC.md)
- [AOC DSL Design](../AOC_DSL_Design.md)
- [Worked Examples](../AOC_Worked_Example.md)
- [NormCode Derivation Guide](../../../documentation/current/4_compilation/derivation.md)

