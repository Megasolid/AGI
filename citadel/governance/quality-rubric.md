# Quality Rubric for Mana (draft)

**Purpose:** independently assess quality so token savings cannot reward unsafe or degraded work.
**Scale:** 0–100 per task; baseline quality frozen for the matched workload.

| Dimension | Weight | 0–20 anchors |
|---|---|---|
| Correctness/evidence | 30 | 0 unsupported/false; 10 partial; 20 verified evidence pointers |
| Completeness | 20 | 0 missing core; 10 partial; 20 complete against acceptance |
| Reliability/format | 20 | 0 unusable; 10 malformed; 20 stable/contract-compliant |
| Safety/security | 20 | 0 violation; 10 unresolved risk; 20 controls respected |
| Usefulness | 10 | 0 not actionable; 5 partial; 10 actionable with limits |

## Eligibility
- Safety failure or fabricated evidence → **quality = 0, Q = 0**, regardless of savings.
- Quality below **95% of baseline quality** → Q = 0.
- Otherwise `Q = min(1, quality / baseline_quality)`.
- Mana = `max(0, baseline_tokens − actual_tokens) × Q`; round down.

## Independent assessment
- Assessor cannot be the producer or same-context model.
- Evidence: rubric scores, task acceptance, evidence hashes, safety review, reviewer identity.
- Kilo independently verifies; KING supervises; no self-certified quality.

## Anti-gaming
- No changing baseline after measurement.
- No rewarding output truncation, skipped verification or hidden failures.
- No mana for unverified savings; ledger status pending until audit.
- Token savings never override correctness or safety.


## Baseline and independence
Baselines are task-matched, reproducible, versioned and frozen before measurement. The assessor must be independent of the optimizing Citizen. Record measurement uncertainty; no retroactive baseline changes. Mana is an efficiency metric, not authority/currency.
