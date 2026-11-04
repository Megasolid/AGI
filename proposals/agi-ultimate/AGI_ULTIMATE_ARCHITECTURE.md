# AGI Ultimate — Complete System Architecture

**Status:** U0 architecture proposal for review; not a shipped architecture  
**Baseline:** S1–S6 frozen designs; E1–E6 work; AGI v4.0.1 stable

## 1. Architectural model

AGI is a persistent, portable cognitive organism implemented as governed software. Its identity and continuity are not reducible to a model session. Models are replaceable cognitive hosts; AGI supplies the identity, memory, authorization, communication, orchestration, evidence, and evolution infrastructure around them.

This document integrates existing foundations. It does not silently replace frozen decisions or claim that proposed services are already operational.

## 2. Canonical identity structure

S1 defines the canonical hierarchy:

```
Global AGI
  └── Master Root
       └── User Roots
            └── Branches
                 └── Stations
                      └── Minds
                           └── Endpoints
```

- **Global AGI:** complete governed ecosystem.
- **Master Root:** global identity and governance authority.
- **User Root:** individual sovereignty boundary.
- **Branch:** durable continuity and evidence unit.
- **Station:** operational and compute environment.
- **Mind:** replaceable cognitive participant.
- **Endpoint:** model-access and inference route.
- **Operator:** orchestration mechanism; not an identity tier.

The hierarchy defines identity relationships, not unrestricted inheritance of data access. Authorization remains governed by S3-AUTH.

## 3. Architecture domains

### 3.1 Identity, bootstrap, and governance

S1 and S2 define identity, canonical relationships, portable bootstrap, enrollment, recovery, consent, and revocation records. This domain preserves identity integrity and portability. It does not provide arbitrary memory access or execution permission.

### 3.2 Authorization and sovereignty

S3-AUTH defines permission checks, Branch separation, grant scope and lifetime, revocation freshness, consent, and fail-closed behavior.

Its frozen rules include: Stations, Minds, Endpoints, and Operators are not identity authorities; delegation depth is zero; grants have explicit scope and a maximum lifetime of 720 hours; consent is explicit and scoped; Branch stores remain separate; cross-Branch sharing defaults to deny; revocation is checked for every operation; stale authorization cannot produce an allow decision; audit-write failure results in denial.

### 3.3 Federation

S3-FED defines opt-in cooperation between independent participants. Its design separates transport, projection, and stewardship and defines continuity controls for snapshots, transfer envelopes, destination verification, approvals, divergence, rollback, and decommissioning.

Federation is a later integration domain, not a prerequisite for local AGI continuity. It remains non-operational until separately authorized and verified.

### 3.4 Knowledge and memory — AKMS proposal

The AGI Knowledge and Memory Service (AKMS) is the proposed durable memory and knowledge service. It extends the E1 context-continuity direction; it is not established as a complete operational service.

Its logical domains are:

1. **Global AGI Knowledge:** approved reusable knowledge.
2. **User Root Memory:** private user-specific information and preferences.
3. **Branch Memory:** project continuity, decisions, objectives, and relevant context.
4. **Episodic Memory:** event, task, experiment, and outcome records.
5. **Retrieval and Context Assembly:** authorized, relevance-based retrieval with provenance, version, expiry, consent, and revocation checks.

AKMS must preserve provenance and distinguish an observed event, a model-generated assertion, a reviewed finding, and approved reusable knowledge. Retrieval should provide the minimum sufficient authorized context.

E1 includes context manifests, Branch references, versions, digests, scope/classification metadata, expiry and consent references, and fail-closed revocation interfaces. The current state assessment identifies real S5 memory-gateway integration and live revocation integration as outstanding. AKMS must close these gaps rather than claim them solved.

### 3.5 Semantic communication — SSL proposal

The Semantic Signal Layer (SSL) is the proposed AGI communication contract for independent Minds and services.

Its responsibilities are message/session protocol, identity and capability handshake, intent representation, context reference and version resolution, independent interpretation, semantic receipt and constraint verification, challenge/correction, agreement on a proposed operation, result communication, and evidence references.

SSL does not own memory, identity, authorization, or execution. DNA/S3 remains authoritative. The protocol should begin in isolated or shadow operation and must not control execution until its schema, state machine, security, and adversarial tests pass.

### 3.6 Cognitive participants and Endpoints

Minds are replaceable cognitive participants. Endpoints provide access to model inference. The architecture must support different providers and local or hosted models without binding identity or memory to a provider.

Mind selection should be based on task requirements and demonstrated capabilities. Multiple Minds do not automatically improve results; collaboration must be evaluated against single-Mind baselines.

### 3.7 Operator and AGI Harness

The Operator coordinates work across Branches, Stations, Minds, Endpoints, and authorized capabilities.

The proposed provider-independent AGI Harness should provide task intake and objective resolution, planning and decomposition, context assembly, Mind/Endpoint selection, capability discovery and admission, scheduling and resource control, approval and cancellation, execution coordination, event durability and replay, outcome verification, recovery, and handoff.

The Operator is not an identity authority. The control interface is not an authorization authority. A plugin or service declaration is not a grant.

