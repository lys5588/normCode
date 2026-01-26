# Integrate Report Sections into Final Document

## Task
Combine all written sections into a cohesive academic report with abstract, conclusion, and references. Output the final report as a complete markdown article.

## Inputs

<report_topic>
$input_1
</report_topic>

<outline>
$input_2
</outline>

<all_section_drafts>
$input_3
</all_section_drafts>

## Instructions
1. Write a comprehensive abstract (200-300 words) summarizing the report
2. Ensure smooth transitions between sections
3. Write a conclusion section that:
   - Summarizes key findings
   - Discusses implications
   - Suggests future research directions
4. Compile all citations into a unified references section
5. Review for consistency in:
   - Terminology usage
   - Writing style and tone
   - Citation format
   - Figure/table numbering
6. Add any necessary connecting text between sections
7. Ensure the report flows logically from introduction to conclusion

## Output Format
Return JSON with `thinking` and `result` fields. The `result` should be the **complete article as a markdown string**:

```json
{
  "thinking": "Your integration and review process...",
  "result": "# 3D Urban Scene Generation: A Comprehensive Survey\n\n## Abstract\n\nThis survey provides a comprehensive overview of...\n\n## 1. Introduction\n\n### 1.1 Motivation\n\nContent here...\n\n## 2. Problem Definition\n\n...\n\n## Conclusion\n\nThis survey has presented...\n\n## References\n\n[1] Author et al., 2023. Paper title. Conference/Journal.\n[2] Researcher et al., 2024. Another paper. Venue."
}
```

**Important:** 
- Your response MUST be valid JSON with exactly these two top-level keys.
- The `result` field should be a **single markdown string** containing the entire formatted article.
- Use `\n` for newlines within the JSON string.
- Include all sections: Title, Abstract, all body sections, Conclusion, and References.
