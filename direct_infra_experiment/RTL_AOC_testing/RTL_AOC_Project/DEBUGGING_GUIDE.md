# NormCode Debugging Guide

A comprehensive guide based on debugging experience with the RTL AOC Verification workflow. This document captures common issues, diagnostic patterns, and solutions encountered during NormCode development.

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Common Error Categories](#2-common-error-categories)
3. [Debugging Workflow](#3-debugging-workflow)
4. [Flow Index Structure](#4-flow-index-structure)
5. [Activator Issues](#5-activator-issues)
6. [Working Interpretation Issues](#6-working-interpretation-issues)
7. [Paradigm Issues](#7-paradigm-issues)
8. [Prompt Engineering Issues](#8-prompt-engineering-issues)
9. [Loop and State Management Issues](#9-loop-and-state-management-issues)
10. [Shape and Axis Issues](#10-shape-and-axis-issues)
11. [Key Diagnostic Files](#11-key-diagnostic-files)

---

## 1. Architecture Overview

### Pipeline Flow

```
_.ncds (NormCode Plan in natural language)
    ↓ Formalizer
_.pf.ncd (NormCode Plan)
    ↓ _.parse_to_nci.py
_.pf.nci.json (Intermediate)
    ↓ _.activate_nci.py
repos/concept_repo.json + repos/inference_repo.json
    ↓ Canvas Execution Engine
logs_run_*/execution_*.txt (Runtime Logs)
```

### Key Components

| Component | Purpose | Key Fields |
|-----------|---------|------------|
| `concept_repo.json` | Defines all concepts | `concept_name`, `axis_name`, `reference_axis_names`, `is_invariant` |
| `inference_repo.json` | Defines how concepts are inferred | `working_interpretation`, `function_concept`, `value_concepts` |
| `working_interpretation` | Runtime instructions | `syntax`, `paradigm`, `value_selectors`, `body_faculty` |

---

## 2. Common Error Categories

### 2.1 Activator Parsing Errors

**Symptoms:**
- Missing fields in `inference_repo.json`
- Incorrect `working_interpretation` structure
- Wrong `function_concept` names

**Root Causes:**
- Regex patterns not matching NormCode syntax
- Indentation bugs (Python code running outside intended blocks)
- Missing annotation extraction

### 2.2 Runtime Execution Errors

**Symptoms:**
- `AR failed for X: 'field' must be specified`
- Shape mismatches in `cross_product`
- `KeyError` in paradigm execution

**Root Causes:**
- Missing `working_interpretation` fields
- Incorrect axis configuration
- Paradigm key extraction mismatches

### 2.3 LLM Output Issues

**Symptoms:**
- `None` extracted from LLM response
- Judgement always returns `False`
- Infinite loops

**Root Causes:**
- Prompt not specifying correct output format
- Paradigm extracting wrong JSON key
- Missing duplicate detection in extraction prompts

---

## 3. Debugging Workflow

### Step 1: Identify the Failing Flow Index

Check execution logs:
```
logs_run_XXXX/execution_NNNN_cycleM_X.Y.Z.txt
```

Look for:
- `[ERROR]` lines
- `AR failed`, `TVA failed`, `MFP failed`
- Empty or missing reference data

### Step 2: Check Working Interpretation

```bash
# Search for the flow index in inference_repo.json
grep -A 30 '"flow_index": "X.Y.Z"' repos/inference_repo.json
```

Verify:
- `syntax` contains required fields for the marker
- `paradigm` matches expected paradigm name
- `value_selectors` present if needed

### Step 3: Check Concept Configuration

```bash
# Search for the concept in concept_repo.json
grep -A 15 '"concept_name": "X"' repos/concept_repo.json
```

Verify:
- `axis_name` is set (required for TVA axis creation from lists)
- `reference_axis_names` matches expected axes
- `is_invariant` is `true` for loop-persistent state

### Step 4: Trace Back to NCI

```bash
# Find the inference in NCI
grep -A 50 '"flow_index": "X.Y.Z"' _.pf.nci.json
```

Check:
- `attached_comments` contains expected annotations
- `operator_type` is correct
- Concept names are parsed correctly

### Step 5: Trace Back to NCD

Check the original `.pf.ncd` file for:
- Correct annotation syntax
- Proper flow index hierarchy
- Expected operator patterns

---

## 4. Flow Index Structure

### 4.1 Flow Index Hierarchy Pattern

**Correct Pattern:**
```
1.7      - {parent value}           (depth 2, index length 2)
  1.7.1  - &[{}] (functional)       (depth 3, index length 3) - ALWAYS .1
  1.7.2  - {input1}                 (depth 3, index length 3) - sibling
  1.7.3  - {input2}                 (depth 3, index length 3) - sibling
    1.7.3.1 - $. (functional)       (depth 4, index length 4) - child's .1
    1.7.3.2 - <source>              (depth 4, index length 4) - sibling input
  1.7.4  - {input3}                 (depth 3, index length 3) - sibling
```

**Rules:**
1. **Same depth = same index length** - Siblings have indices with same number of parts
2. **Functional concept is always `.1`** - The operator/imperative is the first child
3. **Value concepts are siblings, not children** - Inputs to a functional are at same depth
4. **Each functional can have its own child tree** - Nested inferences follow same pattern

**Common Mistake:**
```
# WRONG - nesting inputs under functional
1.7.1    - &[{}] (functional)
  1.7.1.1  - {input1}  ← Wrong! Should be 1.7.2
  1.7.1.2  - {input2}  ← Wrong! Should be 1.7.3
```

### 4.2 Missing Input References for Operators

**Problem:** Specification operator references a concept in `%>()` but doesn't declare it as a child value concept, causing scheduler to not know about the dependency.

**Symptom:** Value concept shows "empty" status even though source is "complete"

**Example:**
```ncd
# WRONG - missing input reference
<- {AOC validity} | ?{flow_index}: 1.7.3
    <= $. %>(<AOC is valid>) | ?{flow_index}: 1.7.3.1 | ?{sequence}: assigning
    # Missing: <- <AOC is valid> | ?{flow_index}: 1.7.3.2

# CORRECT - explicit input reference
<- {AOC validity} | ?{flow_index}: 1.7.3
    <= $. %>(<AOC is valid>) | ?{flow_index}: 1.7.3.1 | ?{sequence}: assigning
    <- <AOC is valid> | ?{flow_index}: 1.7.3.2
        | %{ref_axes}: [_none_axis]
        | %{ref_element}: %{truth_value}
```

**Diagnosis:** Check execution logs for:
```
Value concepts (5): [..., "'{concept}'=empty", ...]
RESULT: NOT READY. Value concepts not ready: ["'{concept}' (Status: empty)"]
```

---

## 5. Activator Issues

### 5.1 Indentation Bug (Critical)

**Problem:** Code running outside intended conditional blocks.

**Example:**
```python
# BUG: This runs for ALL markers!
if marker == "%":
    wi["syntax"] = {"marker": "%", "face_value": ...}
elif marker == ".":
    wi["syntax"] = {"marker": ".", "assign_source": ...}

wi["syntax"] = {"marker": marker, "assign_source": None}  # OVERWRITES!
```

**Solution:** Ensure all syntax assignments are inside their respective blocks:
```python
else:
    # Only for unhandled markers
    wi["syntax"] = {"marker": marker, "assign_source": None}
```

### 5.2 Missing Field Extraction

**Symptoms:** `'field' must be specified` errors

**Checklist:**
- [ ] Regex pattern matches actual NormCode syntax
- [ ] Captured groups are correctly indexed
- [ ] Field is added to `wi["syntax"]`
- [ ] Annotation parsing function handles edge cases

### 5.3 Annotation Pattern Reference

| Annotation | Pattern | Purpose |
|------------|---------|---------|
| `%{name}: value` | `r"%\{(\w+)\}:\s*(.+)"` | Key-value annotation |
| `%{literal<$% X>}: value` | `r"%\{literal<\$([%=.+-])\s*([^>]+)>\}:\s*(.+)"` | Literal value for abstraction |
| `<:{N}>` | `r"<:\{(\d+)\}>"` | Input binding order |
| `%>({concept})` | `r"%>\(\{([^}]+)\}\)"` | Output/source concept (object) |
| `%>[{concept}]` | `r"%>\(\[([^\]]+)\]\)"` | Output/source concept (relation) |
| `%<({concept})` | `r"%<\(\{([^}]+)\}\)"` | Source element (continuation) |
| `%:(axis)` | `r"%:\(([^)]+)\)"` | Axis name |
| `%+(axis)` | `r"%\+\(([^)]+)\)"` | Create axis (grouping) |

---

## 6. Working Interpretation Issues

### 6.1 Required Fields by Sequence Type

| Sequence | Required in `syntax` |
|----------|---------------------|
| `assigning` (abstraction `%`) | `marker`, `face_value`, `axis_names` |
| `assigning` (specification `.`) | `marker`, `assign_source` |
| `assigning` (continuation `+`) | `marker`, `assign_source`, `assign_destination`, `by_axes` |
| `grouping` | `marker`, `sources`, `create_axis`, `by_axes` |
| `looping` | `marker`, `LoopBaseConcept`, `CurrentLoopBaseConcept`, `ConceptToInfer` |
| `imperative`/`judgement` | `paradigm`, `body_faculty`, `value_order` |

### 6.2 Value Selectors

When bundled data (dicts, lists) needs to stay bundled:

```json
"value_selectors": {
  "{concept_name}": {
    "packed": true
  }
}
```

In `.pf.ncd`:
```ncd
<- {bundled data}<:{1}> | ?{flow_index}: X.Y.Z
    | %{selector_packed}: true
```

---

## 7. Paradigm Issues

### 7.1 Key Extraction Mismatch

**Problem:** Paradigm extracts different key than prompt outputs.

**Example:**
- Paradigm: `{"key": "is_vague"}` 
- Prompt outputs: `{"result": {"complete": true}}`
- Result: `None` extracted

**Solution:** Align paradigm key with prompt output structure:
- Paradigm: `{"key": "result"}`
- Prompt: `{"thinking": "...", "result": true}`

### 7.2 Tool Name Mismatch

**Problem:** Paradigm uses wrong tool name.

**Example:**
- Paradigm: `"tool_name": "user_input_tool"`
- Registration: `body.user_input = self.user_input_tool`
- Error: Tool not found

**Solution:** Use registered name: `"tool_name": "user_input"`

### 7.3 Common Paradigm Patterns

| Paradigm | Output | Key Extracted |
|----------|--------|---------------|
| `c_GenerateThinkJson-o_Literal` | `{"thinking": "...", "result": {...}}` | `result` |
| `c_GenerateThinkJson-o_Boolean` | `{"thinking": "...", "result": true}` | `result` (boolean) |
| `c_Execute-o_ListLiteral` | `[item1, item2, ...]` | Wrapped as list of literals |

---

## 8. Prompt Engineering Issues

### 8.1 Required JSON Format

All LLM prompts using `GenerateThinkJson` paradigm MUST specify:

```markdown
## Output Format

Return JSON with `thinking` and `result` fields:
```json
{
  "thinking": "Your analysis...",
  "result": { ... }  // or boolean for judgements
}
```

**Important:** Your response MUST be valid JSON with exactly these two top-level keys.
```

### 8.2 Input Templating

Use `$input_N` variables with XML wrappers:

```markdown
## Input Data

<user_inputs>
$input_1
</user_inputs>

<previous_data>
$input_2
</previous_data>
```

### 8.3 Duplicate Prevention (Extraction Loops)

For iterative extraction, include:

```markdown
## CRITICAL: Avoid Duplicates

**Before extracting, check `<previously_extracted>`:**
- If same trigger signal exists, DO NOT extract variation
- If behavior is same with different wording, it's a duplicate

**If no NEW item found, return:**
```json
{"thinking": "All items covered...", "result": null}
```

**Expected count: 5-10 unique items, NOT 20+**
```

### 8.4 Judgement Termination

For judgements that control loop termination:

```markdown
## Termination Criteria

Return `true` (complete) when:
- All requirements covered
- Duplicates detected (spinning)
- Reasonable count reached (15+)

Return `false` (continue) ONLY when:
- Specific unique requirement not yet covered
```

---

## 9. Loop and State Management Issues

### 9.1 Invariant Concepts

Concepts that persist across loop iterations need:

```ncd
<- [persistent_state] | ?{flow_index}: X.Y.Z
    | %{is_invariant}: true
```

Without this, references may be reset between iterations.

### 9.2 Empty List Initialization

**Problem:** Empty list `[]` has shape `(0,)`, causing `cross_product` to produce nothing.

**Solution:** Initialize with placeholder:

```ncd
<= $% %>([%({"__placeholder__": true})]) | ?{sequence}: assigning
    | %{literal<$% records>}: [{"__placeholder__": true}]
```

Then update prompts to ignore placeholders.

### 9.3 Loop Structure Pattern

```ncd
/: Initialize BEFORE loop (sibling, not child)
<- [counters] | ?{flow_index}: 1.2.6
    <= $% %>([%(1)]) | ?{sequence}: assigning

<- [records] | ?{flow_index}: 1.2.7
    <= $% %>([%(placeholder)]) | ?{sequence}: assigning

/: Loop
<- [results] | ?{flow_index}: 1.2.8
    <= *. %>([counters]) %<({item}) %:({counter}) %@(1) | ?{sequence}: looping
        
        /: Loop return
        <= $. %>({item}) | ?{sequence}: assigning
        
        /: Compute item
        <- {item} | ?{flow_index}: 1.2.8.1.2
            <= ::(...) | ?{sequence}: imperative
        
        /: Update persistent state (invariant)
        <- [records] | ?{flow_index}: 1.2.8.1.3
            | %{is_invariant}: true
            <= $+ %>([records]) %<({item}) %:(_none_axis) | ?{sequence}: assigning
        
        /: Check termination
        <- <done> | ?{flow_index}: 1.2.8.1.4
            <= ::(...)<ALL True> | ?{sequence}: judgement
        
        /: Conditional counter increment
        <- [counters] | ?{flow_index}: 1.2.8.1.5
            | %{is_invariant}: true
            <= $+ %>([counters]) %<({next}) %:(counter) | ?{sequence}: assigning
                <= @:!(<done>) | ?{sequence}: timing
```

---

## 10. Shape and Axis Issues

### 10.1 TVA Axis Creation

For imperative outputs to create axes from lists:

1. Concept needs `axis_name` in `concept_repo.json`
2. Use `o_ListLiteral` paradigm variant
3. Paradigm's `wrap_list` step wraps each element

**Activator must set:**
```python
concept_entry = {
    "axis_name": primary_axis_name,  # For TVA
    "reference_axis_names": axis_names,  # Full list
    ...
}
```

### 10.2 Grouping Without Axis Creation

For packed output (shape `(1,)` with all items in single element):

```ncd
<= &[#] %>[{source}] | ?{sequence}: grouping
    /: NO %+(axis) = create_axis: null
```

Results in:
```json
"syntax": {
  "create_axis": null,
  "by_axes": [["_none_axis"], ...]
}
```

### 10.3 Shape Mismatch Debugging

**Error:** `Shape mismatch for axis 'X': N vs M`

**Causes:**
1. One input has shape `(N,)`, another has shape `(M,)` on same axis
2. Packed selector not applied to bundled data

**Solutions:**
1. Use grouping to normalize shapes
2. Add `%{selector_packed}: true` to bundled inputs
3. Create intermediate grouping step

---

## 11. Key Diagnostic Files

### Execution Logs

```
logs_run_XXXX/execution_NNNN_cycleM_X.Y.Z.txt
```

Contains:
- Step-by-step execution (IWI → IR → AR/MFP/TVA → OR → OWI)
- Reference shapes and contents at each step
- Error messages with context

### Repository Files

```
repos/concept_repo.json  # All concepts with metadata
repos/inference_repo.json  # All inferences with working_interpretation
```

### Intermediate Format

```
_.pf.nci.json  # Parsed NormCode with attached_comments
```

### Quick Diagnostic Commands

```bash
# Find inference by flow index
grep -A 30 '"flow_index": "1.2.7"' repos/inference_repo.json

# Find concept by name
grep -A 15 '"concept_name": "\[counters\]"' repos/concept_repo.json

# Find all assigning inferences
grep -B 2 '"inference_sequence": "assigning"' repos/inference_repo.json

# Count inference types
grep '"inference_sequence":' repos/inference_repo.json | sort | uniq -c

# Find errors in logs
grep -r "\[ERROR\]" logs_run_*/
```

---

## Summary: Top 12 Debugging Tips

1. **Check indentation in activator** - Python indentation bugs cause silent overwrites
2. **Verify working_interpretation fields** - Each sequence type has required fields
3. **Match paradigm keys to prompt output** - `is_vague` vs `result` mismatch causes `None`
4. **Use `is_invariant: true`** for loop-persistent state
5. **Initialize lists with placeholders** - Empty `(0,)` shape breaks `cross_product`
6. **Set `axis_name` for TVA** - Required for list-to-axis conversion
7. **Add `packed: true`** for bundled data inputs
8. **Specify JSON format in prompts** - `{"thinking": ..., "result": ...}`
9. **Add duplicate detection** in extraction prompts
10. **Check flow index hierarchy** - Context concepts should be siblings, not children
11. **Add explicit input references** - Operators need child value concepts for dependencies
12. **Use `%{value_order}`** - Explicitly control which concepts become paradigm inputs

---

## Quick Reference: Flow Index Pattern

```
Parent Value (X.Y)
├── Functional (X.Y.1)          ← Always .1
├── Input Value (X.Y.2)         ← Siblings
│   ├── Child Functional (X.Y.2.1)
│   └── Child Input (X.Y.2.2)
├── Input Value (X.Y.3)
└── Input Value (X.Y.4)
```

**Key Rule:** Same depth = same index length. Functional is always first child (`.1`).

---

*Document created: 2026-01-23*
*Last updated: 2026-01-23 (flow index structure, missing input references)*
*Based on RTL AOC Verification workflow debugging experience*

