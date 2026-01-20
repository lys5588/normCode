# Combine Verification Report

Combine all components into the final verification report.

## Input

You will receive:
1. **AOC Definitions**: The generated AOC rules
2. **AOC Is Valid**: Boolean indicating if AOC passed validation
3. **Trace Per Cycle**: The split RTL trace data
4. **Verification Per Cycle**: Per-cycle verification results

## Task

Synthesize a comprehensive verification report containing:

1. **Executive Summary**: Pass/fail with key metrics
2. **AOC Status**: Validity and rule summary
3. **Trace Summary**: Total cycles, events processed
4. **Verification Results**: Per-cycle status, any violations
5. **Conclusions**: Overall assessment

## Output Format

Return JSON:
```json
{
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
```

## For Failed Verification

Include violation details:
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

