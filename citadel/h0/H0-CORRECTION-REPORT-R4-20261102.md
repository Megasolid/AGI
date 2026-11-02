# H0 — Correction Report (revision 4)

**Date:** 2026-11-02T20:30+0330
**Trigger:** King review 2026-11-02T19:46 — Revision 3 "NOT ACCEPTED FOR FREEZE", four required corrections.
**Status:** all four addressed; new suite added.
**Additive only.** Revisions 1–3 reports and evidence remain unchanged on record.

---

## 1. The findings and what was actually wrong

| # | Finding | Verdict | Real defect |
|---|---|---|---|
| F9 | Validation happened during indexing, after bytes were written | **Correct** | A rejected append could already have written; sequence and chain head left inconsistent. |
| F10 | Writer concurrency undefined | **Correct** | No single-writer contract, no cross-process lock; two writers would fork the chain silently. |
| F11 | Post-effect failure handling | **Correct — most serious** | Outcome-write failure fell into the generic denial path and appended `phase: "deny"`, which **implies the effect did not happen — but it already had**. |
| F12 | One test was meaningless | **Correct** | "Minute cap between clients" asserted only `1 <= admitted <= 200`; the workload never reached the cap. Zero evidence for its name. |

The F11 defect is the failure mode the entire contract exists to prevent, and I introduced it while fixing F7.

---

## 2. Corrections

### F9 — validate before persist

`_validate()` now runs **before** any file handle is opened. Invariants checked pre-append:
intent requires `correlation_id` and must be unique; outcome requires an existing intent and
may occur once; `indeterminate` requires an intent; unknown phases rejected.

Proven by asserting the file bytes, `head_digest` and `seq` are **byte-identical before and after**
a refused append (`test_orphan_outcome_leaves_file_unchanged`, and the duplicate variants).

### F10 — writer concurrency

- **Single-writer contract** enforced with an OS-level advisory lock (`msvcrt.locking` on Windows,
  `fcntl.flock` elsewhere) on `<store>.lock`. A second live writer is refused with `E_AUDIT_SECOND_WRITER`.
- **Foreign-write detection**: before every append the store re-reads the on-disk tail and compares it
  with its own head. A mismatch raises `E_AUDIT_FOREIGN_WRITE`.
- Proven: second-writer refusal; a foreign append behind the store's back is detected on the next
  append; and after that refusal the chain still verifies with the expected record count (`test_chain_intact_after_foreign_write_refusal`).

### F11 — indeterminate execution semantics

The governing rule is now explicit in code: **once the effect has happened, no record may suggest otherwise.**

- **Outcome-write failure after a successful effect** → returns `E_EXECUTION_INDETERMINATE`,
  `indeterminate: true`, **preserves the dangling intent**, and appends **no** denial record.
  Verified on disk: the file contains exactly `["intent"]` and the executor was invoked exactly once.
- **Executor failure with a recordable outcome** → writes `outcome: "failed"` and returns
  `E_EXECUTOR_FAILED`; the request is fully accounted for, so **no duplicate deny record** is appended
  (this was a further defect I found while fixing F11).
- **Executor failure AND outcome unrecordable** → `E_EXECUTION_INDETERMINATE`, no denial record.
- **Restart after indeterminate** → a fresh store reports the dangling intent, so the doubt is visible
  after restart rather than lost (`test_restart_after_indeterminate_shows_dangling_intent`).

### F12 — meaningful minute-cap test

Replaced with a test whose workload can actually reach the limit: 0.4 s spacing (2.5 req/s) keeps the
burst window clear so the **minute cap is the only binding limit**, and the test asserts
`E_RATE_BURST` never fires, `E_RATE_LIMIT` does fire, and every attempt is accounted for.
A separate concurrency test drives 1200 attempts in one clock instant and asserts exactly
`burst_count` admissions.

---

## 3. Test evidence

| Suite | Result |
|---|---|
| `test_h0_contract_v4.py` (new: F9/F10/F11/F12) | **14/14 OK** |
| `test_h0_contract_v3.py` | **18/18 OK** |
| `test_h0_contract_v2.py` | **28/28 OK** |
| `test_h0_contract.py` | **31/31 OK** |
| `test_v41e_*.py` (regression) | **145/145 OK** |

---

## 4. Defects found while correcting (all disclosed)

1. The lock's `mkdir` raised `FileExistsError` outside the fail-closed path.
2. The `_accounted` early return referenced `denial` before it was constructed.
3. Executor-failure denials were double-recorded (outcome + deny) — the same class as F11.
4. My first replacement minute-cap test used 0.5 s spacing, which can never reach 120/min; the
   test would have passed while proving nothing. It was caught by asserting the refusal code
   rather than a loose bound.

---

## 5. Residual risks still open

1. Rate-limiter counters remain in-process.
2. `ReplayStore` is still in-memory — replay durability across restart is an open risk of the same
   class as the audit gap King found.
3. The verifier is injected; real ML-DSA message authentication is not wired.
4. Payload schemas are Python-declared, not published JSON Schema.
5. No fuzzing or property-based testing.
6. The chain proves internal consistency, not non-substitution: a wholesale rewrite by the same
   writer is undetectable without anchoring the head digest to an external trusted record.
7. The single-writer lock is advisory and process-scoped; it does not protect against a
   non-cooperating process that ignores the lock (that case is covered only by the foreign-write check).

## 6. Boundaries

No MCP server, tunnel, credential or exposure. H0 final freeze requires King's separate review and explicit authorization.
