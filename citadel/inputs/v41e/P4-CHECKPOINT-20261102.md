# P4 checkpoint — endpoint roles, durable replay, key lifecycle, cross-process auth (initial)

**Date:** 2026-11-02T08:40+0330  
**Status:** additive P4 increment; **no frozen/DNA change, no network/credentials, no release artifact**.  
**Commit:** `fe9d6575ecc86cc0a50f288d42c90c37c41e8fdf` (pushed to `main`).  
**Tests:** **90/90 OK** (80 prior + 10 P4); evidence `P4-TEST-OUTPUT.txt`; sha256 `f204a2461106e6cba502d69d917cea4faeed7cd97374cca31fdbe458d09e81e2`.

## 1. Files

| File | sha256 |
|---|---|
| `runtime/agi_sem_replay.py` | `1c4d0f659f60b86109bdf2c9feaf28ea708018d7f4dcb68e8107ebbceccd1128` |
| `runtime/agi_sem_keys.py` | `261253e07d00a046faa37192e49987edc5940c245b559d3ade1883f62a5cbff6` |
| `runtime/agi_sem_roles.py` | `c2cfa0f35b804fbf9b8a5482aa5cbdf4d99f413d849f2605ece6cf438b0188a1` |
| `runtime/agi_sem_ipc.py` | `2afa8ce58cedee34ac577e1bd6b0551e9c79b61cf1c2728d82f3b78ab8c1a994` |
| `runtime/test_v41e_p4.py` | `13d1204cb67dc12416f91b5b1e90d61a48395245174c729458091df8c0527e05` |

## 2. Implemented

- **Endpoint roles** (`RoleChannel`): initiator / responder / verifier message-type policy; unknown endpoints and role violations fail closed; receiver isolation.
- **Durable replay store** (`ReplayStore`): append-only JSONL, `(session_id, message_id)` key, same digest idempotent, different digest replay fail, corrupt store fail-closed.
- **Durable channel** (`DurableChannel`): auth + binding + schema + replay store before session delivery; restart-safe idempotent duplicate returns `idempotent` without re-processing.
- **Key lifecycle registry** (`KeyRegistry`): metadata-only active/retired/revoked, purpose, `not_before`/`not_after`; rotation/revocation tests; no private keys.
- **Cross-process auth check** (`agi_sem_ipc.py`): local subprocess, serialized message + mock HMAC secret via environment; valid passes, tampered fails. Proves process boundary + serialization, not production transport.
- **Tests:** role handshake, responder→INTENT rejection, unknown endpoint, receiver isolation, replay store idempotent/conflict/corrupt, durable restart, key active/retired/revoked/expiry/rotation, cross-process valid/tamper.

## 3. Tests

```
python -m unittest discover -s runtime -p "test_v41e_*.py" -v
```
**Ran 90 tests — OK.**

## 4. Not implemented / limitations

| Item | Status |
|---|---|
| ML-DSA auth | mock HMAC in tests; P0 task signing uses device key separately |
| Key distribution / private-key custody | metadata registry only; no distribution |
| Endpoint process isolation / sandbox | in-process roles + local subprocess auth only |
| Partition behavior / replay-store recovery across hosts | not implemented |
| Per-endpoint independent session state | single shared session; role policy only |
| Production transport | not implemented |
| E3/E5/E6 | not started |

## 5. Security caveats

- Role policy is a semantic message-type restriction, not authority/consent/execution.
- A role cannot grant itself authority; no grant/consent fields exist.
- Durable replay is local-file based; no cross-host/global replay protection.
- Cross-process test is a local subprocess with mock HMAC; not transport security proof.
- Frozen DNA v4/S1–S6 unchanged; v4.0.1 remains rollback.

## 6. Next

Kilo independent P4 review, then P5 only after both. Remaining P4: real ML-DSA auth/key distribution, endpoint process isolation, partition/recovery tests, per-endpoint state, production transport.
