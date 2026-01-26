# Provisions for RTL AOC Verification

This directory contains all resources required to execute the RTL AOC Verification workflow.

## Directory Structure

```
provisions/
├── inputs/                  # Input data files
│   ├── specs/               # Specification documents
│   │   ├── isa_v1.md        # ISA specification
│   │   └── uarch_v2.md      # Microarchitecture specification
│   └── trace/               # RTL simulation traces
│       └── rtl_trace.json   # Sample RTL trace
├── paradigms/               # Execution paradigm definitions
│   ├── h_LiteralPath-c_ReadFile-o_Literal.json
│   ├── v_PromptLocation-h_Literal-c_GenerateThinkJson-o_Literal.json
│   ├── v_PromptLocation-h_Literal-c_GenerateThinkJson-o_Boolean.json
│   ├── v_ScriptLocation-h_Literal-c_Execute-o_Literal.json
│   ├── v_ScriptLocation-h_Literal-c_Execute-o_ListLiteral.json
│   └── README.md
├── prompts/                 # LLM prompt templates
│   ├── phase1/              # AOC Schema Generation prompts
│   │   ├── decompose_specs.md
│   │   ├── extract_aoc_canonical.md
│   │   ├── judge_more_canonicals.md
│   │   ├── consolidate_aoc_schemas.md
│   │   └── validate_aoc_rules.md
│   ├── phase2/              # Verification prompts
│   │   ├── update_active_rules.md
│   │   └── verify_cycle.md
│   └── combine_verification_report.md
├── scripts/                 # Python scripts
│   ├── increment_counter.py
│   └── split_trace_to_cycles.py
└── README.md                # This file
```

## Paradigm Reference

### LLM Paradigms
| Paradigm | Purpose |
|----------|---------|
| `v_PromptLocation-h_Literal-c_GenerateThinkJson-o_Literal` | Generate structured JSON from prompt + data |
| `v_PromptLocation-h_Literal-c_GenerateThinkJson-o_Boolean` | Generate boolean judgement |

### File System Paradigms
| Paradigm | Purpose |
|----------|---------|
| `h_LiteralPath-c_ReadFile-o_Literal` | Read file content as string |

### Python Paradigms
| Paradigm | Purpose |
|----------|---------|
| `v_ScriptLocation-h_Literal-c_Execute-o_Literal` | Execute Python, return any value |
| `v_ScriptLocation-h_Literal-c_Execute-o_ListLiteral` | Execute Python, return list |

## Prompt Reference

### Phase 1: AOC Schema Generation

| Prompt | Purpose |
|--------|---------|
| `decompose_specs.md` | Ask user to clarify and decompose specs into intent blocks |
| `extract_aoc_canonical.md` | Extract one AOC canonical from specs |
| `judge_more_canonicals.md` | Judge if more canonicals remain to extract |
| `consolidate_aoc_schemas.md` | Consolidate all extracted schemas into unified definition |
| `validate_aoc_rules.md` | Validate the generated AOC rules |

### Phase 2: Verification

| Prompt | Purpose |
|--------|---------|
| `update_active_rules.md` | Update active rules based on current cycle events |
| `verify_cycle.md` | Verify trace against active rules for one cycle |
| `combine_verification_report.md` | Combine all results into final report |

## Script Reference

| Script | Function | Purpose |
|--------|----------|---------|
| `increment_counter.py` | `increment(n)` | Return n + 1 |
| `split_trace_to_cycles.py` | `split_to_cycles(trace)` | Split trace into discrete cycle events |

## Input Files

### Specification Files (`inputs/specs/`)
- **isa_v1.md**: ISA specification with normative text describing required behaviors
- **uarch_v2.md**: Microarchitecture constraints and implementation details

### Trace Files (`inputs/trace/`)
- **rtl_trace.json**: RTL simulation trace with events per cycle

## Usage

This provisions directory is referenced by `_.pf.ncd`. The Canvas App compiler will:

1. **Post-Formalization (Demand)**: Annotations in `.pf.ncd` declare these resource paths
2. **Activation (Supply)**: Compiler validates and resolves these paths to actual resources

Ensure all files exist before running the workflow.

