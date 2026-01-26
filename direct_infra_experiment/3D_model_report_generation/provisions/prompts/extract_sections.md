# Extract Sections List from Outline

## Task
Extract the list of sections from the structured outline, preserving all metadata needed for section writing.

## Input

<outline>
$input_1
</outline>

## Instructions
1. Extract each section from the outline
2. Preserve the section name, subsections, scope, and depth
3. Return as a list that can be iterated over
4. Maintain the order from the outline

## Output Format
Return JSON with `thinking` and `result` fields:

```json
{
  "thinking": "Extracting sections from the outline...",
  "result": [
    {
      "name": "1. Introduction",
      "subsections": ["1.1 Motivation", "1.2 Scope", "1.3 Contributions"],
      "scope": "Overview of the field and report structure",
      "depth": "high-level overview"
    },
    {
      "name": "2. Problem Definition",
      "subsections": ["2.1 Core Challenges", "2.2 Requirements"],
      "scope": "Define the technical challenges",
      "depth": "moderate technical detail"
    }
  ]
}
```

**Important:** Your response MUST be valid JSON with exactly these two top-level keys. The `result` should be a LIST of section objects.
