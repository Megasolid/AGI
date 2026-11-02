# P6 checkpoint — E5 capability quarantine + E6 evidence/recovery (initial)

**Date:** 2026-11-02T09:20+0330  
**Status:** additive P6 increment; **no frozen/DNA change, no network/credentials, no execution, no release artifact**.  
**Commit:** `259ed16aa317a48f9a62dbdd3bc3bb0074a4c0e5` (pushed to `main`).  
**Tests:** **126/126 OK** (110 prior + 16 P6); evidence `P6-TEST-OUTPUT.txt`; sha256 `082ec4bb34757c01faf8d9fd460995e252185869cdaafe7d616c607c975377fc`.

## 1. Files

| File | sha256 |
|---|---|
| `runtime/agi_capability.py` | `a558b7e847dabd67e50c9b3a4d1f2af22d0f0c93a6adb22332cb6491edef8cf8` |
| `runtime/agi_evidence.py` | `59faadd3052112ef521092277e2adc099a42cc4dc17fed04c1dacb0b89e1f7d1` |
| `runtime/test_v41e_capability.py` | `15ec45c61c7c8ca8ab586ed88ae6de79b6da872f2f3c53092d0d0bc9409d46fb` |
| `runtime/test_v41e_evidence.py` | `fd1926593887d771dc002a6b831713e66a971a33565118515c064f6f97dc5afa` |

## 2. Implemented E5

- Metadata-only capability manifest: id/version/class A-B-C, publisher/source, tree SHA-256, per-file hashes, requested permissions, evaluation/governance refs, `no_identity_authority: true`.
- Forbidden instruction/script fields rejected (`instructions`, `skill_md`, `body`, `scripts`, `content_text`).
- Lifecycle: quarantined → evaluated (scan/eval/local refs) → approved (approval ref) → revoked.
- World view: metadata only, `authorized: false`, no instructions/bodies, explicit "listing is not authorization".
- Activation requires an S3-style allow decision (`operation=activate_capability`, `revocation_checked`, grant id) plus a matching grant; returns metadata-only activation token; sandbox hook receives no instructions; `instructions_loaded: false`.
- Tests: instruction body rejected, bad file hash, world view metadata, unauthorized activation, revoked activation, evaluation refs.

## 3. Implemented E6

- Evidence packet: run/claim/evidence refs/environment/E-level/artifact hashes/review refs, canonical digest; validation; evidence gap check.
- Effect ledger: append-only JSONL, duplicate idempotent, conflict/corrupt fail-closed.
- Reconciliation: emitted effects not in checkpoint are reported, never silently discarded.
- Recovery controller: detected→isolated→replaying→verified/resumed or incident/degraded; verify requires state digest, effect reconciliation and valid lease; resume only after verified.
- Tests: packet gap/digest/E-level, ledger idempotent/conflict/corrupt, reconciliation, recovery order/digest/lease.

## 4. Tests

```
python -m unittest discover -s runtime -p "test_v41e_*.py" -v
```
**Ran 126 tests — OK.**

## 5. Not implemented / limitations

| Item | Status |
|---|---|
| Real sandbox/execution | sandbox is a callable harness hook; no process isolation |
| Package byte verification | manifest hashes only; no signed package fetch |
| Network catalogue sync | disabled/not implemented |
| Real S3 decision / grant issuance | caller-injected; no authority creation |
| Evidence independence/E-level review | not implemented; packet is metadata |
| Durable effect ledger across hosts | local file only |
| Recovery integration with OperatorJournal | not wired |
| E3 full operator / E5/E6 production | initial primitives only |

## 6. Security caveats

- Capability registration/evaluation/approval **never** grants activation or execution authority.
- Activation requires an explicit S3-style allow + matching grant; the module cannot mint either.
- Instructions are never loaded into privileged context; sandbox hook receives metadata only.
- Evidence packet is not proof of truth; E-level and independent review remain required.
- Frozen DNA v4/S1–S6 unchanged; no network/credentials/live execution.

## 7. Next

Kilo independent P6 review, then release-candidate evidence/KING review. Remaining P6: real sandbox, package verification, network sync policy, S3 integration, E-level review, operator-journal recovery wiring.
