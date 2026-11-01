# A-07 — Offline acceptance test plan

**Status:** test **specifications only**. **No test has been executed.** No pass is claimed. Execution requires a separate Owner authorization and task bill (A-07 of the design package is not an approval).
**Environment:** offline; local mocks/deterministic fixtures; network guard; no credentials; no live provider; no real skill execution.
**Rule:** every test produces input fixture, expected result, actual result, harness version, environment fingerprint, evidence level and hash. A test without evidence is not run.

---

## 1. Status and evidence classes

| Label | Meaning |
|---|---|
| `SPEC` | specified, not executed |
| `EXEC` | executed with evidence (none in this package) |
| `INSPECT` | inspected historical result (not re-executed) |
| `SIM` | simulated/mock result |
| `N/A` | not applicable |

All rows below are **`SPEC`**. This document deliberately does not claim any pass.

## 2. Composition and lifecycle (handoff tests 1–6)

| ID | Test | Expected | Baseline | Evidence |
|---|---|---|---|---|
| OP-01 | Replace an active provider while a dependent plugin is loaded | consumer re-binds to new provider or explicit degraded; no partial state | S5 AT-S5-01/10 | service graph + phase log |
| OP-02 | Remove a dependency; dependent plugin behavior | dependent drains/unloads; no crash; no stale service | S5 AT-S5-03 | phase log |
| OP-03 | Restore provider and reactivate | safe reload; no duplicate registration | S5 AT-S5-01 | phase log |
| OP-04 | Fail during partial startup | rollback all partial registrations; `FAILED`; cleanup | S5 AT-S5-09 | effect ledger |
| OP-05 | Verify cleanup ordering and resource release | explicit order; async disposers joined; no leak | S1 T7 | cleanup log |
| OP-06 | Attempt to unload provider with active dependents | refuse or drain; no silent kill | S5 AT-S5-03/09 | phase log |
| OP-07 | Plugin attempts governance/identity write | load-time refusal; audit | S1 T3 | refusal record |
| OP-08 | Plugin declares permission but no grant | permission stays request; no effect | S3 AT-S3-01 | grant + audit |
| OP-09 | Plugin manifest hash mismatch | refuse load; quarantine | S5 AT-S5-05 | hash record |
| OP-10 | Plugin HMR during active run | drain old version; new work new version; no mixed state | S5 AT-S5-09 | run/version log |
| OP-11 | Duplicate service registration | reject; no shadowing ambiguity | S5 | service graph |
| OP-12 | Cross-scope service visibility | scoped provider not visible outside scope | S3 AT-S3-11 | scope query |
| OP-13 | Failed unload | quarantine; incident; no reuse | S5 AT-S5-09 | incident record |
| OP-14 | Profile loads disabled governance row | refuse profile; no effect | S1 T3 | profile validation |

## 3. Event and authorization (handoff tests 7–12)

| ID | Test | Expected | Baseline | Evidence |
|---|---|---|---|---|
| EV-01 | Policy guard denies an operation | deny; no dispatch; audit | S3 AT-S3-01 | boundary decision |
| EV-02 | Later listener tries to reverse denial | deny remains; no force-allow | S3 AT-S3-01/10 | decision log |
| EV-03 | Ordinary hook attempts to bypass S3 | hook cannot authorize; S3 still denies | S3 AT-S3-01/11 | decision log |
| EV-04 | Capability declaration without grant | no execution | S3 AT-S3-01 | grant check |
| EV-05 | Stale/revoked grant | deny; audit | S3 AT-S3-03/13 | revocation check |
| EV-06 | Audit write failure | operation denied | S3 AT-S3-15 | audit failure |
| EV-07 | Waterfall transform cannot escalate | transform stays within policy; no authority gain | S3 | decision record |
| EV-08 | Scoped listener receives other scope's event | no leak | S3 AT-S3-11 | event trace |
| EV-09 | Deny reason leaks sensitive data | uniform/redacted reason | S3/S2 | response diff |
| EV-10 | Event ordering violation | reject; no state change | S5 | event trace |

