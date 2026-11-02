# H0 — Correction Report (revision 9)

**Date:** 2026-11-02T21:15+0330
**Trigger:** King review 2026-11-02T21:05 — Revision 8 "NOT ACCEPTED FOR FREEZE". Three blocking findings plus an evidence-count correction.
**Status:** same-probe attack closed by object identity; the guarantee is now narrowed to what the implementation actually enforces.
**Additive only.** Revisions 1–8 reports and evidence remain unchanged on record.

---

## 1. The findings

| # | Finding | Verdict | Real defect |
|---|---|---|---|
| R9-1 | The closure getter is still replaceable | **Correct** | `_bound_store()` read `self.__audit_getter` on every call. A closure is not protected by its captured value; the reference used to *retrieve* it was a plain instance attribute. My own R8 test performed this replacement. |
| R9-2 | The probe is not an identity guarantee | **Correct** | `probe()` returns a string derived from the store path. A substitute returning the same string passed. Both the getter and the expected probe lived in replaceable attributes. |
| R9-3 | The stated narrow guarantee was not established | **Correct** | R8 claimed "the execution path does not read a reassignable attribute." The source showed it did. |
| R9-4 | Report said 12/12; artifact said 10/10 | **Correct** | Reports and evidence disagreed in the one document whose purpose is trustworthy numbers. |

---

## 2. Corrections

### R9-1 / R9-2 — identity, not a forgeable string

- The per-instance getter is **removed**. `_bound_store()` resolves the store through a
  **class-level table** keyed by kernel instance, never through an instance-held callable.
- `_assert_store_identity()` compares the instance attribute against the class-resolved store by
  **object identity** — `self._trusted_store is not _TrustedStore.resolve(self)` — which a forged probe
  string cannot satisfy.
- `probe()` is **demoted to a diagnostic label** and documented as *not* an identity guarantee.

The same-probe attack King named is now tested directly: a `ForgedStore` whose `probe()` returns the
exact expected string is refused with `E_AUDIT_STORE_SUBSTITUTED`.

### R9-3 — the guarantee, narrowed to the truth

R9 does not defend against arbitrary code executing in the same process, and **does not claim** that an in-process attacker is defeated. A test records what such an attacker can
do: it can import `_TrustedStore` and rebind the class table, and the test asserts that this works. That
is deliberate — the limit is demonstrated, not described.

What R9 does enforce:

1. the constructor cannot be given an implementation;
2. ordinary instance-attribute reassignment of the audit binding is **detected** (object identity);
3. a substitute that forges the probe is **detected**;
4. accidental misuse and careless mutation are caught.

What it does **not** enforce: arbitrary code executing in this process. Protecting against that requires
a **process or OS isolation boundary**, which does not exist here and is not part of H0.

### R9-4 — evidence counts reconciled

Every count below was taken from the actual suites, not from a previous report. A test in the v9 suite
parses this report and fails if any claimed count disagrees with the suite's real test count.

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
| `test_v41e_*.py` (regression) | 145 | OK |

Total H0 contract tests: **146**.

---

## 4. Defects found while correcting

1. **First R9 attempt bound the store in a single class-level closure**, so the *first* kernel's store
   was returned for every later kernel. Every suite failed at once — which is how it was caught.
   Replaced with a per-instance WeakKeyDictionary.
2. The v8 suite referenced the removed getter; its three assertions were retargeted to the R9 mechanism
   without changing what they test.

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
9. **Same-process tampering is not prevented and is not claimed to be**; a test demonstrates the limit.

## 6. Boundaries

No MCP server, tunnel, credential or exposure. H0 final freeze requires King's separate review and explicit authorization.
