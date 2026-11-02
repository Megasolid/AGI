# H0 — Correction Report (revision 5)

**Date:** 2026-11-02T20:35+0330
**Trigger:** King review 2026-11-02T19:53 — Revision 4 "NOT ACCEPTED FOR FREEZE", five required corrections.
**Status:** all five addressed; new suite added.
**Additive only.** Revisions 1–4 reports and evidence remain unchanged on record.

---

## 1. The findings

| # | Finding | Severity | Real defect |
|---|---|---|---|
| G1 | Durable audit is optional: `self.audit = audit or AuditLog()` | **Critical blocker** | Default construction let execution proceed after an in-memory append, contradicting the kernel's central guarantee. The boundary was safe only under the test configuration. |
| G2 | `_accounted` is shared mutable `Kernel` state | Blocker | Concurrent calls set/clear it for each other; one request could skip its denial, another append a duplicate. |
| G3 | `_recover()` indexed without lifecycle validation | Blocker | A digest-consistent but semantically invalid log loaded silently. |
| G4 | `_disk_tail()` compared only the final digest | Blocker | An altered earlier record with an unchanged tail went undetected until full recovery. |
| G5 | `enforce_single_writer=False` constructible | Blocker | The lock bypass was selectable from the enforcement path. |

---

## 2. Corrections

### G1 — durable audit is mandatory

`Kernel.__init__` now raises:

- `E_AUDIT_REQUIRED` when no store is supplied;
- `E_AUDIT_NOT_DURABLE` when the store does not declare `is_durable = True`.

`AuditLog` (in-memory) declares `is_durable = False` and is therefore **rejected**. It survives only so
isolated tests can assert call ordering, and it can no longer run an execution.

### G2 — request-local accounting

The shared `_accounted` flag is gone. An executor failure whose outcome is already recorded raises a
private `_AccountedDenial` exception carrying the code; the handler returns without appending a second
record. Nothing about one request's accounting lives on the kernel object, so concurrent requests
cannot interfere.

Proven by a barrier-synchronised test: two concurrent requests (one executor failure, one success)
produce two distinct intents/two outcomes, zero dangling intents, and the unrelated denial is still
recorded afterwards.

### G3 — recovery validates lifecycle invariants

`_recover()` now calls `_validate()` for every record it loads. A digest-consistent log containing an
orphan outcome, a duplicate intent, or an unknown phase is **refused at load** with `E_AUDIT_ORPHAN` /
`E_AUDIT_DUPLICATE` / `E_AUDIT_INVALID`. Proven with hand-built logs that are internally consistent but
semantically invalid.

### G4 — full chain verified before append

`_disk_chain()` re-reads and fully re-verifies every on-disk record (digest + linkage) and returns the
record count. An append is refused with `E_AUDIT_FOREIGN_WRITE` if the head digest **or the length**
differs from the writer's view. Proven by altering an earlier record while leaving the final record
intact, and separately by truncating the file.

### G5 — writer bypass isolated

The public `enforce_single_writer` keyword is removed. The only bypass is the private
`_allow_unsafe_observer` flag, which is documented as observer-only and is asserted by test not to be
a public enforcement option.

---

## 3. Test evidence

| Suite | Result |
|---|---|
| `test_h0_contract_v5.py` (new: G1–G5) | **14/14 OK** |
| `test_h0_contract_v4.py` | **14/14 OK** |
| `test_h0_contract_v3.py` | **18/18 OK** |
| `test_h0_contract_v2.py` | **28/28 OK** |
| `test_h0_contract.py` | **32/32 OK** |
| `test_v41e_*.py` (regression) | **145/145 OK** |

The revision-1 suite grew from 31 to 32 tests because it gained `test_in_memory_sink_is_rejected`,
which asserts the new G1 boundary.

---

## 4. Migration work this correction forced

Enforcing G1 broke every earlier suite that had been silently relying on the in-memory default. Each
was migrated to a durable temp-file store, and three assertions were rewritten because they had been
testing behaviour that G1 now forbids:

1. an `AuditLog`-based "audit failure" test — the sink can no longer be constructed at all;
2. a `Recorder` subclass of `AuditLog` used for ordering — now wraps a durable store and declares durability;
3. an assertion that every audit record carries `request_digest` — outcome records never did; the
   assertion was loose and is now precise.

That migrations were needed at all is the real signal: **revision 4's suites were green while running
against a sink the kernel should never have accepted.**

---

## 5. Residual risks (unchanged, and still blockers for deployment)

1. Rate-limiter counters are in-process.
2. `ReplayStore` is in-memory — replay durability across restart is still an open risk of the same
   class as the audit gap.
3. The verifier is injected; real ML-DSA message authentication is not wired in.
4. Payload schemas are Python-declared, not published JSON Schema.
5. No fuzzing or property-based testing.
6. The chain proves internal consistency, not non-substitution; the head digest is not externally anchored.
7. The single-writer lock is advisory and OS-scoped.

These are not made safe by a reference-kernel freeze and are not claimed to be.

## 6. Boundaries

No MCP server, tunnel, credential or exposure. H0 final freeze requires King's separate review and explicit authorization.
