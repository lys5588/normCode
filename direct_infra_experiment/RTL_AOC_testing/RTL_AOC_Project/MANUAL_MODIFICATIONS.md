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

## 8. Value Selectors for Input Control

### Problem
When bundled data (like `{all user inputs}` containing a dict) or lists are passed to imperatives, the MVP step may unpack them into multiple inputs unexpectedly.

### Solution
Added value_selectors support with annotations to control how inputs are processed:

```ncd
<- {all user inputs}<:{1}> | ?{flow_index}: 1.2.8.1.2.2
    | %{ref_axes}: [_none_axis]
    | %{ref_element}: dict
    | %{selector_packed}: true
```

### Available Selector Annotations

| Annotation | Purpose | Example |
|------------|---------|---------|
| `%{selector_packed}: true` | Keep as single input (don't unpack lists/dicts) | Bundled data stays bundled |
| `%{selector_source}: {concept}` | Read from another concept | Select from a different source |
| `%{selector_key}: key_name` | Select specific key from dict | `key: isa` extracts "isa" field |
| `%{selector_index}: N` | Select item at index from list | `index: 0` gets first item |
| `%{selector_unpack}: true` | Explicitly unpack list into separate inputs | Each item becomes a separate input |

### Advanced Example: Selecting Fields from Bundled Data

```ncd
/: Original bundled input
<- {all user inputs} | ?{flow_index}: 1.2.5
    | %{ref_element}: dict(isa: str, ma: str, intent_blocks: list)

/: Using selectors to extract specific fields as separate inputs
<- {isa_spec}<:{1}> | ?{flow_index}: 1.2.8.1.2.2
    | %{selector_source}: {all user inputs}
    | %{selector_key}: isa

<- {ma_spec}<:{2}> | ?{flow_index}: 1.2.8.1.2.3
    | %{selector_source}: {all user inputs}
    | %{selector_key}: ma

<- {intent_list}<:{3}> | ?{flow_index}: 1.2.8.1.2.4
    | %{selector_source}: {all user inputs}
    | %{selector_key}: intent_blocks
```

### Changes in `_.activate_nci.py`
Added parsing for selector annotations in imperative and judgement working_interpretation:
- Extracts `selector_source`, `selector_key`, `selector_index`, `selector_packed`, `selector_unpack`
- Builds `value_selectors` dict in `working_interpretation`

---

## Summary of Key Patterns for Automation

| Pattern | Annotation/Syntax | Purpose |
|---------|------------------|---------|
| User input imperative | `:>:` with `body_faculty: user_input` | Human-in-the-loop operations |
| Invariant loop state | `%{is_invariant}: true` | Prevent reference reset in loops |
| Literal abstraction | `%{literal<$% name>}: value` | Initialize with literal values |
| Loop records pattern | Initialize before loop, update inside | Accumulate results across iterations |
| Context concept indices | Siblings of function, not children | Proper flow hierarchy |
| Packed input | `%{selector_packed}: true` | Keep bundled data as single input |
| Key selection | `%{selector_source}` + `%{selector_key}` | Extract field from dict |
| Placeholder for empty lists | `{"__placeholder__": true}` | Ensure non-empty shape for packed values |
| LLM output format | `{"thinking": ..., "result": ...}` | Required by `GenerateThinkJson` paradigm |
| Continuation syntax | `$+ %>([dest]) %<({src}) %:(_none_axis)` | Append element to list along axis |
| Grouping no axis | `&[#] %>[{src}]` (no `%+(axis)`) | Packed output with shape (1,) |

---

## 10. Placeholder Pattern for Empty List Initialization

### Problem
When a list concept (e.g., `[AOC schemas records]`) is initialized as truly empty `[]` with shape `(0,)`, and it's used as a `packed: true` input to an imperative, the MVP's `cross_product` produces empty results. This is because cross product with a (0,) dimension yields nothing.

### Solution
Initialize list concepts with a placeholder entry `{"__placeholder__": true}` instead of empty. This ensures shape `(1,)` instead of `(0,)`, allowing MVP to produce valid input combinations.

### Changes in `.pf.ncd`
```ncd
<- [AOC schemas records] | ?{flow_index}: 1.2.7
    | %{ref_axes}: [canonical]
    | %{ref_shape}: (1,)  # NOT (0,)
    | %{ref_element}: dict(...)
    <= $% %>([%({"__placeholder__": true})]) | ?{flow_index}: 1.2.7.1 | ?{sequence}: assigning
        /: ABSTRACTION: Initialize with placeholder (ensures non-empty shape)
        | %{literal<$% aoc_schemas_records>}: [{"__placeholder__": true}]
```

### Prompt Updates Required
Prompts that receive this data must be updated to ignore placeholders:
```markdown
**Note:** Ignore any entries with `"__placeholder__": true` - these are system placeholders, not real schemas.
```

### Key Points
- Shape must be `(1,)` not `(0,)` when using `packed: true`
- Placeholder is filtered out by LLM during processing
- Alternative: Modify MVP to handle empty packed values (but this changes core infrastructure)

---

## 11. LLM Output Format for GenerateThinkJson Paradigm

### Problem
The `v_PromptLocation-h_Literal-c_GenerateThinkJson-o_Literal` paradigm expects LLM responses to have a specific JSON structure. The paradigm's composition plan:
1. Calls LLM with filled prompt
2. Cleans response (removes markdown code fences)
3. Parses as JSON
4. Extracts `result` field using `formatter_tool.get(key='result')`
5. Wraps as literal

If prompts don't instruct the LLM to output this format, the `get(key='result')` step returns `None`.

### Solution
All prompts that use the `GenerateThinkJson` paradigm must instruct the LLM to output JSON with exactly two top-level keys:

```json
{
  "thinking": "Your reasoning process...",
  "result": { ... actual output ... }
}
```

### Prompt Template
```markdown
## Output Format

Return JSON with `thinking` and `result` fields:
\```json
{
  "thinking": "Your analysis...",
  "result": {
    // actual structured output here
  }
}
\```

**Important:** Your response MUST be valid JSON with exactly these two top-level keys: `thinking` and `result`.
```

### Key Points
- The `thinking` field captures LLM reasoning (useful for debugging)
- The `result` field contains the actual output that gets passed to downstream concepts
- The paradigm discards `thinking` and only preserves `result`
- All prompts in `provisions/prompts/` have been updated to use this format

---

## 12. Continuation Operator Syntax Extraction

### Problem
The continuation operator `$+` was not properly handled by the activator. The AR step failed with:
```
AR failed for continuation (+): Both 'assign_source' and 'assign_destination' must be specified.
```

### Syntax
The continuation operator has the form:
```
$+ %>([destination_list]) %<({source_element}) %:(axis_name)
```

Where:
- `%>([dest])` - the destination list to append to
- `%<({src})` - the source element to append
- `%:(axis)` - the axis name for the new dimension

### Solution
Updated `_.activate_nci.py` to properly extract:
- `assign_destination` from `%>([...])` pattern
- `assign_source` from `%<({...})` pattern
- `by_axes` from `%:(...)` pattern

### Generated working_interpretation
```json
"syntax": {
  "marker": "+",
  "assign_source": "{new AOC}",
  "assign_destination": "[AOC schemas records]",
  "by_axes": "_none_axis"
}
```

### Note on Axis Naming
When using continuation with grouped values (shape `(1,)` on `_none_axis`), use `%:(_none_axis)` to extend along that axis. This keeps the axis naming consistent with the grouping output.

---

## 13. Grouping Operations - No Axis Creation (Packed Output)

### Problem
Grouping operations (`&[{}]` for and_in, `&[#]` for or_across) were creating new axes with shape `(N,)` instead of producing a single packed element with shape `(1,)` containing all items.

### Solution
1. **Remove `%+(axis_name)` from grouping syntax** - This ensures `create_axis` is `None`
2. **Set `by_axes` to collapse `_none_axis` from each input** - This triggers per-ref mode to extract elements
3. **Result**: Shape `(1,)` with all elements wrapped in a single list/dict

### Grouping Syntax
```ncd
/: and_in grouping (creates dict with labeled keys)
<= &[{}] %>[{source1}, {source2}, {source3}] | ?{sequence}: grouping

/: or_across grouping (creates flat list)
<= &[#] %>[{source}] | ?{sequence}: grouping
```

**Important**: Do NOT include `%+(axis_name)` if you want packed output.

### Generated working_interpretation
```json
"syntax": {
  "marker": "in",           // or "across"
  "sources": ["{source1}", "{source2}", ...],
  "create_axis": null,      // null = wrap all in single element
  "by_axes": [["_none_axis"], ["_none_axis"], ...]  // collapse _none_axis from each input
}
```

### Behavior
| `create_axis` | Result Shape | Result Structure |
|---------------|--------------|------------------|
| `null` | `(1,)` | Single element containing list/dict of all items |
| `"axis_name"` | `(N,)` | N separate elements along that axis |

### Changes in `_.activate_nci.py`
```python
# Extract create_axis from %+(...), default to None if not specified
# When None, Grouper wraps all elements into a single element with shape (1,)
create_axis_match = re.search(r"%\+\(([^)]+)\)", nc_main)
create_axis = create_axis_match.group(1) if create_axis_match else None

# Build by_axes to collapse _none_axis from each value concept
# This triggers per-ref mode in Grouper and properly extracts elements
by_axes = [["_none_axis"] for _ in value_concepts]
```

### Key Points
- All value concepts have `_none_axis` (even after continuation operations - only shape changes)
- `by_axes: [["_none_axis"], ...]` tells Grouper to collapse that axis from each input
- `create_axis: null` wraps all extracted elements into a single element
- This produces shape `(1,)` which works well with `packed: true` selectors

---

## 14. Continuation with _none_axis for Grouped Data

### Problem
When using continuation (`$+`) with data from grouping operations (shape `(1,)` on `_none_axis`), the axis specified in `%:(axis)` must match the actual axis of the data.

### Solution
Use `%:(_none_axis)` for continuation when appending to lists that were created/accumulated via grouping with `create_axis: null`.

### Example
```ncd
/: Grouping produces shape (1,) on _none_axis
<- [AOC schemas extracted so far] | ?{flow_index}: 1.2.8.1.2.3
    <= &[#] %>[{AOC schema record}] | ?{sequence}: grouping

/: Continuation must use _none_axis to match
<- [AOC schemas records] | ?{flow_index}: 1.2.8.1.3
    <= $+ %>([AOC schemas records]) %<({new AOC}) %:(_none_axis) | ?{sequence}: assigning
```

---

## 15. Perception Literal Evaluation Fix

### Problem
The `perceive` method in `PerceptionRouter` was returning literal signifiers as strings instead of evaluating them. For example, `%(1)` was being perceived as the string `'1'` instead of the integer `1`. This caused script executions to fail with:
```
'can only concatenate str (not "int") to str'
```

### Solution
Updated the fallback case in `perceive` to use `ast.literal_eval` (same as `strip_sign` does):

```python
# Fallback: Unknown Norm -> Try to evaluate as Python literal
import ast
try:
    return ast.literal_eval(content)
except (ValueError, SyntaxError):
    return content
```

### Key Point
- `%(1)` now perceives to integer `1` instead of string `'1'`
- `%({'key': 'value'})` now perceives to dict `{'key': 'value'}` instead of string
- Non-literal strings remain as strings

---

## Files Modified

1. `_.pf.ncd` - Main NormCode plan
2. `_.ncds` - NormCode design specification
3. `_.activate_nci.py` - Activator script (is_invariant parsing, continuation syntax extraction)
4. `provisions/paradigms/v_PromptLocation-h_Literal-c_UserTextEditor-o_JsonLiteral.json` - New paradigm
5. `provisions/prompts/phase1/*.md` - All phase1 prompts (updated for thinking/result format)
6. `provisions/prompts/phase2/*.md` - All phase2 prompts (updated for thinking/result format)
7. `provisions/prompts/combine_verification_report.md` - Final report prompt (updated for thinking/result format)
8. `infra/_agent/_models/_perception_router.py` - Literal evaluation in perceive fallback

---

## 16. AOC Prompt Structure Alignment

### Problem
The extraction and consolidation prompts were producing AOC schemas with generic descriptions instead of executable, correlated structures that match the AOC DSL design.

### Solution
Updated both prompts to enforce:
1. **Variable bindings on triggers** (e.g., `binds: ["iid"]`)
2. **Match bindings on obligations** (e.g., `match_binds: ["iid"]`)
3. **Categorical classification** (liveness, safety, atomicity, ordering, interrupt, flush)
4. **Explicit failure conditions**
5. **Observable signal names** (not prose descriptions)

### Key Binding Variables
| Variable | Purpose | Example Usage |
|----------|---------|---------------|
| `iid` | Instruction ID correlation | `issued → commit` tracking |
| `addr` | Memory address correlation | Store-load ordering |
| `granule` | Cache line granule | LR-SC atomicity |
| `hart_id` | Core/hart identification | Multi-core operations |
| `exception_code` | Exception type | Exception handling |

### Obligation Types
| Type | Description | Example |
|------|-------------|---------|
| `any_of` | At least one must match | commit OR trap |
| `all_of` | All must be satisfied | precise + CSR saved |
| `must` | Single required condition | visible within bound |
| `conditional` | If X then Y | conflict → SC_FAIL |
| `forbidden` | Must NOT occur | no stale read |

### Category Distribution
| Category | Expected Count |
|----------|----------------|
| Instruction lifecycle | 1 |
| Memory ordering | 1 |
| Atomic operations | 1-2 |
| Exception handling | 1 |
| Interrupt delivery | 1 |
| Flush behavior | 1 |
| **Total** | **5-8** |

### DSL Alignment
The output structure now matches the Python DSL pattern:
```python
Rule("C001_InstrResolution")
    .when(Signal("instr_issued", binds=["iid"]))
    .require(AnyOf(
        Signal("commit", match_binds=["iid"]),
        Signal("trap_taken", match_binds=["iid"])
    ))
    .within(cycles=10000)
    .unless(Signal("flush_event", match_binds=["iid"]))
```

### Files Modified
- `provisions/prompts/phase1/extract_aoc_canonical.md` - Extraction with bindings
- `provisions/prompts/phase1/consolidate_aoc_schemas.md` - Consolidation with DSL structure

---

## 17. Axis Creation from List Outputs (TVA)

### Problem
When an imperative returns a list (e.g., splitting trace into cycles), the TVA step needs to create a proper axis for each element. But the activator was only setting `reference_axis_names` (list), not `axis_name` (singular), which TVA uses.

### Solution
Added `axis_name` field to value concept entries, using the first element of `ref_axes`:

```python
# In _.activate_nci.py
axis_names = parse_axes(axes_str)
primary_axis_name = axis_names[0] if axis_names else "_none_axis"

concept_entry = {
    ...
    "axis_name": primary_axis_name,  # Primary axis for TVA list-to-axis creation
    "reference_axis_names": axis_names,
    ...
}
```

### How It Works

1. Script returns a list: `[{cycle: 1, events: [...]}, {cycle: 2, events: [...]}, ...]`
2. Paradigm wraps each element individually via `formatter_tool.wrap_list`
3. TVA reads `concept.axis_name` (e.g., `"cycle"`)
4. TVA creates a Reference with shape `(N,)` along that axis

### Example

```ncd
<- [trace per cycle] | ?{flow_index}: 1.5
    | %{ref_axes}: [cycle]              # This sets axis_name to "cycle"
    | %{ref_shape}: (n_cycle,)
    | %{ref_element}: dict(cycle_num: int, events: list)
    <= ::(split RTL trace into discrete cycles) | ?{sequence}: imperative
        | %{norm_input}: v_ScriptLocation-h_Literal-c_Execute-o_ListLiteral
```

### Generated concept_repo.json

```json
{
  "concept_name": "[trace per cycle]",
  "axis_name": "cycle",
  "reference_axis_names": ["cycle"],
  ...
}
```

### Key Points
- `axis_name` is used by TVA to name the axis created from list elements
- `reference_axis_names` is the full list of expected axes (for multi-dimensional references)
- For list outputs, use the `o_ListLiteral` paradigm variant
- The paradigm's `wrap_list` step wraps each element individually, enabling axis creation

---

## 18. Specification Operator Source Selection

### Problem
The specification operator `$.` needed a way to specify multiple candidate sources (e.g., "select first available from A, B, or C").

### Solution
Added three priority levels for source specification:

1. **Annotation** (highest priority): `%{assign_sources}: [{src1}, {src2}]`
2. **Inline list**: `$. %>({output}) %<[{src1}, {src2}]`
3. **Inline single** (fallback): `$. %>({X})` - X is both output and source

### Syntax Examples

**Single source (simplest):**
```ncd
<= $. %>({all AOC schema}) | ?{sequence}: assigning
    /: Select {all AOC schema} as output
```
Result: `assign_source: "{all AOC schema}"`

**Multiple sources via annotation:**
```ncd
<= $. %>({output}) | ?{sequence}: assigning
    | %{assign_sources}: [{src1}, {src2}, {src3}]
    /: Select first available from src1, src2, or src3
```
Result: `assign_source: ["{src1}", "{src2}", "{src3}"]`

**Multiple sources via inline syntax:**
```ncd
<= $. %>({output}) %<[{src1}, {src2}] | ?{sequence}: assigning
    /: Select first available from src1 or src2
```
Result: `assign_source: ["{src1}", "{src2}"]`

### Priority Order

| Priority | Method | Pattern | Use Case |
|----------|--------|---------|----------|
| 1 (highest) | Annotation | `%{assign_sources}: [...]` | Explicit control, cleaner syntax |
| 2 | Inline list | `%<[{src1}, {src2}]` | Compact inline specification |
| 3 (fallback) | Single inline | `%>({X})` | Simple pass-through cases |

### Generated working_interpretation

```json
"syntax": {
  "marker": ".",
  "assign_source": ["{src1}", "{src2}"]  // or single string if one source
}
```

### Notes
- Annotation takes priority over inline syntax
- Mixed bracket types supported: `[{obj}, [rel], <prop>]`
- Single source returns string, multiple sources return array

---

*Last updated: 2026-01-23 (specification operator source selection)*

