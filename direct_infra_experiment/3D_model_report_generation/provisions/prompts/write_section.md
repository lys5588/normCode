# Write Report Section

## Task
Research and write a complete section for the academic report on **3D Urban Scene Generation**.

## Input

<current_section>
$input_1
</current_section>

The section object contains:
- `name`: Section title
- `subsections`: List of subsection titles to cover
- `scope`: What the section should cover
- `depth`: Level of technical detail expected

## Instructions
1. Write comprehensive content covering all specified subsections
2. Include relevant citations (use placeholder format: [Author et al., Year])
3. Suggest figures/tables where appropriate (describe what they should show)
4. Maintain consistent academic tone and formatting
5. Focus on recent advances (2020-2026) where applicable
6. Balance between breadth (survey-style coverage) and depth (technical details)
7. Use proper academic writing conventions

## Writing Guidelines
- Start with an introduction to the section topic
- Cover each subsection systematically
- Include technical details appropriate to the depth level
- Reference key papers and methods
- End with a brief summary or transition to next section

## Output Format
Return JSON with `thinking` and `result` fields:

```json
{
  "thinking": "Your research and writing process...",
  "result": {
    "section_name": "1. Introduction",
    "content": "# 1. Introduction\n\n## 1.1 Motivation\n\nContent here...\n\n## 1.2 Scope\n\nContent here...",
    "citations": [
      {"id": "author2023", "text": "Author et al., 2023 - Paper title"},
      {"id": "researcher2024", "text": "Researcher et al., 2024 - Another paper"}
    ],
    "figures": [
      {"id": "fig1", "description": "Overview diagram of 3D urban scene generation pipeline"},
      {"id": "fig2", "description": "Comparison of different representation methods"}
    ]
  }
}
```

**Important:** Your response MUST be valid JSON with exactly these two top-level keys.
