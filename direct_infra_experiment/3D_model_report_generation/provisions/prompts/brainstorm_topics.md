# Brainstorm Key Areas for 3D Urban Scene Generation Report

## Task
Brainstorm and identify the key areas/topics that should be covered in an academic-style report on **3D Urban Scene Generation**.

## Input

<report_topic>
$input_1
</report_topic>

## Instructions
1. Consider the full scope of 3D urban scene generation research
2. Include foundational concepts, methods, applications, and future directions
3. Balance technical depth with accessibility
4. Focus on recent advances (2020-2026)
5. Cover both traditional and modern deep learning approaches

## Suggested Areas to Consider
- Introduction & Background
- Problem Definition & Challenges
- Data Sources & Representations (point clouds, meshes, voxels, implicit representations)
- Traditional Methods (procedural generation, rule-based systems)
- Deep Learning Approaches (GANs, VAEs, diffusion models, transformers)
- Neural Radiance Fields (NeRF) and Gaussian Splatting for urban scenes
- Text-to-3D and Image-to-3D urban generation
- Datasets & Benchmarks
- Evaluation Metrics
- Applications (autonomous driving, urban planning, gaming, AR/VR)
- Current Limitations & Open Challenges
- Future Directions

## Output Format
Return JSON with `thinking` and `result` fields:

```json
{
  "thinking": "Your reasoning about what areas to include and why...",
  "result": {
    "areas": [
      {
        "name": "Section Name",
        "description": "Brief description of what this section covers"
      }
    ]
  }
}
```

**Important:** Your response MUST be valid JSON with exactly these two top-level keys.
