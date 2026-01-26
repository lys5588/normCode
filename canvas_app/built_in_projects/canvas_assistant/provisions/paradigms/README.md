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

### User Input Paradigms
- `v_PromptLocation-h_Literal-c_UserTextEditor-o_JsonLiteral.json` - Show prompt to user via text editor, get JSON response

### Canvas Integration Paradigms
- `c_CanvasIntegrationGetChat-o_Literal.json` - Block and wait for user chat message (no inputs)
- `h_Literal-c_CanvasIntegrationSay-o_LiteralStatus.json` - Send message to user via chat
- `h_Literal-c_CanvasIntegrationExecute-o_LiteralStatus.json` - Execute parsed command on canvas

## Paradigm Usage in Canvas Assistant

| Paradigm | Used For |
|----------|----------|
| `h_LiteralPath-c_ReadFile-o_Literal` | Loading command schema from file |
| `c_CanvasIntegrationGetChat-o_Literal` | Blocking wait for user input |
| `h_Literal-c_CanvasIntegrationSay-o_LiteralStatus` | Emitting status (thinking, executing, generating), sending responses |
| `h_Literal-c_CanvasIntegrationExecute-o_LiteralStatus` | Executing parsed canvas commands |
| `v_PromptLocation-h_Literal-c_GenerateThinkJson-o_Literal` | Summarizing context, classifying commands, generating responses |
| `v_PromptLocation-h_Literal-c_GenerateThinkJson-o_Boolean` | Judging session termination |

## Paradigm Usage in RTL AOC Verification

| Paradigm | Used For |
|----------|----------|
| `h_LiteralPath-c_ReadFile-o_Literal` | Loading ISA spec, MA spec, RTL trace |
| `v_PromptLocation-h_Literal-c_UserTextEditor-o_JsonLiteral` | Asking user to decompose specs into intent blocks |
| `v_PromptLocation-h_Literal-c_GenerateThinkJson-o_Literal` | Extracting AOC, consolidating schemas, updating rules, verifying cycles, generating report |
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

## User Input Paradigm

The user input paradigm (`v_PromptLocation-h_Literal-c_UserTextEditor-o_JsonLiteral`) uses the Canvas app's `user_input_tool` to:

1. Read the prompt template from the specified path
2. Fill the template with horizontal input data (context)
3. Show a text editor to the user with the filled prompt
4. Wait for user to provide JSON response
5. Parse and return the JSON as a literal

This paradigm is used for user-facing imperatives marked with `:>:` in NormCode.

