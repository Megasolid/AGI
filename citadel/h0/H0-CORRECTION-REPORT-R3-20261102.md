# H0 — Correction Report (revision 3)

**Date:** 2026-11-02T20:05+0330
**Trigger:** King review 2026-11-02T19:43 — three findings remaining after revision 2.
**Status:** all three corrected; new adversarial suite added.
**Additive only.** Revision 1 (`92db7ee1…`) and revision 2 (`3fef6bfb…`) evidence and their reports remain unchanged on record.

---

## 1. The three findings

| # | Finding | Verdict | What was actually wrong |
|---|---|---|---|
| F6 | Audit durability unproven — the store is an in-memory list | **Correct** | The F1 correction made audit a *precondition*, but a precondition on a list that vanishes on restart proves ordering, not durability. |
| F7 | Audit outcome lifecycle incomplete — `outcome: "pending"` written and never completed; a failure can append a denial after an allow | **Correct** | My own contract required one record per request; the implementation could produce two contradictory ones. |
| F8 | Rate limiting not concurrency-safe — `check()` and `record()` take the lock separately | **Correct** | I added a lock and then failed to hold it across the operation that matters. Concurrent requests could all pass `check()` before any `record()` landed. |

All three are the same failure class as F1: **a control that appears enforced until its failure mode is tested.**

---

## 2. Corrections

### F6 — durable audit store (`runtime/h0_audit_store.py`)

- Append-only JSONL on disk, **fsync'd before the append is acknowledged**.
- **Hash-chained**: every record carries `prev_digest` and its own `digest`.
- **Tamper evidence**: on reload, a modified record fails digest verification; a re-ordered or substituted record fails chain verification; both raise `E_AUDIT_TAMPERED` / `E_AUDIT_CORRUPT`.
- **Restart recovery**: reload re-verifies the whole chain and publishes a watermark (`records`, `head_digest`).
- **Fail-closed**: if the path cannot be created, opened, written or fsync'd, `append()` raises `AuditStoreError("E_AUDIT_UNAVAILABLE")` and the kernel denies without executing.

### F7 — two-phase audit lifecycle

```
phase: "intent"   written BEFORE the effect      outcome: "pending"
phase: "outcome"  written AFTER  the effect      outcome: "executed" | "failed"
```

- Invariants enforced by the store: exactly one intent per `correlation_id`; at most one outcome; **an outcome without an intent is rejected as `E_AUDIT_ORPHAN`**.
- `dangling_intents()` exposes authorised-but-unrecorded executions so a restarted station can see that execution is in doubt.
- Executor failure now writes `outcome: "failed"` with `E_EXECUTOR_FAILED` and never leaves a dangling intent.
- If the outcome record itself cannot be written, the kernel returns `E_AUDIT_UNAVAILABLE` rather than claiming success — the effect happened but the trail has a gap, and the caller is told.

### F8 — atomic rate admission

`RateLimiter.admit()` holds the lock across **test-all-limits-and-record**. The separate `check()` / `record()` seam is removed and now raises if called, so the unsafe pattern cannot be reintroduced by accident.

Concurrency proof: 200 threads racing at one instant yield **exactly 20** admissions (the burst cap), not more.

---

## 3. Test evidence

| Suite | Result |
|---|---|
| `test_h0_contract_v3.py` (new: F6/F7/F8) | **18/18 OK** |
| `test_h0_contract_v2.py` (F1–F5, re-run) | **28/28 OK** |
| `test_h0_contract.py` (revision 1, re-run) | **31/31 OK** |
| `test_v41e_*.py` (regression) | **145/145 OK** |

Fixtures in revisions 1–2 were updated where revision 3 legitimately changed observable behaviour (executor failures now report `E_EXECUTOR_FAILED`; a successful request now writes two audit records, intent then outcome). The kernel was never bent to satisfy a test.

---

## 4. Defects found while correcting (all fixed forward, none hidden)

1. `mkdir` was outside the fail-closed `try`, so an unusable path raised a bare `FileExistsError` instead of `E_AUDIT_UNAVAILABLE`.
2. The kernel caught only `H0Error` around the audit append; `AuditStoreError` (a `ValueError`) escaped as an unhandled exception.
3. The **denial path** caught only `H0Error`, so a store that raised on the denial record turned a clean denial into an unhandled exception.
4. A test asserted construction-time failure for an unusable path; construction is lazy by design, so the test was replaced with the append-time proof that actually matters.

---

## 5. Residual risks still open

1. Rate-limiter counters remain in-process; multi-instance deployment needs shared counters.
2. `ReplayStore` is still in-memory; durable replay protection across restarts is not implemented (audit durability was the finding; replay durability is an equivalent open risk).
3. The verifier is injected; real ML-DSA message authentication is not wired into the kernel.
4. Payload schemas are Python-declared, not published JSON Schema artifacts.
5. No fuzzing or property-based testing.
6. The audit chain proves internal consistency; it does not prove the store was never replaced wholesale with a forged chain re-signed by the same writer. That requires anchoring the head digest to an external trusted record.

## 6. Boundaries

No MCP server, tunnel, credential or exposure exists or is created by this revision.
H0 final freeze requires King's separate review and explicit authorization.
