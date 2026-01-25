# Automation Failure Journal

This document records derivation mistakes made during automated `.ncds` generation and their corrections, to improve future automation.

---

## 2026-01-26: Initial Derivation of Canvas Assistant

**Task**: Derive `_.instruction.md` into `_.ncds`

### Failure 1: Loop Base Placement

**What I did wrong**:
```ncds
/: At the END of the file, outside the loop:
<- [on-going messages]
    /: Invariant: accumulates across iterations
```

**Why it's wrong**: The loop base collection `[on-going messages]` was placed at the bottom of the file, outside the loop structure. In NormCode, the loop base must be **initialized in GROUND** before the loop starts.

**Correct pattern**:
```ncds
/: In GROUND CONCEPTS section, before the loop:
<- [on-going messages]
    <= initiate an empty list.
    /: Invariant: accumulates across iterations
```

**Lesson**: Self-seeding loops need their base collection initialized as a GROUND concept, not declared after the loop.

---

### Failure 2: Loop Control Placement

**What I did wrong**:
```ncds
<- [all canvas statuses]
    <= for each message in conversation
        <= return canvas status for this iteration
        ...
    
    /: OUTSIDE the return operation (sibling to loop operator):
    <- <session should end>
    <- [on-going messages]  /: conditional append
```

**Why it's wrong**: I placed the loop control (judgement and conditional append) as **siblings** of the loop operator, outside the loop body. They should be **children** inside the loop iteration.

**Correct pattern**:
```ncds
<- [all canvas statuses]
    <= for each message in conversation
        <= return canvas status for this iteration
            ...
            /: INSIDE the return operation (children):
            <- <session should end>
            <- [on-going messages]  /: conditional append
```

**Lesson**: Loop control (termination judgement and conditional append) must be inside the loop body as children of the return operation, not as siblings outside.

---

### Failure 3: Loop Input Collection Placement

**What I did wrong**:
```ncds
<- [all canvas statuses]
    <= for each message in conversation
        <= return canvas status for this iteration
        ...
    
    /: Loop context at the end, but missing the input collection reference:
    <* {message}
```

**Why it's wrong**: The loop needs an explicit reference to the collection being iterated over (`[on-going messages]`) as a **value sibling** inside the loop operator scope.

**Correct pattern**:
```ncds
<- [all canvas statuses]
    <= for each message in conversation
        <= return canvas status for this iteration
        ...
    
    /: Input collection as value sibling:
    <- [on-going messages]
    
    /: Loop context variable:
    <* {message}
```

**Lesson**: Loops require the input collection as an explicit `<-` sibling alongside the `<*` context variable.

---

## Summary of Loop Patterns

### Correct Self-Seeding Loop Structure:

```ncds
/: GROUND - Initialize base
<- [base collection]
    <= initiate empty

/: LOOP
<- [results]
    <= for each item
        <= return result
        
        /: ... loop body ...
        
        /: INSIDE: Loop control
        <- <should stop>
            <= judge termination
        <- [base collection]
            <= conditional append
                <= if should NOT stop
                <* <should stop>
            <- {item}
    
    /: SIBLING: Input collection reference
    <- [base collection]
    
    /: SIBLING: Context variable
    <* {item}
```

---

---

## 2026-01-26: Prompt Template Variable Format

**Task**: Correct variable placeholder format in prompt templates

### Failure 4: Incorrect Variable Placeholder Format

**What I did wrong**:
```markdown
## User Message

$input_1

## Available Commands

$input_2
```

Or even worse:
```markdown
**Conversation History ({1}):**
{1}
```

**Why it's wrong**: Variable placeholders should follow a consistent pattern:
1. Use `$input_x` format (not `{1}` or other variations)
2. Wrap in descriptive XML tags for clarity and safe parsing

**Correct pattern**:
```markdown
## User Message

<user_message>
$input_1
</user_message>

## Available Commands

<command_schema>
$input_2
</command_schema>
```

**Lesson**: Prompt templates should use `$input_x` placeholders wrapped in XML tags with descriptive names. This ensures:
- Consistent variable substitution
- Clear boundaries for multi-line content
- Self-documenting placeholder purpose

---

## 2026-01-26: Hardcoded Ground Values

**Task**: Post-formalize hardcoded file paths

### Failure 5: Unnecessary Assigning Sequence for Hardcoded Ground

**What I did wrong**:
```ncd
<- {command schema file path}<:{1}> | ?{flow_index}: 1.2.2
    | %{literal_value}: "provisions/schemas/canvas_commands.json"
    <= $% %>({%(provisions/schemas/canvas_commands.json)}) | ?{flow_index}: 1.2.2.1 | ?{sequence}: assigning
        /: Literal file path
```

**Why it's wrong**: For hardcoded ground values (like file paths that never change), adding an assigning sequence (`$%`) is unnecessary abstraction. The value is already known at compile time and specified in `%{literal_value}`.

**Correct pattern**:
```ncd
<- {command schema file path}<:{1}> | ?{flow_index}: 1.2.2
    | %{ref_axes}: [_none_axis]
    | %{ref_shape}: (1,)
    | %{ref_element}: str
    | %{literal_value}: "provisions/schemas/canvas_commands.json"
    | %{is_ground}: true
    /: Hardcoded ground - no functional concept needed
```

**Lesson**: Hardcoded ground values need:
1. `%{literal_value}` annotation with the actual value
2. `%{is_ground}: true` to mark it as ground
3. NO functional concept (`<=`) - the annotations are sufficient

---

## 2026-01-26: Paradigm Output Naming Convention

**Task**: Name paradigm output types correctly

### Failure 6: Using `o_Status` Instead of `o_LiteralStatus`

**What I did wrong**:
```
h_Literal-c_CanvasIntegrationSay-o_Status.json
h_Literal-c_CanvasIntegrationExecute-o_Status.json
```

**Why it's wrong**: The output naming convention uses `o_[Collection]Type` format. When the output is a literal (no perception sign), it should be prefixed with `Literal`. Using just `o_Status` implies there's a special "Status" perception norm, but status results are just plain dictionaries - literals.

**Correct pattern**:
```
h_Literal-c_CanvasIntegrationSay-o_LiteralStatus.json
h_Literal-c_CanvasIntegrationExecute-o_LiteralStatus.json
```

**Lesson**: Output types follow the pattern:
- `o_Literal` - generic literal output
- `o_LiteralStatus` - literal dict representing status/result
- `o_Boolean` - truth value output
- `o_ListLiteral` - list of literals (enables axis creation)
- `o_FileLocation` - perception sign pointing to file

If the output is just data without a perception sign, prefix with `Literal`.

---

## Takeaways for Future Automation

1. **Initialize loop bases in GROUND** - Don't declare them after the loop
2. **Loop control goes INSIDE** - Judgement and conditional append are children, not siblings
3. **Explicit input collection reference** - Loops need `<- [collection]` as a sibling alongside `<* {context}`
4. **First-executed, first-written applies to loop internals too** - The loop body structure matters
5. **Prompt variable format** - Use `$input_x` wrapped in `<descriptive_name>$input_x</descriptive_name>` XML tags
6. **Hardcoded grounds need no functional concept** - Use `%{literal_value}` + `%{is_ground}: true`, skip the `<= $%` sequence
7. **Output naming convention** - Use `o_Literal[Type]` for literal outputs (no perception sign), e.g., `o_LiteralStatus` not `o_Status`

