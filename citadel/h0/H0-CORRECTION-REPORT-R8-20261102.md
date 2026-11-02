# H0 — Correction Report (revision 8)

**Date:** 2026-11-02T21:10+0330
**Trigger:** King review 2026-11-02T20:57 — Revision 7 "NOT ACCEPTED FOR FREEZE": the store remains replaceable after construction.
**Status:** substitution route closed and detected; threat model stated honestly.
**Additive only.** Revisions 1–7 reports and evidence remain unchanged on record.

---

## 1. The finding, and the evidence King used

Revision 7 bound the constructed store to `self.__audit`. Python name-mangling **renames** the attribute
(`_Kernel__audit`); it does not prevent assignment. A caller holding `k` could set
`k._Kernel__audit = hostile_object` and `handle()` would append through it.

**King found this in my own R7 report**, which stated that the migrated outage tests "replace
`_Kernel__audit` with a failing wrapper." I described the bypass in the same document where I claimed to
have closed the trust boundary. The read-only `k.audit` property blocked one name; it never protected the
underlying attribute.

King's distinction is exactly right: **R7 proved constructor non-injectability, not store
non-replaceability.**

---

## 2. Corrections

### R8-1 — the store is reached through a closure, not an attribute

```
self.__audit_getter = (lambda _s=store: _s)
```

`_bound_store()` calls that closure; `handle()` obtains the store from the closure on every use.
Reassigning `_Kernel__audit`, `audit`, `__audit` or `_bound_store` on the instance does not change what
the execution path uses. The attribute that previously held the store **no longer exists** (asserted by
test).

### R8-2 — substitution is detected, not silently followed

`_assert_store_identity()` runs at the audit gate and compares the bound store's `probe()` against the
probe captured at construction. A swapped getter yields `E_AUDIT_STORE_SUBSTITUTED` and the request is
refused. This is a *detection* guarantee layered on the closure, not a substitute for it.

### R8-3 — outages are simulated without a substitution route

Added `_FailureInjector`, a test-only fault switch that makes the **real** store report failure. It can
neither supply another implementation nor change where bytes go — both asserted. Every suite that
previously replaced `_Kernel__audit` was migrated to it; no suite substitutes an implementation into the
enforcement path any more (`grep` for `_Kernel__audit` across the suites: zero matches).

### R8-4 — the threat model, stated plainly

**Arbitrary code executing in the same Python process can tamper with objects and runtime behaviour.**
Python offers no access control that stops it. R8 therefore claims only that:

- the constructor cannot be given an implementation;
- the execution path does not read a reassignable attribute;
- substitution is detected when it occurs.

This is NOT claimed. It makes **no claim** about resisting an attacker who can already execute code inside the process.
Protection against that attacker requires a process or OS isolation boundary, which does not exist here
and is not part of H0. A test in the suite demonstrates that name-mangling is naming, not security, so
the design does not quietly rely on it.

---

## 3. Test evidence

| Suite | Result |
|---|---|
| `test_h0_contract_v8.py` (new: R8-1–R8-4) | **12/12 OK** |
| `test_h0_contract_v7.py` | **9/9 OK** |
| `test_h0_contract_v6.py` | **14/14 OK** |
| `test_h0_contract_v5.py` | **14/14 OK** |
| `test_h0_contract_v4.py` | **14/14 OK** |
| `test_h0_contract_v3.py` | **18/18 OK** |
| `test_h0_contract_v2.py` | **28/28 OK** |
| `test_h0_contract.py` | **32/32 OK** |
| `test_v41e_*.py` (regression) | **145/145 OK** |

---

## 4. Residual risks (unchanged; none resolved by any freeze)

1. Rate-limiter counters are in-process.
2. `ReplayStore` is in-memory — replay durability across restart remains open.
3. The verifier is injected; real ML-DSA message authentication is not wired in.
4. Payload schemas are Python-declared, not published JSON Schema.
5. No fuzzing or property-based testing.
6. The chain proves internal consistency, not non-substitution; the head digest is not externally anchored.
7. The single-writer lock is advisory and OS-scoped.
8. A second process importing `h0_audit_store` could append to the same file; the foreign-write check
   detects it only at the next kernel append.
9. **Same-process tampering is not prevented** (see R8-4). This is a design limitation, not an oversight.

## 5. Boundaries

No MCP server, tunnel, credential or exposure. H0 final freeze requires King's separate review and explicit authorization.