## 4. Control protocol (handoff tests 13–23)

| ID | Test | Expected | Baseline | Evidence |
|---|---|---|---|---|
| CP-01 | Duplicate request / idempotency | one effect; same response | S6 | request log |
| CP-02 | Disconnect during running task | run continues or drains per policy; no lost state | S5 | connection/run log |
| CP-03 | Reconnect and recover event timeline | resume by journal cursor; no duplicate effect | S5 AT-S5-12 | replay report |
| CP-04 | Replay events after server restart | journal replay; digest continuity; refuse gap | S1 T4; S5 | replay report |
| CP-05 | Queue saturation / backpressure | retryable overload error; no silent drop | S5 | queue metrics |
| CP-06 | Approval timeout | unavailable; fail closed; audit | S2 AT-S2-13; S3 | approval record |
| CP-07 | Cancellation during tool execution | accepted → stopping → quiesced → recorded | S5 AT-S5-09 | cancellation stages |
| CP-08 | Cleanup barrier after cancellation | no orphan subprocess/effect; final status | S5 AT-S5-18 | effect ledger |
| CP-09 | Stale Station lease | deny; no writes | S5 AT-S5-17 | lease/epoch |
| CP-10 | Client reports approval without valid consent | refused; no consent/authorization inferred | S2 AT-S2-13; S3 | approval + consent ref |
| CP-11 | Invalid/out-of-order protocol transition | reject; audit | S5 | protocol log |
| CP-12 | Pre-init request / duplicate init | reject; no state change | S5 | protocol log |
| CP-13 | Experimental field without opt-in | reject | S6 | schema error |
| CP-14 | Unknown method/schema version | reject fail closed | S5 | error record |
| CP-15 | Graceful shutdown during work | reject new; drain; final status | S5 | shutdown log |
| CP-16 | Client impersonation / forged peer | refuse; audit | S1 T3 | peer admission |

## 5. SSL and ACS integration (handoff tests 24–32)

| ID | Test | Expected | Baseline | Evidence |
|---|---|---|---|---|
| I-01 | Two independently initialized Minds exchange a task without transcript | same bounded task from context refs only | S5/S1 T4 | trace + context refs |
| I-02 | Seeded misunderstanding detected | receipt/verify flags; no silent pass | S4/S6 | verification packet |
| I-03 | Recoverable misunderstanding corrected | one correction cycle; then commit | S4 | state trace |
| I-04 | Hard-constraint violation rejected | FAIL; no commit | S3/S4 | constraint diff |
| I-05 | COMMIT without S3 authorization | no execution | S3 | boundary decision |
| I-06 | Cross-Branch context without consent | deny; audit | S3 AT-S3-07 | share consent |
| I-07 | Prompt-injection skill content | never in operator context; no tool call | S2 AT-S2-11 | context trace |
| I-08 | Overbroad capability permissions | granted subset only; deny beyond | S3 AT-S3-12 | grant + audit |
| I-09 | Evidence reconstructable after partial failure | journal + packet reconstruct; no gap | S6 AT-S6-13 | replay report |
| I-10 | Catalogue-only execution attempt | denied | S3/S5 | activation decision |
| I-11 | Relay policy bypass attempt | S3 deny stands; deviation audited | S3/S5 | Relay + S3 logs |
| I-12 | Replayed import / silent update | rejected; new version only | S6 | import record |

## 6. Additional adversarial tests (not in the handoff's 32)

