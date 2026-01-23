# Combine Verification Report

Combine all components into the final verification report.

## Input Data

<all_testing_information>
$input_1
</all_testing_information>

**Input Structure:**
The input is a dictionary containing:
- `{AOC definitions}`: The AOC rules extracted from specifications
- `{AOC validity}`: Boolean indicating if AOC rules are valid
- `[verification results]`: List of per-cycle verification results
- `[trace data]`: List of per-cycle trace data
- `{all user inputs}`: Original specification inputs (ISA, MA, intent blocks)

## Task

Synthesize a comprehensive verification report containing:

1. **Executive Summary**: Pass/fail with key metrics
2. **AOC Status**: Validity and rule summary
3. **Trace Summary**: Total cycles, events processed
4. **Verification Results**: Per-cycle status, any violations
5. **Conclusions**: Overall assessment

## Output Format

Return JSON with `thinking` and `result` fields:
```json
{
  "thinking": "Your synthesis analysis - summarizing verification outcomes...",
  "result": {
    "executive_summary": {
      "overall_status": "PASS",
      "total_cycles": 500,
      "violations_found": 0,
      "rules_evaluated": 5
    },
    "aoc_status": {
      "valid": true,
      "total_rules": 5,
      "rule_ids": ["C001", "C002", "C003", "C004", "C005"]
    },
    "trace_summary": {
      "total_events": 15,
      "event_types": ["instr_issued", "commit", "trap_taken", "LR_executed", "SC_executed", "SC_result"]
    },
    "verification_results": {
      "cycles_checked": 500,
      "cycles_passed": 500,
      "cycles_failed": 0,
      "active_rules_peak": 3,
      "violations": []
    },
    "conclusions": {
      "assessment": "RTL implementation conforms to all specified AOC rules",
      "recommendations": []
    }
  }
}
```

**Important:** Your response MUST be valid JSON with exactly these two top-level keys: `thinking` and `result`.

## For Failed Verification

Include violation details in the `result.verification_results.violations` array:
```json
{
  "violations": [
    {
      "cycle": 10100,
      "rule_id": "C001_InstrResolution",
      "type": "TIMEOUT",
      "description": "Instruction 0x42 did not resolve within deadline",
      "context": {"iid": "0x42", "start_cycle": 100, "deadline": 10100}
    }
  ]
}
```

## Handling Missing Data

If some components are not available (e.g., verification didn't run due to invalid AOC):
- Report what's available
- Note missing components in `conclusions.recommendations`
- Set appropriate status based on available data
