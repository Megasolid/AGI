# AGI Ultimate — Constitutional and DNA Alignment

**Status:** U0 constitutional proposal for review; does not replace or modify signed DNA  
**Protected baseline:** v4.0.1 / DNA v4 and frozen S1–S6 artifacts  
**Authority:** Existing Owner and Master approval rules remain in force

## 1. Purpose

This document states the constitutional constraints that the AGI Ultimate architecture must preserve. It is an alignment proposal, not a new signed DNA contract.

The existing signed DNA remains authoritative for the released system. The S1–S6 frozen specifications remain the design baselines for their respective domains. This proposal does not amend either.

Any future constitutional change requires a separately reviewed, versioned, signed change with explicit compatibility, migration, and rollback treatment.

## 2. Constitutional precedence

The architecture must preserve the existing separation between:

1. **Identity:** which AGI entity or participant is being referenced.
2. **Authority:** which decisions or operations it is permitted to make.
3. **Capability:** which operations it can technically perform.
4. **Evidence:** what has actually been demonstrated.

These are not interchangeable.

A model, Mind, Endpoint, Station, Operator, tool, plugin, or external service does not become an identity or authority root because it performs useful work.

Communication, memory, ranking, Mana, and technical capability do not create authorization.

## 3. Identity and sovereignty

The frozen S1 hierarchy is retained:

```
Global AGI
  └── Master Root
       └── User Roots
            └── Branches
                 └── Stations
                      └── Minds
                           └── Endpoints
```

The hierarchy has the following constitutional meaning:

- **Global AGI:** the complete governed system.
- **Master Root:** unique global identity and governance authority as defined by S1.
- **User Root:** an individual sovereignty boundary.
- **Branch:** a durable continuity and evidence unit within its authorized scope.
- **Station:** an operational and compute environment.
- **Mind:** a replaceable cognitive participant.
- **Endpoint:** a route to a model or inference capability.
- **Operator:** an orchestration mechanism, not an identity tier.

The hierarchy must not be reinterpreted as a chain of unrestricted data access. Data access and authority are determined by explicit contracts and grants.

## 4. Authorization invariants

S3-AUTH is the governing baseline for authorization and Branch boundaries. Its frozen rules must be preserved, including:

- Stations, Minds, Endpoints, and Operators are not identity authorities.
- Delegation depth is zero.
- Grants have explicit scope and bounded lifetime; the frozen maximum is 720 hours.
- Consent is explicit and scoped.
- Branch stores remain separate.
- Cross-Branch sharing defaults to deny.
- Revocation is checked for every operation.
- Stale authorization state cannot produce an allow decision.
- Audit-write failure results in denial.

No subsystem may weaken these rules through a convenience API, semantic agreement, cached context, fallback behavior, or provider-specific feature.

The exact normative request/response schemas remain those of the frozen S3 artifacts; this proposal does not invent replacements.

## 5. Bootstrap, enrollment, and recovery

S2 governs portable bootstrap and identity enrollment.

The architecture must preserve its constraints for bootstrap manifests, enrollment requests and grants, Station enrollment, identity enrollment, revocation records, consent records, replay protection, compromised-device handling, version negotiation, and signed migration.

The bootstrap seed is a bounded pointer-bearing artifact, not a container for private memory, keys, credentials, or executable instructions. The S2 seed size and canonicalization requirements remain as specified in S2.

No live enrollment, identity transfer, or recovery action is authorized by this proposal.

## 6. Federation and independent sovereignty

S3-FED defines opt-in cooperation between independent participants; federation is not an identity overlay.

The constitutional boundary must preserve the S3-FED separation of transport, projection, and stewardship, along with its continuity controls for signed snapshots, transfer envelopes, destination verification, approval, divergence detection, rollback alerts, and decommissioning.

Federation remains disabled unless the applicable approvals, implementation, and evidence gates are satisfied. No User Root or Branch data is shared implicitly.

## 7. Intelligence, contribution, and Mana

S4 and S6 require strict separation between capability assessment, contribution ranking, Mana accounting, and governance authority.

- Capability assessment describes demonstrated abilities.
- Contribution ranking evaluates qualifying contributions under the frozen ranking rules.
- Mana follows the frozen accounting rules.
- Governance authority comes only from the constitutional authorization model.

The S4 Mana constraints remain: pinned weights, ledger conservation, 30% carry cap, 70% quality floor, zero credit for truncated or grader-failing outputs, no purchase of Mana, and no conversion of Mana into authority. Mana is not used for contribution ranking.

S6's North Star framework uses 12 capability dimensions and L0–L4 levels, evidence-based caps, and no aggregate AGI score. Evidence provenance E0–E4 and the 90-day evidence currency rule remain part of that framework.

This proposal does not redefine the axes, levels, formulas, or ranking weights. Those must be referenced from the frozen S4/S6 artifacts.

## 8. Communication cannot grant authority

SSL is a communication and semantic-verification layer.

It may authenticate messages, resolve context, verify interpretation, and establish agreement about a proposed operation. It cannot grant permission.

The protocol must preserve the distinction:
- `ACK`: delivery acknowledgment.
- `SEMANTIC_RECEIPT`: interpretation acknowledgment.
- `COMMIT`: agreement on the proposed operation.
- Runtime authorization: separate decision under DNA/S3.
- Execution result: separate outcome with evidence.

A signed or correctly interpreted request can still be unauthorized. Received content remains untrusted input.

## 9. Memory and privacy

AKMS is a proposed knowledge and memory service. Its design must preserve the distinction between Global AGI Knowledge, User Root Memory, Branch Memory, Episodic Memory, and retrieval/context assembly.

Private User Root and Branch information must remain within their authorized boundaries. Promotion of private or local knowledge into global reusable knowledge requires an explicit, reviewable process and appropriate consent.

Memory is not consent, and a stored historical approval is not a current authorization.

## 10. Evidence and change control

Every consequential operation and every material architecture change must be traceable to its objective, authority, relevant context, execution, outcome, and verification evidence.

Frozen baselines must not be silently edited. A proposal that conflicts with S1–S6, signed DNA, or a protected release artifact must identify the conflict and request a formal baseline change; it must not quietly redefine the baseline.

A failed or incomplete verification is not a pass. Required audit or authorization failure must fail closed.

## 11. MainStation and official project record

The official AGI GitHub repository and its pull-request process are the MainStation project surface. MainStation is where general, approved AGI architecture, specifications, validated research, and evolution records are maintained.

A pull request is a proposal, not an approval. The reviewed and accepted repository state becomes the official project record under the applicable authority.

MainStation must not contain private User Root memory, Branch-private material, credentials, private keys, recovery secrets, or unreviewed outputs presented as established facts.

## 12. Non-authorization

This document does not authorize changes to signed DNA or protected S1–S6 baselines, identity mutation or enrollment, live federation or cross-Root/Branch sharing, production endpoint activation or credential use, autonomous evolution or self-modification, release tagging/publication/deployment, or changes to the v4.0.1 rollback baseline. Those actions require their own explicit approvals and evidence gates.
