# Manual Modifications Log

This document records manual modifications made to the NormCode files (`.pf.ncd`, `.ncds`) and related infrastructure during development. These patterns should be considered for automation in the compilation pipeline.

---

## 1. User Input Paradigm for Human-in-the-Loop Operations

### Problem
The `:>:` (user-facing imperative) was incorrectly using an LLM paradigm instead of a user input tool.

### Solution
Created a new paradigm `v_PromptLocation-h_Literal-c_UserTextEditor-o_JsonLiteral` that uses the `user_input_tool` for human-in-the-loop interaction.

### Changes in `.pf.ncd`
```ncd
<= :>:(ask user to clarify and decompose the specs into intent blocks) | ?{flow_index}: 1.2.4.1 | ?{sequence}: imperative
    | %{norm_input}: v_PromptLocation-h_Literal-c_UserTextEditor-o_JsonLiteral
    | %{v_input_norm}: prompt_location
    | %{v_input_provision}: provisions/prompts/phase1/decompose_specs.md
    | %{h_input_norm}: Literal
    | %{body_faculty}: user_input
    | %{interaction_type}: text_editor
```

### Key Annotations
- `%{body_faculty}: user_input` - Specifies user input tool instead of LLM
- `%{interaction_type}: text_editor` - Specifies the interaction mode

### Paradigm File
Location: `provisions/paradigms/v_PromptLocation-h_Literal-c_UserTextEditor-o_JsonLiteral.json`

**Important**: The tool name in the paradigm must match the registered name in `tool_injection.py`:
- Registered as: `body.user_input = self.user_input_tool`
- So paradigm uses: `"tool_name": "user_input"` (NOT `user_input_tool`)

---

## 2. Loop State Management with Records Concept

### Problem
The iterative extraction loop needed to accumulate results across iterations, but the original design didn't have a persistent state container.

### Solution
Added `[AOC schemas records]` as a mutable state container initialized before the loop and updated within each iteration.

### Changes in `.ncds`
```
<- counters
    <= initialize to list containing only 1

<- AOC schemas records
    <= initialize to empty list

/: Iterative extraction loop
<- all AOC schemas
    <= for each counter in counters
    
        <= return the new AOC for this iteration
        
        <- new AOC
            <= extract a new action-obligation canonical
            <- all user inputs
            <- AOC schemas extracted so far
                <= collect all AOC schemas from previous iterations
                <- AOC schemas records
        
        <- AOC schemas records
            <= append next new AOC to AOC schemas records
            <- AOC schemas records
            <- new AOC
```

### Changes in `.pf.ncd`
```ncd
/: Initialize AOC schemas records before loop
<- [AOC schemas records] | ?{flow_index}: 1.2.7
    | %{ref_axes}: [canonical]
    | %{ref_shape}: (0,)
    | %{ref_element}: dict(id: str, trigger: dict, obligation: dict, timing: dict, abort: dict)
    <= $% %>([%([])]) | ?{flow_index}: 1.2.7.1 | ?{sequence}: assigning
        /: ABSTRACTION: Initialize AOC schemas records to empty list
        | %{literal<$% aoc_schemas_records>}: []
```

### Pattern: Loop with Mutable State
1. Initialize state container BEFORE the loop (sibling, not child)
2. Inside loop: read from state, compute new value, update state
3. Use `$+` (continuation) operator for appending to lists

---

## 3. Invariant Concepts in Loops

### Problem
Certain concepts inside loops need to persist their references across iterations without being reset. Specifically:
- `[counters]` - The loop counter that grows each iteration
- `[AOC schemas records]` - The accumulated results

### Solution
Added `%{is_invariant}: true` annotation to mark concepts that should not have their references reset during loop iterations.

### Changes in `.pf.ncd`
```ncd
<- [AOC schemas records] | ?{flow_index}: 1.2.8.1.3
    | %{ref_axes}: [canonical]
    | %{ref_shape}: (n_canonical,)
    | %{ref_element}: dict(id: str, trigger: dict, obligation: dict, timing: dict, abort: dict)
    | %{is_invariant}: true

<- [counters] | ?{flow_index}: 1.2.8.1.5
    | %{ref_axes}: [counter]
    | %{ref_shape}: (n_counter,)
    | %{ref_element}: int
    | %{is_invariant}: true
```

