# Create Structured Outline for 3D Urban Scene Generation Report

## Task
Create a detailed, structured outline with main sections and subsections for an academic report on **3D Urban Scene Generation**.

## Input

<topic_areas>
$input_1
</topic_areas>

## Instructions
1. Organize the identified topic areas into a coherent structure
2. Create subsections for each main section
3. Define the scope (what to cover) and depth (how detailed) for each section
4. Ensure logical flow from fundamentals to advanced topics to applications
5. Consider dependencies between sections (e.g., foundations before advanced methods)

## Output Format
Return JSON with `thinking` and `result` fields:

```json
{
  "thinking": "Your reasoning about how to structure the outline...",
  "result": {
    "title": "3D Urban Scene Generation: A Comprehensive Survey",
    "sections": [
      {
        "name": "1. Introduction",
        "subsections": ["1.1 Motivation", "1.2 Scope", "1.3 Contributions"],
        "scope": "Overview of the field and report structure",
        "depth": "high-level overview"
      }
    ]
  }
}
```

**Important:** Your response MUST be valid JSON with exactly these two top-level keys.
