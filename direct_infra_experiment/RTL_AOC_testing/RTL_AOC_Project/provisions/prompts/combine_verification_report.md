# Combine Verification Report

Synthesize all verification components into a comprehensive final report.

## Input Data

<all_testing_information>
$input_1
</all_testing_information>

## Input Structure Analysis

The input is a bundled dictionary containing all testing artifacts:

### 1. AOC Definitions (`{AOC definitions}`)
The Action-Obligation Canonical rules extracted from ISA/microarchitecture specifications:
- `rules`: Array of AOC rule objects, each with:
  - `id`: Unique canonical identifier (e.g., "C001_InstrResolution")
  - `trigger`: Signal/condition that activates the obligation
  - `obligation`: What must happen (any_of, all_of, if_then conditions)
  - `timing`: Temporal constraints (max_cycles, deadlines)
  - `abort`: Valid cancellation conditions

### 2. AOC Validity (`{AOC validity}`)
Boolean indicating whether the extracted AOC rules passed validation:
- `true`: Rules are well-formed, testable, and complete
- `false`: Rules have issues (missing fields, untestable conditions, contradictions)

### 3. Verification Results (`[verification results]`)
Per-cycle verification outcomes from Phase 2:
- Each entry contains:
  - `cycle_num`: The clock cycle number
  - `status`: "PASS", "FAIL", or "SKIP"
  - `violations`: Array of rule violations detected
  - `active_rules`: Rules being tracked at this cycle
  - `triggered_rules`: Rules that became active this cycle
  - `satisfied_rules`: Rules that were satisfied this cycle

### 4. Trace Data (`[trace data]`)
Per-cycle RTL simulation trace information:
- Each entry contains:
  - `cycle_num`: Clock cycle number
  - `events`: Array of architectural events observed
  - `signals`: Relevant signal states

### 5. User Inputs (`{all user inputs}`)
Original specification sources:
- `isa`: ISA specification text
- `ma`: Microarchitecture specification text  
- `intent_blocks`: User-clarified requirements

## Synthesis Task

Generate a comprehensive verification report by:

1. **Analyzing AOC Status**
   - Count total rules, categorize by type (liveness, safety, ordering)
   - Note any validation issues if AOC was invalid
   - Summarize rule coverage

2. **Processing Verification Results**
   - Aggregate pass/fail counts across all cycles
   - Identify any violations with full context
   - Track rule lifecycle (triggered → active → satisfied/violated)
   - Calculate metrics (peak active rules, average resolution time)

3. **Correlating with Trace Data**
   - Map violations to specific trace events
   - Identify event patterns leading to failures
   - Note any suspicious but non-violating patterns

4. **Synthesizing Conclusions**
   - Overall conformance assessment
   - Root cause analysis for any failures
   - Coverage gaps or untested scenarios
   - Recommendations for spec clarification or RTL fixes

## Output Format

Return JSON with `thinking` and `result` fields:

```json
{
  "thinking": "Detailed analysis process: examining AOC rules, correlating verification results with trace events, identifying patterns...",
  "result": {
    "report_metadata": {
      "generated_at": "2026-01-23T21:30:00Z",
      "verification_version": "1.0",
      "spec_sources": ["ISA v1", "Microarch v2"]
    },
    "executive_summary": {
      "overall_status": "PASS|FAIL|INCOMPLETE",
      "confidence": "HIGH|MEDIUM|LOW",
      "total_cycles_verified": 500,
      "total_violations": 0,
      "critical_findings": []
    },
    "aoc_analysis": {
      "validity": true,
      "total_rules": 5,
      "rules_by_category": {
        "liveness": 2,
        "safety": 2,
        "ordering": 1
      },
      "rule_summary": [
        {
          "id": "C001_InstrResolution",
          "category": "liveness",
          "description": "Instructions must resolve within deadline",
          "testability": "HIGH"
        }
      ],
      "validation_notes": []
    },
    "trace_analysis": {
      "total_cycles": 500,
      "total_events": 1250,
      "event_distribution": {
        "instr_issued": 400,
        "commit": 380,
        "trap_taken": 15,
        "flush_event": 5
      },
      "trace_characteristics": {
        "avg_events_per_cycle": 2.5,
        "peak_activity_cycle": 234,
        "idle_cycles": 12
      }
    },
    "verification_analysis": {
      "cycles_passed": 500,
      "cycles_failed": 0,
      "cycles_skipped": 0,
      "rule_statistics": {
        "total_triggers": 400,
        "total_satisfactions": 395,
        "total_aborts": 5,
        "total_violations": 0,
        "peak_concurrent_active": 8,
        "avg_resolution_cycles": 3.2
      },
      "per_rule_metrics": [
        {
          "rule_id": "C001_InstrResolution",
          "times_triggered": 400,
          "times_satisfied": 395,
          "times_aborted": 5,
          "times_violated": 0,
          "avg_resolution_cycles": 3.2,
          "max_resolution_cycles": 12
        }
      ],
      "violations": []
    },
    "conclusions": {
      "conformance_assessment": "RTL implementation fully conforms to specified AOC rules",
      "coverage_assessment": {
        "rules_exercised": 5,
        "rules_with_triggers": 5,
        "edge_cases_tested": ["flush during active obligation", "concurrent triggers"],
        "untested_scenarios": []
      },
      "risk_areas": [],
      "recommendations": []
    }
  }
}
```

## Handling Violations

When violations are detected, include detailed context:

```json
{
  "violations": [
    {
      "violation_id": "V001",
      "cycle": 10100,
      "rule_id": "C001_InstrResolution",
      "violation_type": "TIMEOUT",
      "severity": "CRITICAL",
      "description": "Instruction did not resolve within deadline",
      "trigger_context": {
        "trigger_cycle": 100,
        "trigger_event": {"type": "instr_issued", "iid": "0x42"}
      },
      "obligation_status": {
        "expected": "commit OR trap_taken",
        "observed": "neither within 10000 cycles"
      },
      "abort_analysis": {
        "valid_aborts_checked": ["flush_event"],
        "abort_occurred": false
      },
      "trace_excerpt": [
        {"cycle": 100, "event": "instr_issued", "iid": "0x42"},
        {"cycle": 10100, "event": "deadline_exceeded"}
      ],
      "root_cause_hypothesis": "Instruction may be stuck in reservation station"
    }
  ]
}
```

## Handling Incomplete Data

If verification couldn't complete (e.g., invalid AOC):

```json
{
  "result": {
    "executive_summary": {
      "overall_status": "INCOMPLETE",
      "confidence": "LOW",
      "critical_findings": ["AOC validation failed - verification skipped"]
    },
    "aoc_analysis": {
      "validity": false,
      "validation_notes": ["Rule C003 has untestable condition: signal 'foo' not in trace vocabulary"]
    },
    "verification_analysis": {
      "cycles_passed": 0,
      "cycles_failed": 0,
      "cycles_skipped": 500,
      "skip_reason": "Invalid AOC rules prevented verification"
    },
    "conclusions": {
      "conformance_assessment": "Cannot assess - verification not performed",
      "recommendations": [
        "Fix AOC rule C003: replace 'foo' with observable signal",
        "Re-run verification after AOC fixes"
      ]
    }
  }
}
```

## Quality Expectations

1. **Completeness**: Report on all input components, note any missing data
2. **Accuracy**: Metrics must match actual counts from inputs
3. **Actionability**: Recommendations should be specific and implementable
4. **Traceability**: All findings should reference specific cycles/rules/events

**CRITICAL:** Your response MUST be valid JSON with exactly two top-level keys: `thinking` and `result`.
