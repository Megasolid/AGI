# H0 — Correction Report (revision 2)

**Date:** 2026-11-02T19:55+0330
**Trigger:** King review 2026-11-02T19:27 — five findings against the H0 reference kernel.
**Status:** all five corrected; new adversarial tests added.
**This report is additive.** The revision-1 signed evidence (`H0-TEST-OUTPUT-20261102.txt`, sha256 `92db7ee1…`) and its meaning are unchanged and remain on record.

---

## 1. The five findings and what was actually wrong

| # | King finding | Verdict | Root cause |
|---|---|---|---|
| F1 | Audit is not a precondition to execution | **Correct — security bug** | Kernel executed first, then audited; on audit failure it decremented an `executed` counter to pretend nothing happened. The side effect had already occurred. |
| F2 | Kernel checks scope before rate; contract says rate → scope; tests never assert ordering | **Correct** | I wrote the contract, then implemented a different order, and tested neither. |
| F3 | Replay check and mark are separate; marking occurs after execution | **Correct — concurrency bug** | Two concurrent duplicates could both pass the check before either marked. |
| F4 | No per-method payload schemas | **Correct** | `payload` was only checked to be an object plus size caps. |
| F5 | `issued_at` never validated | **Correct** | Only `expires_at` was checked. |

**The governing principle, accepted verbatim:** *a denial response is not proof that an action was prevented.*

---

## 2. Corrections

### F1 — audit as a durable precondition

The audit record is appended **before** the executor is called. If the append raises, the executor is never invoked:

```
audit.append(allow_record)   # must succeed
result = self.executor(request)   # only now
```

Tested with an executor that counts its own invocations: **0 invocations** when audit fails (`test_executor_not_invoked_when_audit_fails`), and an ordering recorder proving the sequence is `audit:allow` → `execute` (`test_audit_success_precedes_execution`).

The counter-decrement substitute is deleted.

### F2 — declared order, asserted by tests

`ORDER = (auth, replay, schema, payload, limits, rate, scope, policy, audit, execute)` is a module constant. The kernel records every gate it passes in `order_seen`; tests assert:

- an allowed request traverses `ORDER` exactly;
- a policy denial stops at index 8 (never reaching `audit` or `execute`);
- a scope violation occurs at its declared position.

### F3 — atomic reservation

`ReplayStore` reserves `request_id` and `nonce` under a lock **before any effect**, and releases the reservation if the request is denied before execution, so a denial cannot permanently burn an identifier. Tests:

- 16 threads firing the same `request_id`: **exactly 1 succeeds**, 15 get `E_REPLAY`;
- 12 threads firing the same `nonce`: **exactly 1 succeeds**;
- a scope-denied request releases its reservation and can be retried;
- a successful request consumes its identifier permanently.

### F4 — per-method payload schemas

`PAYLOAD_SCHEMAS` defines required / optional / typed fields for **every** registered method, with strict unknown-field rejection (`E_UNKNOWN_PAYLOAD_FIELD`). Tests cover unknown fields for every method, missing required fields, wrong types, and `bool` explicitly rejected where `int` is expected.

### F5 — timestamps

`validate_timestamps` enforces: both present, strict ISO-8601, mandatory timezone, `issued_at < expires_at`, `expires_at > now`, and `issued_at` no more than 300 s in the future (`E_CLOCK_SKEW`). Tests cover naive, future, inconsistent, expired, missing and unparseable values.

---

## 3. Test evidence

| Suite | Result |
|---|---|
| `test_h0_contract.py` (revision 1, preserved) | **31/31 OK** |
| `test_h0_contract_v2.py` (new adversarial) | **28/28 OK** |
| `test_v41e_*.py` (regression) | **145/145 OK** |

Revision-1 tests required three corrections, and each one is itself a finding:

1. `test_audit_failure_downgrades_allow_to_deny` **asserted the bug** — its name and its `"downgraded"` note only made sense while the kernel had the F1 defect. It now asserts that nothing executes.
2. `test_internal_error_denies` patched `k._execute`, which no longer exists; executor injection is now the supported seam.
3. `test_expired_request` and `test_read_scope_cannot_write` built envelopes with empty payloads, which under F4 are now correctly rejected earlier. Their fixtures were fixed, not the kernel's ordering.

None of these were "fix the test until it goes green": each change is justified by a contract clause, and the kernel's order was never bent to satisfy a test — when a test wanted a different order, I re-read the contract and restored the contract.

---

## 4. What this does NOT change

- No MCP server, tunnel, credential or socket exists. The kernel is a verifier, not a server.
- No exposure. H0 completion still requires separate review and explicit authorization.
- No protected file, tag, publication or activation.
- The five findings were implementation/conformance defects. The H0 **design** was not discarded.

## 5. Residual risks still open in H0

1. Rate limiter state is in-process; a multi-instance deployment needs shared counters.
2. `ReplayStore` is in-memory; durable replay protection across restarts needs a persistent store.
3. The verifier is injected; real ML-DSA message authentication is not wired into the kernel.
4. Payload schemas are Python-declared, not published JSON Schema artifacts.
5. Audit is an in-memory list; durable append-only storage is not implemented.
6. No fuzzing or property-based testing has been performed.
