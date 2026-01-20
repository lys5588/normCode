# Decompose Specifications into Intent Blocks

Break down the ISA and microarchitecture specifications into atomic intent blocks.

## Input

You will receive:
1. **ISA Spec Text**: The Instruction Set Architecture specification
2. **MA Spec Text**: The Microarchitecture specification

## Task

Decompose these specifications into discrete "intent blocks" - atomic units of normative behavior.

Each intent block should:
- Capture a single behavioral requirement
- Be self-contained (can be understood without full context)
- Use normative language ("shall", "must", "required")
- Identify trigger conditions and expected outcomes

## Output Format

Return JSON:
```json
{
  "intent_blocks": [
    {
      "id": "IB001",
      "text": "Each issued instruction shall resolve to commit or trap",
      "type": "liveness",
      "source": "ISA Section 1"
    },
    {
      "id": "IB002", 
      "text": "Pipeline flush may cancel younger in-flight instructions",
      "type": "exception",
      "source": "ISA Section 1"
    },
    ...
  ]
}
```

## Intent Block Types

- **liveness**: Something must eventually happen
- **safety**: Something must never happen
- **ordering**: Relative order requirements
- **atomicity**: Indivisibility requirements
- **exception**: Valid deviations from normal behavior

