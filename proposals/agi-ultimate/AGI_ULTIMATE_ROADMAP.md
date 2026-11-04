# AGI Ultimate — U0–U8 Roadmap

**Status:** Proposed dependency and release plan  
**Baseline:** v4.0.1 immutable rollback baseline; S1–S6 frozen foundations  
**Rule:** Planning approval is not implementation, deployment, or activation approval

## 1. Roadmap principles

1. Preserve v4.0.1 as the immutable rollback baseline.
2. Keep S1–S6 frozen unless a separately approved baseline change is required.
3. Implement additive changes on feature branches and submit them through MainStation PR review.
4. Do not infer operational readiness from a specification or passing unit tests alone.
5. Require traceability from each requirement to contract, implementation, test, evidence, and approval.
6. Keep live endpoints, credentials, federation, identity mutation, and production execution disabled until their explicit gates pass.
7. Publish negative and null research results as well as positive results.
8. Retain rollback and recovery paths for every consequential migration.

## 2. U0 — Constitutional and architectural proposal

**Goal:** establish one coherent target architecture before new implementation work.

Deliverables:
- `AGI_ULTIMATE_VISION.md`
- `AGI_ULTIMATE_DNA.md`
- `AGI_ULTIMATE_ARCHITECTURE.md`
- `AGI_ULTIMATE_PROTOCOLS.md`
- `AGI_ULTIMATE_ROADMAP.md`

Acceptance:
- Canonical S1 identity hierarchy is preserved.
- S2/S3 authorization, bootstrap, sovereignty, and federation constraints are traceable.
- S4/S6 capability, ranking, Mana, and research rules are not conflated.
- S5/E1–E6 dependencies and maturity are accurately represented.
- No unsupported role, identity tier, authority, implementation, or capability is introduced.
- Conflicts and gaps are recorded rather than silently resolved.
- Owner review and MainStation acceptance are recorded before U0 is treated as official.

U0 is documentation and architecture review only. It does not authorize runtime changes.

## 3. U1 — Identity, bootstrap, authorization, and security integration

**Goal:** establish a verified end-to-end path for identity, enrollment, consent, revocation, and Branch isolation.

Work:
- Reconcile S1/S2/S3 schemas and implementation.
- Verify identity and enrollment lifecycle.
- Integrate current revocation checks at every consequential operation.
- Verify stale-state and partition behavior.
- Verify Branch isolation and fail-closed audit behavior.
- Complete threat model and negative tests.

Gate:
- All required S1–S3 contract tests pass.
- Seeded unauthorized access and stale revocation cases are rejected.
- Evidence is replayable and independently reviewed.
- No protected DNA/baseline diff exists without explicit approval.

## 4. U2 — AKMS and durable memory

**Goal:** implement the proposed knowledge and memory service without violating sovereignty boundaries.

Work:
- Freeze AKMS schemas and service boundary.
- Implement Global AGI Knowledge, User Root Memory, Branch Memory, and Episodic Memory classification.
- Implement provenance, versioning, digest validation, expiry, consent, revocation, and supersession.
- Integrate E1 context manifests with S5.
- Implement minimum-sufficient context assembly.
- Test cross-Root and cross-Branch isolation.
- Define review and consent for promotion into global reusable knowledge.

Gate:
- Retrieval and writes are authorization-gated.
- Cross-scope negative tests fail closed.
- Revocation is enforced in live service paths.
- Provenance and memory lifecycle are auditable.
- Recovery and backup/restore preserve integrity.

## 5. U3 — SSL semantic communication

**Goal:** demonstrate reliable semantic handoff between independently initialized Minds.

Work:
- Freeze envelope schema and protocol state machine.
- Implement identity handshake, context resolution, semantic receipt, challenge/correction, and closure.
- Enforce hard constraints deterministically.
- Integrate AKMS references without exposing unrestricted memory.
- Add authentication, integrity, replay, expiry, and downgrade protections.
- Run two-Mind simulations and adversarial misunderstanding tests.
- Begin in isolated/shadow mode.

Gate:
- Seeded semantic misunderstandings are detected.
- Recoverable mismatches are corrected.
- Hard-constraint violations are rejected.
- No SSL message grants execution permission.
- Independent review and evidence replay pass.

## 6. U4 — Cognitive and provider adapters

**Goal:** make cognitive resources replaceable and measurable.

Work:
- Define Mind and Endpoint adapter contracts.
- Define capability declarations and probing.
- Record provider/model/version substitution.
- Preserve task and context continuity across provider changes.
- Evaluate single-Mind and multi-Mind baselines.
- Apply S4/S6 evidence and calibration rules.

Gate:
- Provider substitution does not alter AGI identity or Branch state.
- Capability mismatch is explicit; no silent substitution.
- Collaboration gains are demonstrated rather than assumed.
- Evaluation evidence is reproducible and current.