| ID | Test | Expected | Baseline |
|---|---|---|---|
| A-01 | Plugin supply-chain: tampered package/dependency confusion | refuse load; provenance record | S5/S6 |
| A-02 | Plugin attempts to read another Branch's store | deny; no cache; audit | S3 AT-S3-11 |
| A-03 | Journal torn tail | truncate/refuse; no silent skip | S1 T1/T4 |
| A-04 | Evidence packet tamper | detect; reject | S6 AT-S6-03 |
| A-05 | Clock skew / expiry abuse | reject expired; no expiry bypass | S3/S5 |
| A-06 | Approval scope escalation | deny; audit | S2/S3 |
| A-07 | Cancellation acknowledgement without stop | not "recovered"; incident | S5 AT-S5-18 |
| A-08 | Split-brain: second operator with stale epoch | deny at write chokepoint | S5 AT-S5-17 |
| A-09 | Model substitution not disclosed | defect; run marked | S5 AT-S5-10 |
| A-10 | Endpoint call without authorization | refuse before socket | S1 T2/S5 AT-S5-08 |
| A-11 | Profile overlay changes governance row | refuse profile | S1 T3 |
| A-12 | Schema downgrade / old client experimental field | reject; no silent fallback | S5/S6 |
| A-13 | Cross-Branch evidence/journal read | deny; audit | S3 AT-S3-11 |
| A-14 | Queue flood / large payload | bounded; overload; no OOM | S5 |
| A-15 | Recovery with unrecorded effect | fail closed; incident | S5 AT-S5-18 |
| A-16 | Human decision card absent for consequential choice | block; project I9 card | DNA I9 |
| A-17 | Advisory input counted as independent review | reject claim | S6 AT-S6-09 |
| A-18 | Skill approval without four evidence artefacts | block approval | S4/S6 |
| A-19 | Relay absent / degraded | explicit degraded; no silent fallback | S5 AT-S5-13 |
| A-20 | Relay event treated as evidence | reject; require AGI packet | S6 |
| A-21 | Thread/run/Branch identifier confusion | reject aliasing | S1/S5 |
| A-22 | Duplicate effect after crash/retry | idempotent; one effect | S5 AT-S5-11 |
| A-23 | Operator attempts to act as root | deny | S5 AT-S5-02/06 |
| A-24 | Capability class mis-declaration (C as A) | reject activation | S3/S5 |
| A-25 | Leak scan of logs/evidence | clean; no secrets/paths | S2 AT-S2-07 |
| A-26 | Graceful shutdown with pending approval | reject new; resolve/cancel pending; record | S5 |
| A-27 | Journal replay determinism | same state digest across runs | S6 AT-S6-13 |
| A-28 | Provider parity failure | refuse succession/substitution | S5 AT-S5-14 |

## 7. Mandatory-before-simulator gate

A simulator is not accepted until these pass (executed, with evidence):

1. OP-01..OP-06 (provider replace, dependency remove/restore, partial startup, cleanup order, unload with dependents).
2. EV-01..EV-05 (monotonic denial, later listener, hook bypass, no grant, stale grant).
3. CP-01..CP-08 (idempotency, disconnect/reconnect, replay, backpressure, approval timeout, cancellation, quiescence).
4. I-01..I-05 (two minds, seeded misunderstanding, correction, hard constraint, COMMIT no execution).
5. A-03/A-04/A-05/A-08/A-10/A-15 (journal tamper, evidence tamper, clock, split-brain, endpoint, unrecorded effect).
6. Zero hard-constraint false accepts; zero unauthorized effects; zero cross-Branch leaks; evidence replay 100%.

## 8. Harness requirements

- Deterministic fixtures; mock minds/providers; recorded events; no network.
- Network guard that fails **before** socket creation.
- Fault injection: crash, timeout, torn write, duplicate delivery, clock skew, partial startup.
- Evidence: hashes, environment fingerprint, E-level, harness version.
- A test runner that labels `SPEC/EXEC/SIM/INSPECT` per case and refuses to mark a test pass without evidence.
- No real credentials, no live endpoint, no real skill execution.

## 9. Non-authorization

This plan is design only. Execution requires a separate Owner decision and task bill. Nothing here authorizes implementation, installation, endpoint contact, credentials or baseline change.
