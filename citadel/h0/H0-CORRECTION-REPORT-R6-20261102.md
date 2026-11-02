# H0 — Correction Report (revision 6)

**Date:** 2026-11-02T20:50+0330
**Trigger:** King review 2026-11-02T20:07 — Revision 5 "NOT ACCEPTED FOR FREEZE". G1 and G5 incomplete.
**Status:** both blockers closed; new suite added.
**Additive only.** Revisions 1–5 reports and evidence remain unchanged on record.

---

## 1. The two blockers

| # | Finding | Real defect |
|---|---|---|
| R6-1 | An observer-mode store still enters the enforcement path | `_allow_unsafe_observer=True` set `enforce_single_writer=False` but the class still declared `is_durable = True`. The kernel only checked that declaration, so a store documented as unsuitable for enforcement passed the gate. |
| R6-2 | Durability was self-declared, not enforced | `fsync=False` also declared `is_durable = True` and was accepted despite skipping `os.fsync()`. Any injected object could declare `is_durable = True` and be trusted. |

Both are the G1 failure one level down: **I replaced a permissive default with a permissive declaration.** A
security boundary made of a boolean the guarded object sets about itself is not a boundary.

---

## 2. Corrections

### R6-1 — observer mode categorically refused

`DurableAuditStore.durability()` now reports `observer_mode` and derives `enforceable` from actual
configuration: an observer-mode instance reports `enforceable: False`, `single_writer: False`,
`fsync: False`. `_require_enforceable_store()` rejects any store whose `observer_mode` is not exactly
`False`.

Proven by constructing the exact path — `DurableAuditStore(..., _allow_unsafe_observer=True)` — and
asserting the kernel refuses it with `E_AUDIT_NOT_DURABLE`.

### R6-2 — synchronous persistence required

`fsync` is now derived: `self.fsync = bool(fsync) and not _allow_unsafe_observer`. The contract
requires `fsync is True`; a store built with `fsync=False` is refused for enforcement.

Proven directly: `DurableAuditStore(p, fsync=False)` → `E_AUDIT_NOT_DURABLE` with `fsync` named in the
detail.

### R6-3 — verifiable contract replaces the bare declaration

The kernel no longer reads `is_durable`. It requires a **callable `durability()`** returning a mapping
that must report `enforceable`, `fsync`, `single_writer`, `append_only`, `chained` all `True` and
`observer_mode` exactly `False`. Rejected cases with their codes:

| Injection | Result |
|---|---|
| object with `is_durable = True` and no contract | `E_AUDIT_NOT_DURABLE` — "no durability() contract" |
| object whose contract reports `fsync: False` | `E_AUDIT_NOT_DURABLE` — names `fsync` |
| contract returns a non-mapping | `E_AUDIT_NOT_DURABLE` |
| contract raises | `E_AUDIT_NOT_DURABLE` |
| contract omits required properties | `E_AUDIT_NOT_DURABLE` |

---

## 3. Test evidence

| Suite | Result |
|---|---|
| `test_h0_contract_v6.py` (new: R6-1/2/3 + R5 preservation) | **14/14 OK** |
| `test_h0_contract_v5.py` | **14/14 OK** |
| `test_h0_contract_v4.py` | **14/14 OK** |
| `test_h0_contract_v3.py` | **18/18 OK** |
| `test_h0_contract_v2.py` | **28/28 OK** |
| `test_h0_contract.py` | **32/32 OK** |
| `test_v41e_*.py` (regression) | **145/145 OK** |

R6 also re-tests G2 (request-local accounting), G3 (recovery validation) and G4 (full-chain check) to
prove R6 did not regress them.

---

## 4. Migration

One staging object changed: the revision-2 `Recorder` used for ordering assertions declared
`is_durable = True`. It now **delegates `durability()` to a real durable store** rather than asserting
durability itself. That is the intended shape — a wrapper demonstrates the durability of what it wraps,
it does not vouch for itself.

This is the third time a test staging object has had to be corrected because it was imitating the very
guarantee under audit. That pattern is worth naming: **test doubles that assert the security property
instead of delegating it will pass while the property is absent.**

---

## 5. Residual risks (unchanged; deployment blockers, not resolved by any freeze)

1. Rate-limiter counters are in-process.
2. `ReplayStore` is in-memory — replay durability across restart remains open.
3. The verifier is injected; real ML-DSA message authentication is not wired in.
4. Payload schemas are Python-declared, not published JSON Schema.
5. No fuzzing or property-based testing.
6. The chain proves internal consistency, not non-substitution; the head digest is not externally anchored.
7. The single-writer lock is advisory and OS-scoped.
8. `durability()` is a contract honoured by the concrete store; a hostile subclass could still lie. Only a
   trusted, non-injectable implementation fully closes this — which is the natural next step if King
   requires it.

## 6. Boundaries

No MCP server, tunnel, credential or exposure. H0 final freeze requires King's separate review and explicit authorization.