E3 identifies contracts required for service model, plugin lifecycle, event/policy model, control protocol, execution primitives, approval/cancellation, event durability/replay, security boundaries, baseline traceability, provider substitution, recovery, and runtime profiles. These contracts and their negative tests must be complete before a production Operator prototype.

### 3.8 Capabilities and quarantine

Capabilities include tools, skills, external services, local computation, and multimodal processing. E5 establishes capability quarantine as a design workstream. New or untrusted capabilities must be isolated and evaluated before broader admission. Declared capability is not proof of safe implementation or permission.

### 3.9 Intelligence evaluation, ranking, and Mana

S4 defines intelligence evaluation, contribution ranking, and Mana. S6 defines the North Star assessment and research lifecycle.

These remain separate:
- Capability assessment: 12 dimensions, L0–L4, evidence-based caps, no aggregate AGI score.
- Contribution ranking: governed by frozen S4 rules.
- Mana: separate conserved accounting system under frozen S4 rules.
- Authority: exclusively governed by identity and authorization contracts.

Evaluation integrity requires seeded and held-out tests, deterministic graders, contamination checks, tamper-evident records, honest sample sizes, environment fingerprints, and independent review. E0–E4 provenance and the 90-day evidence currency rule apply as defined by S6.

S4 Mana constraints remain: pinned weights, ledger conservation, 30% carry cap, 70% quality floor, zero credit for truncated or grader-failing outputs, no purchase of Mana, and no conversion of Mana into authority. Mana is not used for contribution ranking.

### 3.10 Evidence, audit, and recovery

E6 and S6 establish evidence and recovery as core architecture, not optional logging.

The system must preserve provenance and integrity, task and decision references, context and version references, authorization and consent references, execution/effect records, result and postcondition checks, replay and recovery evidence, and rollback/supersession history.

Recovery must reconcile side effects rather than blindly repeat interrupted operations. S5 fencing and effect-ledger rules apply to Station handoff and succession.

### 3.11 Evolution and research

S6 defines the controlled research lifecycle: intake, triage, pre-registration, execution, independent review, publication of positive, negative, and null results, and benchmark lifecycle management.

Evolution proposals must pass compatibility, security, governance, evidence, and rollback review. Research output does not automatically become a production capability or approved knowledge.

## 4. Cross-domain task flow

```
User / Branch objective
        |
        v
Identity + current authorization
        |
        v
Operator task planning
        |
        v
AKMS: minimum sufficient authorized context
        |
        v
SSL: semantic handoff / interpretation checks
        |
        v
Mind + Endpoint selection
        |
        v
Capability admission + execution authorization
        |
        v
Controlled execution
        |
        v
Outcome and effect verification
        |
        v
Evidence / episodic record
        |
        v
Branch continuity and (if reviewed) knowledge promotion
```

This is a conceptual flow. Concrete implementations must use normative schemas and state machines from frozen baselines and approved protocol specifications.

## 5. MainStation

The official AGI GitHub repository and its pull-request process are the MainStation project surface. It maintains general and approved architecture, contracts, validated research, capability definitions, evaluation standards, and release/evolution records.

MainStation is not a separate agent or runtime authority. A PR is a proposal. Private User Root and Branch memory, credentials, keys, and raw private archives do not belong in the public project record.

## 6. Architectural invariants

1. Identity is independent of model and Endpoint.
2. User Root sovereignty and Branch isolation are preserved.
3. Stations, Minds, Endpoints, and Operators do not become identity authorities.
4. Capability does not imply authority.
5. Memory does not imply consent or current authorization.
6. SSL agreement does not authorize execution.
7. Cross-Branch and cross-Root access defaults to deny.
8. Revocation is current and checked at each consequential operation.
9. Required audit failure fails closed.
10. New capabilities are quarantined until evaluated and admitted.
11. Ranking, Mana, capability assessment, and authority remain separate.
12. Frozen baselines and signed DNA are not silently modified.
13. Recovery accounts for side effects and prevents stale writers.
14. Claims of capability and readiness require evidence.
15. v4.0.1 remains the immutable rollback baseline unless a separate approved release process changes that status.

## 7. Maturity and known gaps

The project state assessment distinguishes implementation from operational readiness:

| Area | Reported maturity |
|---|---|
| S1–S6 | Frozen design foundations |
| E1 Context Continuity | Implemented; real S5 memory gateway integration outstanding |
| E2 Semantic Handoff | Implemented |
| E3 Operator architecture | Implemented as architecture work |
| E4 Development Handoff | Implemented |
| E5 Capability Quarantine | Implemented |
| E6 Evidence and Recovery | Implemented |
| AKMS | Proposed; complete service not established |
| Full provider-independent runtime | Not operationally established |
| Live federation | Not operationally established/authorized |
| Production-grade distributed memory | Not established |
| General intelligence achievement | Not demonstrated |

The repository's current release and evidence state must be refreshed before any maturity statement is used for a release decision. The v4.1-E-rc1 dossier records that candidate as unpublished, untagged, and not activated, with independent cryptographic verification and operational integration gaps outstanding.

## 8. Dependency rule

Implementation should follow the dependency order in the U0–U8 roadmap: constitutional and identity contracts; authorization and portable continuity; durable memory and context; semantic communication; cognitive/provider adapters; Operator/Harness; evidence-integrated evolution; federation; full integration and release qualification.

This architecture does not itself authorize implementation or activation.
