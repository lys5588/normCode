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

## Takeaways for Future Automation

1. **Initialize loop bases in GROUND** - Don't declare them after the loop
2. **Loop control goes INSIDE** - Judgement and conditional append are children, not siblings
3. **Explicit input collection reference** - Loops need `<- [collection]` as a sibling alongside `<* {context}`
4. **First-executed, first-written applies to loop internals too** - The loop body structure matters
5. **Prompt variable format** - Use `$input_x` wrapped in `<descriptive_name>$input_x</descriptive_name>` XML tags

