# H0 — Correction Report (revision 7)

**Date:** 2026-11-02T20:55+0330
**Trigger:** King review 2026-11-02T20:36 — Revision 6 "NOT ACCEPTED FOR FREEZE": trusted audit implementation open, R5 preservation test insufficient.
**Status:** trust boundary closed; genuine R5 concurrency test carried forward.
**Additive only.** Revisions 1–6 reports and evidence remain unchanged on record.

---

## 1. The finding

**Self-attestation, one layer deeper.** Revision 6 replaced a bare `is_durable` declaration with a
`durability()` contract — and the kernel still accepted *any injected object* whose contract returned
the right mapping. A hostile subclass could report every property while overriding `append()` to do
nothing, or to write somewhere that is not durable.

I named this risk in the R6 report and shipped it anyway. Naming a bypass is not mitigating it; a known
hole in an enforcement boundary is a blocker, not a caveat. That was my error, not King's discovery of
something I had missed.

---

## 2. Corrections

### R7-1 — the enforcement store is built by the kernel, not injected

`Kernel.__init__` no longer accepts `audit`. It accepts **`audit_path`** and constructs its own
`DurableAuditStore`, then verifies the concrete type it built. The store is held privately
(`_Kernel__audit`); `k.audit` is a read-only property.

There is therefore **no parameter through which a caller can supply an implementation.**

### R7-2 — a hostile subclass has no route in

Demonstrated rather than argued: a `Hostile` class whose `durability()` returns a perfect mapping is
still unreachable, because the kernel takes a path. A `Disguised(DurableAuditStore)` that overrides
`durability()` to lie and `append()` to never persist is **unrepresentable** — passing it raises
`TypeError` because the parameter no longer exists.

The test also records the uncomfortable truth: the contract checker *alone* would accept `Hostile`. That
is precisely why the store must never be caller-supplied.

### R7-3 — "reports success without persisting" is impossible by construction

The execution path and the persistence path are now the **same object the kernel created**. A test
asserts that the number of records the kernel reports equals the number of lines actually on disk.

### R7-4 — the real R5 concurrency test, carried forward

R6's "preservation" test did not reproduce the scenario it claimed. R7 carries forward the genuine
barrier-synchronised test: two concurrent requests, one executor failure and one success, asserting
**two distinct intents, two outcomes, zero dangling intents**, and that a **later unrelated denial is
still accounted for**.

---

## 3. Test evidence

| Suite | Result |
|---|---|
| `test_h0_contract_v7.py` (new: R7-1–R7-4) | **9/9 OK** |
| `test_h0_contract_v6.py` | **14/14 OK** |
| `test_h0_contract_v5.py` | **14/14 OK** |
| `test_h0_contract_v4.py` | **14/14 OK** |
| `test_h0_contract_v3.py` | **18/18 OK** |
| `test_h0_contract_v2.py` | **28/28 OK** |
| `test_h0_contract.py` | **32/32 OK** |
| `test_v41e_*.py` (regression) | **145/145 OK** |

---

## 4. Migration

Making the store non-injectable invalidated the injection-based mechanism **every earlier suite used to
simulate an audit outage**. Six suites were migrated to reach the kernel-built store instead:

- `kernel_for(...)` now takes a path;
- audit-outage tests replace `_Kernel__audit` with a failing wrapper (name-mangled, deliberate, and
  visible in the test source);
- disk assertions read `k.audit.path` rather than a path the test chose;
- the ordering test reads the record sequence instead of intercepting `append`.

That every suite had to change is again the signal: they were all written against a seam that should not
have existed. **This is the fourth time a test double had to be removed because it was standing in for
the guarantee being audited.**

---

## 5. Residual risks (unchanged; not resolved by any freeze)

1. Rate-limiter counters are in-process.
2. `ReplayStore` is in-memory — replay durability across restart remains open.
3. The verifier is injected; real ML-DSA message authentication is not wired in.
4. Payload schemas are Python-declared, not published JSON Schema.
5. No fuzzing or property-based testing.
6. The chain proves internal consistency, not non-substitution; the head digest is not externally anchored.
7. The single-writer lock is advisory and OS-scoped.
8. **A caller who imports `h0_audit_store` directly could still construct and use a store themselves.**
   The kernel refuses such objects, but nothing prevents a second, non-enforcing writer process from
   appending to the same file — the foreign-write check detects it only at the next kernel append.

## 6. Boundaries

No MCP server, tunnel, credential or exposure. H0 final freeze requires King's separate review and explicit authorization.