## 7. U5 — Provider-independent AGI Harness

**Goal:** integrate planning, orchestration, execution, approval, persistence, and recovery.

Work:
- Close E3 contract gaps before production prototype.
- Define service and plugin lifecycle.
- Define event/policy model and control protocol.
- Define execution identifiers and checkpoint semantics.
- Define approval, cancellation, quiescence, and effect reconciliation.
- Implement durable journal, replay, and evidence linkage.
- Integrate S5 leases, fencing epochs, Station ownership, parity, and succession.
- Provide offline deterministic test harness and fault injection.

Gate:
- No stale writer can commit.
- Cancellation proves quiescence or reports an unresolved incident.
- Duplicate side effects are prevented or reconciled.
- Recovery is tested across process and Station failure.
- Provider adapters cannot bypass policy.
- Independent security and recovery review passes.

## 8. U6 — Evaluation and controlled evolution

**Goal:** integrate S4/S6 research and evaluation into the operational development lifecycle.

Work:
- Integrate the 12-axis North Star assessment with L0–L4 levels.
- Preserve evidence caps, E0–E4 provenance, and 90-day currency.
- Maintain separate capability assessment, contribution ranking, Mana, and authority.
- Automate intake, triage, pre-registration, execution, independent review, and publication.
- Track benchmark versioning, contamination, and environment fingerprints.
- Require compatibility, security, and rollback analysis for changes.

Gate:
- No aggregate AGI score is introduced.
- Ranking and Mana cannot influence authority.
- Failed/null results remain discoverable.
- Capability claims are traceable and independently reviewable.
- Evolution cannot silently change protected baselines.

## 9. U7 — Federation

**Goal:** enable opt-in cooperation between independent AGI installations.

Work:
- Complete S3-FED implementation and operational threat model.
- Implement signed snapshots and transfer envelopes.
- Verify destination, provenance, replay protection, and consent.
- Implement divergence detection and resolution deadlines.
- Implement rollback and decommissioning.
- Test partitions and partial failure.

Gate:
- Independent identity and sovereignty are preserved.
- Cross-installation access is explicit and scoped.
- Divergence and revocation behavior pass adversarial tests.
- Federation activation receives separate explicit approval.

## 10. U8 — Integrated release qualification

**Goal:** qualify an integrated AGI Ultimate release without overstating its capabilities.

Work:
- Full regression and cross-version audit.
- Security and privacy review.
- Independent cryptographic verification with implementation diversity.
- Long-horizon and cross-context reliability.
- Provider substitution and continuity tests.
- Memory isolation and revocation tests.
- Semantic handoff adversarial suite.
- Operator recovery and effect-ledger fault injection.
- Federation conformance if U7 is approved.
- Release dossier, migration plan, compatibility matrix, and rollback drill.

Gate:
- Every release claim has evidence.
- Protected baselines are unchanged or changes are separately approved.
- Critical security findings are closed or explicitly accepted by the proper authority.
- Rollback is demonstrated.
- Owner approval is recorded before tag/publication/activation.

## 11. Cross-phase dependency map

```
U0 Constitution and architecture
  -> U1 Identity / authorization / security
       -> U2 AKMS and durable memory
            -> U3 SSL semantic communication
                 -> U4 Minds and provider adapters
                      -> U5 AGI Harness and succession
                           -> U6 Evaluation and controlled evolution
                                -> U7 Federation
                                     -> U8 Integrated qualification
```

Some offline research and contract work can proceed in parallel, but a dependent capability must not be activated before its prerequisite gates pass.

## 12. Current baseline and release honesty

The repository identifies v4.0.1 as the stable release and immutable rollback baseline. The v4.1-E-rc1 dossier records that candidate as unpublished, untagged, and not activated, with independent ML-DSA verification and real integration gaps outstanding.

The U0 proposal must not alter the v4.0.1 signed DNA, release artifacts, or rollback state. It must not be used to infer that v4.1-E or any U1–U8 capability is accepted.

The current repository and evidence state must be refreshed before each release decision. Historical test counts must not be copied forward as current results.

## 13. Change and review process

- All changes are additive on a dedicated branch.
- Every change is submitted through a MainStation pull request.
- PRs identify motivation, scope, source baseline, evidence, compatibility, security/governance impact, tests, and rollback.
- Protected files and frozen baselines are not changed without explicit authorization.
- Review comments and requested changes are resolved before acceptance.
- Merge, tag, publication, activation, and deployment are distinct decisions.

## 14. Definition of roadmap completion

A phase is complete only when its deliverables exist, the acceptance criteria pass, evidence is preserved, required independent review is complete, residual risks are explicit, and the appropriate authority accepts the phase.

A phase marked complete in a planning document is not proof of implementation or operational readiness.
