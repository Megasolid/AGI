# H0 — Correction Report (revision 10)

**Date:** 2026-11-02T21:45+0330
**Trigger:** King review 2026-11-02T21:35 — Revision 9 "NOT ACCEPTED FOR H0 FREEZE": the evidence-consistency test is vacuous.
**Status:** the check is now real, and demonstrably able to fail.
**Additive only.** Revisions 1–9 reports and evidence remain unchanged on record.

---

## 1. The finding

R9 shipped this regex to reconcile report counts with suite sizes:

```python
r"`(test_h0_contract[^`]*)\.py`\| \*\*(\d+)/\d+"
```

The report's table actually reads `` `test_h0_contract.py` | 32 | OK ``. The regex matched **nothing**,
the claim dictionary came back empty, the loop ran **zero** comparisons, and the test **passed**.

So the mechanism I announced as making "an R8-style mismatch mechanically impossible to repeat silently"
was itself silently checking nothing. The R8 error was a wrong number; the R9 repair was a check that
could not fail. King found it by comparing the table format against the actual regex.

This is the fifth instance in this project of a test asserting a property its body does not exercise.
It is also the most embarrassing, because I wrote it *in response to* that exact criticism.

---

## 2. Correction — `runtime/h0_evidence.py`

A standalone checker with four properties:

| Property | Implementation |
|---|---|
| Parses the real table | `ROW = ^\|\s*`(?P<name>...\.py)`\s*\|\s*(?P<count>\d+)\s*\|` |
| **Cannot pass vacuously** | zero extracted claims raises `EvidenceError("vacuous check")` |
| Compares every suite | every listed suite checked; unlisted suites reported as missing |
| Total cross-checked | `Total H0 contract tests: **N**` compared to the measured sum |

**Negative controls are built in.** `self_test()` fabricates four bad reports and requires the checker to
reject each:

1. a report with a wrong count for one suite → must fail on that suite;
2. a report with no recognisable table → must raise instead of passing;
3. a report omitting a suite → must report it missing;
4. a report with a wrong total → must fail the total check.

`python runtime/h0_evidence.py self-test runtime` reports all five controls (`accepts_correct_report`
plus the four rejections). The v10 suite runs it and asserts every control is `True`.

Applying the checker to the **R9 report** produced `ok: True` with all nine suites matched and the total
verified — so R9's numbers were correct; only its checking mechanism was empty.

---

## 3. Test evidence

| Suite | Tests | Result |
|---|---|---|
| `test_h0_contract.py` | 32 | OK |
| `test_h0_contract_v2.py` | 28 | OK |
| `test_h0_contract_v3.py` | 18 | OK |
| `test_h0_contract_v4.py` | 14 | OK |
| `test_h0_contract_v5.py` | 14 | OK |
| `test_h0_contract_v6.py` | 14 | OK |
| `test_h0_contract_v7.py` | 9 | OK |
| `test_h0_contract_v8.py` | 10 | OK |
| `test_h0_contract_v9.py` | 7 | OK |
| `test_h0_contract_v10.py` | 10 | OK |
| `test_v41e_*.py` (regression) | 145 | OK |

Total H0 contract tests: **156**.

These counts are verified by `h0_evidence.py check` against this document; if any number above drifts
from the suites, the check fails.

---

## 4. What R10 does and does not establish

**Established:** the report/evidence consistency mechanism is real, non-vacuous, covers every suite,
cross-checks the total, and has been observed failing against four fabricated bad reports.

**Not established:** anything about H0 enforcement readiness. R10 corrects an evidence tool. It does not
close any of the enforcement residuals below, and it is not a freeze argument.

---

## 5. Residual risks (unchanged; none resolved by a freeze)

1. Rate-limiter counters are in-process.
2. `ReplayStore` is in-memory — replay durability across restart remains open.
3. The verifier is injected; real ML-DSA message authentication is not wired in.
4. Payload schemas are Python-declared, not published JSON Schema.
5. No fuzzing or property-based testing.
6. The chain proves internal consistency, not non-substitution; the head digest is not externally anchored.
7. The single-writer lock is advisory and OS-scoped.
8. A second process importing `h0_audit_store` can append to the same file; foreign-write detection
   happens only at the next kernel append.
9. Same-process tampering is not prevented; a test demonstrates the limit explicitly.

## 6. Boundaries

No MCP server, tunnel, credential or exposure. H0 final freeze requires King's separate review and explicit authorization.
