# Paradigm Definitions

Paradigms are declarative JSON specifications that define how operations execute.

## Naming Convention

```
[inputs]-[composition]-[outputs].json

Prefixes:
  h_ = horizontal input (runtime value)
  v_ = vertical input (setup metadata)
  c_ = composition steps
  o_ = output format
```

## Paradigms Used in This Plan

### File System Paradigms
- `h_LiteralPath-c_ReadFile-o_Literal.json` - Read file content from path

### LLM Paradigms
- `v_PromptLocation-h_Literal-c_GenerateThinkJson-o_Literal.json` - LLM generation with JSON output
- `v_PromptLocation-h_Literal-c_GenerateThinkJson-o_Boolean.json` - LLM judgement returning boolean

### Python Interpreter Paradigms
- `v_ScriptLocation-h_Literal-c_Execute-o_Literal.json` - Execute Python script, return scalar
- `v_ScriptLocation-h_Literal-c_Execute-o_ListLiteral.json` - Execute Python script, return list (enables axis creation)

## Paradigm Usage in RTL AOC Verification

| Paradigm | Used For |
|----------|----------|
| `h_LiteralPath-c_ReadFile-o_Literal` | Loading ISA spec, MA spec, RTL trace |
| `v_PromptLocation-h_Literal-c_GenerateThinkJson-o_Literal` | Decomposing specs, extracting AOC, consolidating schemas, updating rules, verifying cycles, generating report |
| `v_PromptLocation-h_Literal-c_GenerateThinkJson-o_Boolean` | Judging if more canonicals remain, validating AOC rules |
| `v_ScriptLocation-h_Literal-c_Execute-o_Literal` | Incrementing loop counter |
| `v_ScriptLocation-h_Literal-c_Execute-o_ListLiteral` | Splitting trace into cycles |

## Prompt Format Requirements

LLM paradigms expect prompts to return JSON with this structure:

```json
{
  "thinking": "reasoning here",
  "result": "<actual output>"
}
```

For boolean paradigms, the `result` field should be `true` or `false`.

