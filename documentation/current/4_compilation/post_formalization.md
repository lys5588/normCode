# Post-Formalization

**Phase 3: Enriching plans with execution context—norms, resources, and tensor structure.**

---

## Overview

**Post-Formalization** is the third phase of NormCode compilation. It enriches the formal `.ncd` with annotations that configure execution and ground abstract concepts to concrete resources.

**Input**: `.ncd` (formalized with flow indices and sequences)  
**Output**: `.pf.ncd` (post-formalized, enriched with execution annotations)

**Core Task**: Answer "HOW and WITH WHAT RESOURCES?" for each operation.

### Combined Workflow Note

In practice, formalization and post-formalization are often done **simultaneously**, producing `.pf.ncd` directly from `.ncds`. This is especially common when:

- Building complex workflows iteratively
- Using LLM-assisted generation
- Needing to see the complete picture (structure + configuration)

See [Formalization - Combined Workflow](formalization.md#combined-formalization--post-formalization) for details.

---

## The Three Sub-Phases

Post-Formalization consists of three distinct sub-phases:

| Sub-Phase | Purpose | Adds |
|-----------|---------|------|
| **3.1 Re-composition** | Map to normative context | Paradigms, body faculties, perception norms |
| **3.2 Provision** | Link to concrete resources | File paths, prompt locations |
| **3.3 Syntax Re-confirmation** | Ensure tensor coherence | Axes, shapes, element types |

Each sub-phase adds a specific layer of configuration through **annotation lines**.

---

## Annotation Syntax

### How Annotations Work

Annotations are **comment lines** that appear after concept or functional lines, providing metadata without modifying the core syntax.

**Format**:
```ncd
<- {concept} | ?{flow_index}: 1.2
    |%{annotation_name}: value
    |%{another_annotation}: another value
```

**Key properties**:
- Start with `|%{...}:` (referential comments)
- Associated with the line above them
- Inherited by same flow index
- Multiple annotations per concept/functional line allowed

---

## Sub-Phase 3.1: Re-composition

### Purpose

**Re-composition** roots the `.ncd` into the **normative context of execution**—mapping abstract intent to available conventions and capabilities.

**Key Question**: *"Given what tools and conventions exist, which ones should this operation use?"*

### The Normative Context

The normative context consists of three components:

| Component | Location | Role |
|-----------|----------|------|
| **Body** | `infra/_agent/_body.py` | Agent's tools/faculties (file_system, llm, python_interpreter) |
| **Paradigms** | `infra/_agent/_models/_paradigms/` | **Action Norms** — composition patterns for operations |
| **PerceptionRouter** | `infra/_agent/_models/_perception_router.py` | **Perception Norms** — how signs become objects |

### Paradigms (Action Norms)

**Paradigms** are declarative JSON specifications that define how semantic operations execute.

**Naming Convention** (from `_paradigms/README.md`):
```
[inputs]-[composition]-[outputs].json

Examples:
h_PromptTemplate-c_Generate-o_Text.json
v_Prompt-h_FileData-c_LoadParse-o_Struct.json
h_PromptTemplateInputOther_SaveDir-c_GenerateThinkJson-Extract-Save-o_FileLocation.json
```

**Components**:
- `h_`: Horizontal input (runtime value)
- `v_`: Vertical input (setup metadata)
- `c_`: Composition steps
- `o_`: Output format (e.g., `o_Literal`, `o_FileLocation`, `o_Memo`)

**Purpose**:
- Define execution logic without hardcoding
- Reusable across plans
- Configurable via JSON
- Enable vertical (setup) vs horizontal (runtime) separation

> **Legacy Note**: Older paradigm names and documentation may use `o_Normal` for literal/direct value outputs. This has been replaced by `o_Literal` for clarity.

### Perception Norms

**Perception norms** define how perceptual signs are transmuted into actual data.

**Common Norms**:

| Norm | Purpose | Body Faculty | Example |
|------|---------|--------------|---------|
| `{file_location}` | Read file content | `body.file_system.read()` | `%{file_location}(data/input.txt)` |
| `{prompt_location}` | Load prompt template | `body.prompt_tool.read()` | `%{prompt_location}(prompts/sentiment.md)` |
| `{script_location}` | Python script path | `body.python_interpreter` | `%{script_location}(scripts/process.py)` |
| `{save_path}` | File write target | `body.file_system.write()` | `%{save_path}(output/result.json)` |
| `{memorized_parameter}` | Stored value | `body.file_system.read_memorized_value()` | `%{memorized_parameter}(config/threshold)` |
| `in-memory` | Direct value | N/A (no transmutation) | Used for computed concepts |

### Annotations Added by Re-composition

**On functional concepts** (`<=`):

| Annotation | Purpose | Example |
|------------|---------|---------|
| `\|%{norm_input}` | Paradigm ID to load | `h_PromptTemplate-c_Generate-o_Text` |
| `\|%{v_input_norm}` | Vertical input perception norm (resolved during MFP) | `{prompt_location}` |
| `\|%{h_input_norm}` | Horizontal input perception norm (resolved during MVP) | `{file_location}`, `in-memory` |
| `\|%{body_faculty}` | Body faculty to invoke | `llm`, `file_system`, `python_interpreter` |
| `\|%{o_shape}` | Output structure hint | `dict in memory`, `boolean per signal` |

> **Note on Input Norms**: Both vertical and horizontal norms are resolved by the **PerceptionRouter** during execution. The difference is *when*:
> - **Vertical (`v_input_norm`)**: Resolved during MFP (Model Function Perception) at setup time
> - **Horizontal (`h_input_norm`)**: Resolved during MVP (Memory Value Perception) at runtime
> 
> The norm `in-memory` means no perception is needed—the value is already loaded.

### Example: Re-composition

**Before Re-composition**:
```ncd
:<:{document summary} | ?{flow_index}: 1
    <= ::(summarize this text) | ?{flow_index}: 1.1 | ?{sequence}: imperative
    <- {clean text} | ?{flow_index}: 1.2
```

**After Re-composition**:
```ncd
:<:{document summary} | ?{flow_index}: 1
    <= ::(summarize this text) | ?{flow_index}: 1.1 | ?{sequence}: imperative
        |%{norm_input}: h_PromptTemplate-c_GenerateThinkJson-o_Literal
        |%{v_input_norm}: {prompt_location}
        |%{h_input_norm}: in-memory
        |%{body_faculty}: llm
        |%{o_shape}: dict in memory
    <- {clean text} | ?{flow_index}: 1.2
```

**What was added**:
- **Paradigm**: `h_PromptTemplate-c_GenerateThinkJson-o_Literal` (specifies how to execute)
- **Vertical norm**: `{prompt_location}` (prompt loaded from file during MFP setup phase)
- **Horizontal norm**: `in-memory` (input already loaded, no perception needed at runtime)
- **Body faculty**: `llm` (uses language model)
- **Output shape**: `dict in memory` (returns structured dict)

### Re-composition Process

**Algorithm**:

1. **Identify operation type** (imperative, judgement, syntactic)
2. **For semantic operations**:
   - Determine required inputs (vertical vs horizontal)
   - Select appropriate paradigm from registry
   - Identify body faculty needed
   - Assign perception norms for inputs
3. **For syntactic operations**:
   - No paradigm needed (deterministic)
   - May need perception norms for ground concepts
4. **Inject annotations** into `.ncd`

**Paradigm Selection Heuristics**:

| Operation Pattern | Likely Paradigm | Reasoning |
|-------------------|----------------|-----------|
| "generate X" | `v_PromptLocation-h_Literal-c_GenerateThinkJson-o_Literal` | LLM text generation |
| "analyze X" | `v_PromptLocation-h_Literal-c_GenerateThinkJson-o_Literal` | LLM structured analysis |
| "judge if X" | `v_PromptLocation-h_Literal-c_GenerateThinkJson-o_Boolean` | LLM judgement |
| "execute script" | `v_ScriptLocation-h_Literal-c_Execute-o_Literal` | Python execution |
| "ask user X" | `v_PromptLocation-h_Literal-c_UserTextEditor-o_JsonLiteral` | Human-in-the-loop |

### ⚠️ CRITICAL: User Input Paradigm (Human-in-the-Loop)

For user-facing imperatives (`:>:`), use paradigms with `body_faculty: user_input`:

```ncd
<= :>:(ask user to clarify specs) | ?{flow_index}: 1.2.4.1 | ?{sequence}: imperative
    | %{norm_input}: v_PromptLocation-h_Literal-c_UserTextEditor-o_JsonLiteral
    | %{v_input_norm}: prompt_location
    | %{v_input_provision}: provisions/prompts/clarify_specs.md
    | %{h_input_norm}: Literal
    | %{body_faculty}: user_input
    | %{interaction_type}: text_editor
```

**Key Annotations:**
- `%{body_faculty}: user_input` — Use user input tool instead of LLM
- `%{interaction_type}: text_editor` — Specify interaction mode

### ⚠️ Tool Name Must Match Registration

The tool name in paradigms must match the **registered name** in `tool_injection.py`:

```python
# Registration in tool_injection.py
body.user_input = self.user_input_tool
```

```json
// Paradigm JSON - use "user_input", NOT "user_input_tool"
"tool_name": "user_input"
```

**Common Error**: `Tool not found` when paradigm uses `"user_input_tool"` but it's registered as `"user_input"`.

### ⚠️ CRITICAL: LLM Output Format for GenerateThinkJson

Prompts using `c_GenerateThinkJson` paradigms **MUST** specify the output format:

```markdown
## Output Format

Return JSON with `thinking` and `result` fields:
```json
{
  "thinking": "Your analysis...",
  "result": { /* actual output */ }
}
```

**Important:** Your response MUST be valid JSON with exactly these two top-level keys.
```

**Why?** The paradigm extracts the `result` key. Missing format = `None` output.

For judgements (boolean results), `result` should be `true` or `false` (boolean, not string).

---

## Sub-Phase 3.2: Provision (Demand Declaration)

### Purpose

**Provision in Post-Formalization** declares the **demand** for concrete resources within the normative context established by re-composition.

**Key Question**: *"What resources will be needed and where should they be located?"*

**Important Distinction**: This sub-phase **declares demands**—it does not validate or resolve them. Actual resource validation and resolution happens during [Provision in Activation](provision_in_activation.md).

| Phase | Role | What Happens |
|-------|------|--------------|
| **Post-Formalization 3.2** | **Demand** | Annotate paths: "I need a prompt at X" |
| **Activation (Provision)** | **Supply** | Validate and resolve: "X exists and contains valid content" |

**Relationship to Re-composition**:
- **Re-composition says**: "Use `{prompt_location}` norm with `llm` faculty"
- **Provision (Demand) says**: "The prompt should be at `provision/prompts/sentiment_extraction.md`"
- **Activation (Supply) verifies**: "The file exists and is valid"

### Annotations Added by Provision (Demand)

These annotations **declare resource demands**. They specify *where* resources should be found, but do not validate their existence. Validation occurs during [Provision in Activation](provision_in_activation.md).

**On value concepts** (`<-`) for ground concepts:

| Annotation | Purpose | Example |
|------------|---------|---------|
| `\|%{file_location}` | Path to data file (demand) | `provision/data/price_data.json` |
| `\|%{ref_element}: perceptual_sign` | Mark as perceptual sign | Indicates lazy loading |
| `\|%{literal<$% name>}: value` | Literal initialization value | `[{"__placeholder__": true}]` |

**On functional concepts** (`<=`) for paradigm inputs:

| Annotation | Purpose | Example |
|------------|---------|---------|
| `\|%{v_input_provision}` | Path to prompt/script (demand) | `provision/prompts/sentiment.md` |
| `\|%{value_order}` | Explicit input concept ordering | `[{concept1}, {concept2}]` |

> **Note**: At this stage, these are just string paths. The files may or may not exist. Activation's provision step will validate and resolve these demands. See [Provision in Activation](provision_in_activation.md) for the supply side.

### Value Selectors (Controlling Input Processing)

When bundled data (dicts, lists) is passed to imperatives, MVP may unpack them unexpectedly. **Value selectors** control how inputs are processed.

| Annotation | Purpose | Example |
|------------|---------|---------|
| `%{selector_packed}: true` | Keep as single input (don't unpack) | Bundled data stays bundled |
| `%{selector_source}: {concept}` | Read from another concept | Select from different source |
| `%{selector_key}: key_name` | Select specific key from dict | Extract "isa" field |
| `%{selector_index}: N` | Select item at index from list | Get first item |

**Example: Keeping Bundled Data Together**

```ncd
<- {all user inputs}<:{1}> | ?{flow_index}: 1.2.8.1.2.2
    | %{ref_axes}: [_none_axis]
    | %{ref_element}: dict
    | %{selector_packed}: true
```

### Explicit Value Order (`%{value_order}`)

When an imperative has many value concepts but only needs a subset as inputs:

```ncd
<= ::(combine all testing information) | ?{flow_index}: 1.1 | ?{sequence}: imperative
    | %{norm_input}: v_PromptLocation-h_Literal-c_GenerateThinkJson-o_Literal
    | %{value_order}: [{all testing information}]
```

This ensures only `{all testing information}` is passed as `$input_1`, even if the inference tree has many value concepts.

### ⚠️ Placeholder Pattern for Empty List Initialization

**Problem**: Empty lists `[]` with shape `(0,)` cause `cross_product` to produce nothing when used with `packed: true`.

**Solution**: Initialize with a placeholder:

```ncd
<- [AOC schemas records] | ?{flow_index}: 1.2.7
    | %{ref_axes}: [canonical]
    | %{ref_shape}: (1,)  # NOT (0,)!
    | %{ref_element}: dict(...)
    <= $% %>([%({"__placeholder__": true})]) | ?{flow_index}: 1.2.7.1 | ?{sequence}: assigning
        | %{literal<$% aoc_schemas_records>}: [{"__placeholder__": true}]
```

**Key Points**:
- Shape must be `(1,)` not `(0,)` when using `packed: true`
- Update prompts to ignore entries with `"__placeholder__": true`

### Example: Provision (Demand)

**Before Provision**:
```ncd
:<:{sentiment analysis} | ?{flow_index}: 1
    <= ::(analyze sentiment) | ?{flow_index}: 1.1 | ?{sequence}: imperative
        |%{norm_input}: h_PromptTemplate-c_GenerateThinkJson-o_Literal
        |%{v_input_norm}: {prompt_location}
        |%{h_input_norm}: {file_location}
    <- {customer reviews} | ?{flow_index}: 1.2
```

**After Provision**:
```ncd
:<:{sentiment analysis} | ?{flow_index}: 1
    <= ::(analyze sentiment) | ?{flow_index}: 1.1 | ?{sequence}: imperative
        |%{norm_input}: h_PromptTemplate-c_GenerateThinkJson-o_Literal
        |%{v_input_norm}: {prompt_location}
        |%{v_input_provision}: provision/prompts/sentiment_extraction.md
        |%{h_input_norm}: {file_location}
    <- {customer reviews} | ?{flow_index}: 1.2
        |%{file_location}: provision/data/reviews.json
        |%{ref_element}: perceptual_sign
```

**What was added** (as demands):
- **Prompt path demand**: `provision/prompts/sentiment_extraction.md` — declares where the prompt should be
- **Data path demand**: `provision/data/reviews.json` — declares where data should be located
- **Perceptual sign marker**: Indicates `{customer reviews}` is initially a pointer, not loaded data

> **Important**: These paths are demands, not validated resources. The [Provision in Activation](provision_in_activation.md) step will verify these files exist and are properly formatted.

### Provision (Demand) Process

**Algorithm**:

1. **Identify ground concepts** (marked with `:>:` or no parent inference)
2. **Determine perception norm** from re-composition
3. **Declare resource paths** (these are demands, not validated):
   - Specify expected `provision/` directory structure
   - Assign logical paths based on concept names and phases
   - Use configuration or user input for custom paths
4. **Inject path annotations** as demands
5. **Mark as perceptual signs** if lazy loading

> **Note**: This step does NOT validate that files exist. It declares WHERE files SHOULD be. Actual validation happens during [Provision in Activation](provision_in_activation.md).

**Ground Concept Identification**:

A concept is **ground** if:
- Marked with `:>:` (explicit input marker)
- Created by `$%` (abstraction operator)
- Has no parent inference (leaf node with no `<=` child)
- Marked in compilation configuration

---

## Sub-Phase 3.3: Syntax Re-confirmation

### Purpose

**Syntax Re-confirmation** ensures **tensor coherence** by declaring reference structure (axes, shape, element type) for each concept.

**Key Question**: *"What is the dimensional structure of each concept's data?"*

**Why It Matters**:
- Operations need to know input dimensions
- Syntactic operators manipulate axes
- Type mismatches cause runtime errors
- Documentation for developers

### Axes of Indeterminacy

**Axes** are named dimensions that model indeterminacy in data.

**Example**:
```
"A student" has axes:
- [school]: which school?
- [class]: which class?
- [nationality]: which nationality?
```

A reference with these axes is a 3D tensor where each cell is a student.

**Axis Conventions**:

| Axis Name | Meaning | Example |
|-----------|---------|---------|
| `[_none_axis]` | Singleton (no indeterminacy) | Single value |
| `[concept_name]` | One element per concept instance | `[signal]`, `[document]` |
| `[outer_axis, inner_axis]` | Nested structure | 2D or higher dimensional |

### Element Type Conventions

| Element Type | Meaning | Example |
|--------------|---------|---------|
| `dict(key1: type1, ...)` | Structured dictionary | `dict(sentiment: str, score: float)` |
| `%{truth value}` | Boolean (from judgement) | Output of `::<>` |
| `perceptual_sign` | Pointer requiring transmutation | Ground concepts before MVP |
| `str`, `int`, `float` | Primitives | Simple values |

### Annotations Added by Syntax Re-confirmation

**On concepts** (both `<-` and `<=`):

| Annotation | Purpose | Example |
|------------|---------|---------|
| `\|%{ref_axes}` | Named axes of the reference | `[_none_axis]`, `[signal]` |
| `\|%{ref_shape}` | Tensor shape | `(1,)`, `(n_signal,)` |
| `\|%{ref_element}` | Element type/schema | `dict(...)`, `%{truth value}` |
| `\|%{ref_skip}` | Filter documentation | `filtered by <condition>` |
| `\|%{is_invariant}: true` | Persist across loop iterations | Loop state containers |

### Invariant Concepts (Loop State Management)

Concepts that must persist their references across loop iterations need the `is_invariant` annotation:

```ncd
<- [AOC schemas records] | ?{flow_index}: 1.2.8.1.3
    | %{ref_axes}: [canonical]
    | %{ref_shape}: (n_canonical,)
    | %{ref_element}: dict(...)
    | %{is_invariant}: true

<- [counters] | ?{flow_index}: 1.2.8.1.5
    | %{ref_axes}: [counter]
    | %{ref_shape}: (n_counter,)
    | %{ref_element}: int
    | %{is_invariant}: true
```

**Without `is_invariant: true`**, references may be reset between iterations.

### Example: Syntax Re-confirmation

**Before Syntax Re-confirmation**:
```ncd
:<:{sentiment analysis} | ?{flow_index}: 1
    <= ::(analyze sentiment) | ?{flow_index}: 1.1 | ?{sequence}: imperative
    <- {customer reviews} | ?{flow_index}: 1.2
```

**After Syntax Re-confirmation**:
```ncd
:<:{sentiment analysis} | ?{flow_index}: 1
    |%{ref_axes}: [_none_axis]
    |%{ref_shape}: (1,)
    |%{ref_element}: dict(sentiment: str, score: float, confidence: float)
    <= ::(analyze sentiment) | ?{flow_index}: 1.1 | ?{sequence}: imperative
    <- {customer reviews} | ?{flow_index}: 1.2
        |%{ref_axes}: [review]
        |%{ref_shape}: (n_review,)
        |%{ref_element}: perceptual_sign
```

**What was added**:
- **Root axes**: `[_none_axis]` (single result)
- **Root shape**: `(1,)` (one element)
- **Root element**: Structured dict with schema
- **Input axes**: `[review]` (collection of reviews)
- **Input shape**: `(n_review,)` (variable number)
- **Input element**: `perceptual_sign` (not yet loaded)

### Continuation Operator (`$+`) Syntax

The continuation operator appends elements to lists:

```ncd
<= $+ %>([destination_list]) %<({source_element}) %:(axis_name) | ?{sequence}: assigning
```

**Components**:
- `%>([dest])` — Destination list to append to
- `%<({src})` — Source element to append
- `%:(axis)` — Axis name for the new dimension

**Example**:
```ncd
<- [AOC schemas records] | ?{flow_index}: 1.2.8.1.3
    | %{is_invariant}: true
    <= $+ %>([AOC schemas records]) %<({new AOC}) %:(_none_axis) | ?{flow_index}: 1.2.8.1.3.1 | ?{sequence}: assigning
```

**Note**: Use `%:(_none_axis)` when appending to lists with grouped values (shape `(1,)` on `_none_axis`).

### Grouping Operations (`&[{}]` and `&[#]`)

Grouping operators bundle multiple inputs:

| Operator | Name | Result | Use Case |
|----------|------|--------|----------|
| `&[{}]` | and_in | Dict with labeled keys | Bundle named items |
| `&[#]` | or_across | Flat list | Collect items |

**Grouping WITHOUT Axis Creation** (packed output):

```ncd
<= &[#] %>[{source}] | ?{sequence}: grouping
    /: NO %+(axis) = create_axis: null → shape (1,)
```

**Grouping WITH Axis Creation**:

```ncd
<= &[#] %>[{source}] %+(new_axis) | ?{sequence}: grouping
    /: %+(new_axis) = create_axis: "new_axis" → shape (N,)
```

| `create_axis` | Result Shape | Result Structure |
|---------------|--------------|------------------|
| `null` (no `%+`) | `(1,)` | Single element containing list/dict |
| `"axis_name"` | `(N,)` | N separate elements along axis |

### Common Restructuring Patterns

Sometimes axis analysis reveals the need to restructure the plan:

| Problem | Solution | Operator |
|---------|----------|----------|
| Need to process each element separately | Add loop | `*.` (looping) |
| Need to collapse axis into flat list | Add grouping | `&[#]` (group across) |
| Need to bundle items with labels | Add grouping | `&[{}]` (group in) |
| Need to append to list in loop | Add continuation | `$+` with `is_invariant` |
| Need to protect an axis from collapse | Add protection | `%^<$!={axis}>` |
| Need element-wise truth mask | Adjust assertion | `<FOR EACH ... True>` |
| Need single collapsed boolean | Adjust assertion | `<ALL True>` or `<ALL False>` |

### Complete Loop Structure Pattern

Loops with mutable state follow this pattern:

```ncd
/: Initialize BEFORE loop (sibling, not child)
<- [counters] | ?{flow_index}: 1.2.6
    | %{ref_axes}: [counter]
    | %{ref_shape}: (1,)
    <= $% %>([%(1)]) | ?{flow_index}: 1.2.6.1 | ?{sequence}: assigning
        | %{literal<$% counters>}: [1]

<- [records] | ?{flow_index}: 1.2.7
    | %{ref_axes}: [canonical]
    | %{ref_shape}: (1,)
    <= $% %>([%({"__placeholder__": true})]) | ?{flow_index}: 1.2.7.1 | ?{sequence}: assigning
        | %{literal<$% records>}: [{"__placeholder__": true}]

/: Loop
<- [results] | ?{flow_index}: 1.2.8
    <= *. %>([counters]) %<({item}) %:({counter}) %@(1) | ?{flow_index}: 1.2.8.1 | ?{sequence}: looping
        
        /: Loop return
        <= $. %>({item}) | ?{flow_index}: 1.2.8.1.1 | ?{sequence}: assigning
        
        /: Compute item
        <- {item} | ?{flow_index}: 1.2.8.1.2
            <= ::(extract item) | ?{flow_index}: 1.2.8.1.2.1 | ?{sequence}: imperative
            <- {input}<:{1}> | ?{flow_index}: 1.2.8.1.2.2
                | %{selector_packed}: true
        
        /: Update persistent state (invariant)
        <- [records] | ?{flow_index}: 1.2.8.1.3
            | %{is_invariant}: true
            <= $+ %>([records]) %<({item}) %:(_none_axis) | ?{flow_index}: 1.2.8.1.3.1 | ?{sequence}: assigning
        
        /: Check termination
        <- <done> | ?{flow_index}: 1.2.8.1.4
            <= ::(check if complete)<ALL True> | ?{flow_index}: 1.2.8.1.4.1 | ?{sequence}: judgement
        
        /: Conditional counter increment (only if NOT done)
        <- [counters] | ?{flow_index}: 1.2.8.1.5
            | %{is_invariant}: true
            <= $+ %>([counters]) %<({next}) %:(counter) | ?{flow_index}: 1.2.8.1.5.1 | ?{sequence}: assigning
                <= @:!(<done>) | ?{flow_index}: 1.2.8.1.5.1.1 | ?{sequence}: timing
                <* <done> | ?{flow_index}: 1.2.8.1.5.1.2
    
    <- [counters] | ?{flow_index}: 1.2.8.2
    <* {counter}<$([counters])*> | ?{flow_index}: 1.2.8.3
```

**Key Elements**:
1. **Initialize before loop** — State containers as siblings, not children
2. **Loop return** — Explicit `$. %>({item})` to specify what gets collected
3. **Invariant state** — `%{is_invariant}: true` on mutable containers
4. **Conditional operations** — Timing gate `@:!` for conditional execution

**Example Restructuring**:

**Problem**: Judgement needs to evaluate each signal separately, but current structure evaluates all at once.

**Before**:
```ncd
<- <signals valid> | ?{flow_index}: 1
    |%{ref_axes}: [_none_axis]  # WRONG: Should have [signal] axis
    <= ::(validate signals)<ALL True> | ?{flow_index}: 1.1
    <- [signals] | ?{flow_index}: 1.2
        |%{ref_axes}: [signal]
```

**After** (with loop added):
```ncd
<- [all <signal valid>] | ?{flow_index}: 1
    |%{ref_axes}: [signal]
    |%{ref_element}: %{truth value}
    <= *. %>({signals}) %<({valid}) %:({signal}) %@(1) | ?{flow_index}: 1.1 | ?{sequence}: looping
        <= $. %>({valid}) | ?{flow_index}: 1.1.1 | ?{sequence}: assigning
        <- <signal valid> | ?{flow_index}: 1.1.2
            |%{ref_axes}: [_none_axis]
            |%{ref_element}: %{truth value}
            <= ::(validate signal)<ALL True> | ?{flow_index}: 1.1.2.1 | ?{sequence}: judgement
            <- {signal}*1 | ?{flow_index}: 1.1.2.2
    <- [signals] | ?{flow_index}: 1.2
        |%{ref_axes}: [signal]
    <* {signal}<$({signals})*> | ?{flow_index}: 1.3
```

**Note**: `{signal}*1` is now `1.1.2.2` (sibling of `1.1.2.1`), following the sibling pattern.

### Syntax Re-confirmation Process

**Algorithm**:

1. **Analyze each concept**:
   - Determine type (`{}`, `[]`, `<>`)
   - Infer axes from context (loops, groupings)
   - Determine element type from operation output
2. **Check coherence**:
   - Input axes match operation expectations?
   - Judgement assertions match axes?
   - Grouping collapses correct axes?
3. **Restructure if needed**:
   - Add loops for element-wise processing
   - Add groupings for axis manipulation
   - Adjust truth assertions
4. **Inject annotations**

---

## Complete Post-Formalization Example

### Before Post-Formalization

```ncd
:<:{investment decision} | ?{flow_index}: 1
    <= ::(synthesize recommendation) | ?{flow_index}: 1.1 | ?{sequence}: imperative
    <- {risk analysis} | ?{flow_index}: 1.2
        <= ::(analyze risk) | ?{flow_index}: 1.2.1 | ?{sequence}: imperative
        <- {price data} | ?{flow_index}: 1.2.2
    <- {sentiment score} | ?{flow_index}: 1.3
        <= ::(analyze sentiment) | ?{flow_index}: 1.3.1 | ?{sequence}: imperative
        <- {news articles} | ?{flow_index}: 1.3.1.1
```

### After Post-Formalization

```ncd
:<:{investment decision} | ?{flow_index}: 1
    |%{ref_axes}: [_none_axis]
    |%{ref_shape}: (1,)
    |%{ref_element}: dict(decision: str, confidence: float, reasoning: str)
    <= ::(synthesize recommendation from {1} and {2}) | ?{flow_index}: 1.1 | ?{sequence}: imperative
        |%{norm_input}: h_PromptTemplate-c_GenerateThinkJson-o_Literal
        |%{v_input_norm}: {prompt_location}
        |%{v_input_provision}: provision/prompts/investment_synthesis.md
        |%{h_input_norm}: in-memory
        |%{body_faculty}: llm
        |%{o_shape}: dict in memory
    <- {risk analysis}<:{1}> | ?{flow_index}: 1.2
        |%{ref_axes}: [_none_axis]
        |%{ref_shape}: (1,)
        |%{ref_element}: dict(risk_level: str, factors: list)
        <= ::(analyze risk based on {1}) | ?{flow_index}: 1.2.1 | ?{sequence}: imperative
            |%{norm_input}: h_PromptTemplate-c_GenerateThinkJson-o_Literal
            |%{v_input_norm}: {prompt_location}
            |%{v_input_provision}: provision/prompts/risk_analysis.md
            |%{h_input_norm}: {file_location}
        <- {price data}<:{1}> | ?{flow_index}: 1.2.2
            |%{file_location}: provision/data/price_history.json
            |%{ref_axes}: [date]
            |%{ref_shape}: (n_date,)
            |%{ref_element}: perceptual_sign
    <- {sentiment score}<:{2}> | ?{flow_index}: 1.3
        |%{ref_axes}: [_none_axis]
        |%{ref_shape}: (1,)
        |%{ref_element}: float
        <= ::(analyze sentiment) | ?{flow_index}: 1.3.1 | ?{sequence}: imperative
            |%{norm_input}: h_Data-c_ThinkJSON-o_Literal
            |%{h_input_norm}: {file_location}
            |%{body_faculty}: llm
        <- {news articles} | ?{flow_index}: 1.3.1.1
            |%{file_location}: provision/data/recent_news.json
            |%{ref_axes}: [article]
            |%{ref_shape}: (n_article,)
            |%{ref_element}: perceptual_sign
```

### What Was Added

**Re-composition**:
- Paradigm IDs for all semantic operations
- Perception norms (prompt_location, file_location, in-memory)
- Body faculties (llm)
- Output shape hints

**Provision**:
- Prompt paths (`provision/prompts/*.md`)
- Data paths (`provision/data/*.json`)
- Perceptual sign markers

**Syntax Re-confirmation**:
- Axes for all concepts (`[_none_axis]`, `[date]`, `[article]`)
- Shapes (`(1,)`, `(n_date,)`, `(n_article,)`)
- Element types (dict schemas, perceptual_sign, float)

---

## Post-Formalization Validation

### Checklist

Before moving to activation:

**Re-composition**:
- [ ] All semantic operations have paradigms
- [ ] Perception norms specified
- [ ] Body faculties assigned
- [ ] Paradigm IDs exist in registry
- [ ] User-facing operations (`:>:`) have `body_faculty: user_input`

**Provision**:
- [ ] Ground concepts have resource paths
- [ ] File paths are valid
- [ ] Prompt paths exist
- [ ] Perceptual signs marked
- [ ] Empty lists initialized with placeholders (not `(0,)` shape)
- [ ] Explicit `%{value_order}` where needed

**Syntax Re-confirmation**:
- [ ] All concepts have axes declared
- [ ] Shapes are consistent
- [ ] Element types match operations
- [ ] No axis mismatches
- [ ] Loop state containers have `%{is_invariant}: true`

**⚠️ Critical Checks (Common Bugs)**:
- [ ] Prompts specify `{"thinking": "...", "result": ...}` format for GenerateThinkJson
- [ ] Bundled data inputs have `%{selector_packed}: true`
- [ ] Tool names in paradigms match registered names
- [ ] Loop return operations explicitly specified (`$. %>({item})`)

### Common Issues

| Issue | Symptom | Fix |
|-------|---------|-----|
| **Missing paradigm** | Semantic operation without `\|%{norm_input}` | Add paradigm annotation |
| **Invalid path** | File path doesn't exist | Correct path or create file |
| **Axis mismatch** | Operation expects [axis] but gets [_none_axis] | Restructure with loop or grouping |
| **Wrong element type** | Expects dict but gets perceptual_sign | Add transmutation step |
| **Missing perceptual sign marker** | Ground concept without `\|%{ref_element}: perceptual_sign` | Add marker |

### ⚠️ Critical Issues from Debugging

| Issue | Symptom | Fix |
|-------|---------|-----|
| **`None` from LLM** | Paradigm extracts `result` but LLM returns different structure | Update prompt to specify `{"thinking": "...", "result": ...}` |
| **Tool not found** | Paradigm uses wrong tool name | Use registered name (e.g., `"user_input"` not `"user_input_tool"`) |
| **Judgement always False** | LLM returns `"true"` (string) not `true` (boolean) | Update prompt to specify boolean output |
| **Empty cross_product** | List initialized with `(0,)` shape | Use placeholder with `(1,)` shape |
| **Too many inputs** | Automatic value_order picks up all nested concepts | Use explicit `%{value_order}` |
| **Dict unpacked** | Bundled data not marked as packed | Add `%{selector_packed}: true` |
| **Loop state reset** | References lost between iterations | Add `%{is_invariant}: true` |
| **Infinite extraction** | No duplicate detection in prompt | Add termination criteria to prompt |

---

## Tools and Automation

### Automated Post-Formalization

**Command** (if implemented):
```bash
python compiler.py post-formalize formalized.ncd
```

**What it does**:
1. Runs re-composition (paradigm selection)
2. Runs provision (path resolution)
3. Runs syntax re-confirmation (axis inference)
4. Outputs enriched `.ncd`

### Manual Post-Formalization

**Steps**:
1. **Re-composition**:
   - For each semantic operation, select paradigm
   - Assign perception norms
   - Inject annotations
2. **Provision**:
   - Identify ground concepts
   - Resolve resource paths
   - Add path annotations
3. **Syntax Re-confirmation**:
   - Analyze axes for each concept
   - Determine element types
   - Restructure if needed
   - Inject annotations

### Configuration Files

**Paradigm Registry**: `infra/_agent/_models/_paradigms/`
- Each paradigm is a JSON file
- Naming follows convention
- Can be extended

**Provision Configuration**: `provision/`
- `provision/data/` - Data files
- `provision/prompts/` - Prompt templates
- `provision/scripts/` - Python scripts

---

## Next Steps

After post-formalization, your enriched `.ncd` file moves to:

- **[Activation](activation.md)** - Transform to JSON repositories for orchestrator execution
- **[Provision in Activation](provision_in_activation.md)** - Where declared demands are validated and resolved

---

## Summary

### Key Takeaways

| Concept | Insight |
|---------|---------|
| **Three sub-phases** | Re-composition, Provision (Demand), Syntax Re-confirmation |
| **Annotations** | Comment lines (`\|%{...}:`) that configure execution |
| **Normative context** | Body faculties, paradigms, perception norms |
| **Resource demands** | File paths declared but not yet validated |
| **Tensor coherence** | Axes, shapes, element types |
| **Restructuring** | Sometimes needed to fix axis mismatches |

### ⚠️ Critical Lessons from Debugging

| Lesson | Detail |
|--------|--------|
| **LLM output format** | Prompts MUST specify `{"thinking": "...", "result": ...}` for GenerateThinkJson |
| **User input paradigms** | Need `body_faculty: user_input` annotation |
| **Tool name matching** | Use registered name, not class name |
| **Value selectors** | Use `%{selector_packed}: true` for bundled data |
| **Explicit value order** | Use `%{value_order}` when automatic inference picks up too many concepts |
| **Placeholder initialization** | Use `(1,)` shape with placeholder, not `(0,)` |
| **Invariant loop state** | Add `%{is_invariant}: true` to persistent loop variables |
| **Loop returns** | Explicitly specify what gets collected with `$. %>({item})` |

### The Demand/Supply Model

| Phase | Role | What Happens |
|-------|------|--------------|
| **Post-Formalization 3.2** | **Demand** | Declare resource paths in annotations |
| **Activation (Provision)** | **Supply** | Validate paths, resolve mappings, include resources |

### The Post-Formalization Promise

**Post-Formalization bridges intent and execution**:

1. Abstract operations → Concrete paradigm demands
2. Conceptual data → File path demands (not yet validated)
3. Implicit structure → Explicit axes and types
4. Loop state management → Invariant annotations
5. Input control → Value selectors and explicit ordering
6. Ready for Activation (where demands become validated resources)

**Result**: A fully annotated `.pf.ncd` plan with declared resource demands, ready for Activation to supply and validate.

---

**Ready to generate repositories?** Continue to [Activation](activation.md) to transform your enriched `.pf.ncd` into JSON repositories that the orchestrator can execute.