### Changes in `_.activate_nci.py`
Added parsing for `is_invariant` annotation:
```python
is_invariant_str = get_annotation_value(attached_comments, "is_invariant")
is_invariant = is_invariant_str and is_invariant_str.lower() == "true"
```

And included in concept entry:
```python
concept_entry = {
    ...
    "is_invariant": is_invariant,
    ...
}
```

### Infrastructure Support
The `is_invariant` field is defined in `infra/_orchest/_repo.py`:
```python
is_invariant: bool = False  # New attribute: prevents reference reset during quantifying loops
```

**Note**: The looping step (`_lr.py`) may need updates to respect this flag.

---

## 4. Flow Index Structure for Context Concepts

### Problem
Context concepts for imperatives were incorrectly nested under the function concept instead of being siblings.

### Correct Structure
Context concepts should be siblings of the function concept (imperative), not children:

```
<- {new AOC} | ?{flow_index}: 1.2.8.1.2                          # Value to infer
    <= ::(extract...) | ?{flow_index}: 1.2.8.1.2.1               # Function (imperative)
    <- {all user inputs}<:{1}> | ?{flow_index}: 1.2.8.1.2.2      # Context 1 (sibling)
    <- [AOC schemas extracted so far]<:{2}> | ?{flow_index}: 1.2.8.1.2.3  # Context 2 (sibling)
```

### Pattern
- Parent concept: `X.Y.Z`
- Function concept: `X.Y.Z.1`
- Context concepts: `X.Y.Z.2`, `X.Y.Z.3`, etc.

---

## 5. Literal Value Preservation in Abstraction

### Problem
For abstraction operations (`$%`), the `face_value` in `inference_repo.json` was being parsed to raw values (e.g., `[1]`) instead of preserving the literal wrapper notation (e.g., `%(1)`).

### Solution
Modified `_.activate_nci.py` to use `extract_literal_annotation_value` to preserve the literal wrapper:

```python
elif marker == "%":
    face_value = extract_literal_annotation_value(func_concept.get("attached_comments", []), "literal<$% counters>")
    # ...
    wi["syntax"] = {
        "marker": marker,
        "face_value": [face_value],  # Preserves %(1) notation
        "axis_names": axis_names,
    }
```

### Annotation Format
```ncd
<= $% %>([%(1)]) | ?{flow_index}: 1.2.6.1 | ?{sequence}: assigning
    | %{literal<$% counters>}: [1]
```

---

## 6. Functional Concept Name Cleanup

### Problem
Functional concepts had `<=` inference marker in their `concept_name`, `description`, and `natural_name` fields.

### Solution
Strip the `<=` marker early in the concept processing:

```python
# Strip the <= marker first (it's inference syntax, not part of the concept)
concept_name = re.sub(r"^<=\s*", "", nc_main)
```

---

## 7. Reference Data for Operators

### Problem
Operators lacked `reference_data` in `concept_repo.json`.

### Solution
Added default dummy reference for operators:

```python
else:
    # Operators and other function concepts get dummy reference
    reference_data = ["%{dummy}(_)"]
```

---

## Summary of Key Patterns for Automation

| Pattern | Annotation/Syntax | Purpose |
|---------|------------------|---------|
| User input imperative | `:>:` with `body_faculty: user_input` | Human-in-the-loop operations |
| Invariant loop state | `%{is_invariant}: true` | Prevent reference reset in loops |
| Literal abstraction | `%{literal<$% name>}: value` | Initialize with literal values |
| Loop records pattern | Initialize before loop, update inside | Accumulate results across iterations |
| Context concept indices | Siblings of function, not children | Proper flow hierarchy |

---

## Files Modified

1. `_.pf.ncd` - Main NormCode plan
2. `_.ncds` - NormCode design specification
3. `_.activate_nci.py` - Activator script (is_invariant parsing)
4. `provisions/paradigms/v_PromptLocation-h_Literal-c_UserTextEditor-o_JsonLiteral.json` - New paradigm

---

*Last updated: 2026-01-22*

