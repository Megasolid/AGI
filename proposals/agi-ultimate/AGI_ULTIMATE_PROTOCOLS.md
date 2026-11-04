# AGI Ultimate — Protocol Architecture

**Status:** U0 protocol proposal; individual protocols require separate normative specifications  
**Authority:** Existing signed DNA and frozen S1–S6 contracts remain authoritative

## 1. Purpose

This document maps the protocol contracts required by AGI Ultimate. It does not replace frozen S1–S6 schemas or claim that every proposed protocol is implemented.

A protocol is complete only when its schema, state machine, trust assumptions, failure behavior, security boundary, compatibility policy, negative tests, and evidence requirements are defined.

## 2. Protocol layers

| Layer | Responsibility | Governing basis |
|---|---|---|
| Identity and enrollment | Identity references, bootstrap, enrollment, recovery | S1/S2 |
| Authorization | Scoped decisions, consent, revocation, Branch boundaries | S3-AUTH |
| Federation | Transfer, projection, stewardship, continuity | S3-FED |
| Context continuity | Context manifests, Branch references, version and digest | E1 |
| Semantic communication | Meaning, context resolution, semantic receipt, challenge/correction | SSL / E2 |
| Operator control | Task/run/item lifecycle, approval, cancellation, events | E3 |
| Development handoff | Transfer of development context and state | E4 |
| Capability admission | Capability declaration, quarantine, evaluation, admission | E5 |
| Evidence and recovery | Provenance, effect records, replay, recovery, rollback | E6/S5/S6 |

These layers may share transport and cryptographic primitives, but they must not collapse their authority boundaries.

## 3. Identity and bootstrap protocol

S2's existing contracts cover bootstrap manifests, enrollment requests and grants, Station enrollment, identity enrollment, revocation records, and consent records.

Implementations must preserve canonicalization, signature, replay, compromised-device, version-negotiation, and migration requirements defined by S2.

The bootstrap seed is a bounded pointer-bearing artifact, not a container for private memory, keys, credentials, or executable instructions. No new enrollment schema is approved by this document.

## 4. Authorization protocol

S3-AUTH remains the normative authorization baseline.

Every consequential operation must be evaluated against current identity, scope, consent, grant lifetime, Branch boundary, and revocation state. Stale or unavailable authorization state must not yield an allow decision. Audit failure must fail closed.

No communication protocol, Operator control API, memory retrieval API, or capability adapter may bypass this boundary.

## 5. Semantic Signal Layer (SSL)

### 5.1 Purpose

SSL enables independent Minds and services to exchange structured messages while preserving intended meaning and relevant context.

The central research question is whether independently operating LLMs can maintain verifiable shared understanding of a task without sharing their complete conversational context.

### 5.2 Responsibility separation

| Component | Owns |
|---|---|
| DNA contract | Trust and authorization |
| SSL | Communication and semantic agreement |
| Memory index / AKMS | Context storage and retrieval |
| Runtime adapter | Model invocation and execution |
| Evidence subsystem | Audit and verification records |

SSL may verify that a request is well-formed and semantically understood. It cannot grant permission to execute it.

### 5.3 Message contract

The proposed primary format is structured JSON with a mandatory semantic contract. Context is represented by reference, version, and digest rather than duplicated conversation history.

The protocol should include protocol/schema version, message/session identifiers, sender and receiver identity references, intent and expected outcome, hard constraints and preconditions, context references with version and digest, expiry/nonce/sequence information, relevant capability declarations, semantic receipt and verification result, and evidence references.

Exact field names and normative schema are deferred to a separately reviewed SSL specification.

### 5.4 Semantic lifecycle

```
Handshake
  -> Receive and validate envelope
  -> Authenticate sender and protect against replay
  -> Resolve authorized context references
  -> Independently interpret intent and constraints
  -> Semantic receipt
  -> Challenge/correction if ambiguous or mismatched
  -> Agreement on proposed operation
  -> Separate runtime authorization
  -> Execution by authorized runtime
  -> Result and postcondition verification
  -> Evidence record and closure
```

### 5.5 Message meanings

- `ACK`: delivery acknowledgment only.
- `SEMANTIC_RECEIPT`: interpretation acknowledgment.
- `COMMIT`: agreement on the proposed operation.
- Runtime authorization: a separate DNA/S3 decision.
- `RESULT`: reported outcome.
- `VERIFIED`: outcome meets the required verification conditions.

No message label or semantic score can substitute for authorization.

### 5.6 Verification and failure

The receiver independently interprets intent and compares expected outcome, hard constraints, and context references. Hard constraints require deterministic enforcement. LLM confidence or semantic similarity cannot override a hard-constraint mismatch.

Ambiguity or mismatch leads to challenge/correction or refusal. Malformed, unauthenticated, replayed, expired, unauthorized, or unverifiable messages fail closed.

### 5.7 Security and transport

The security design must address identity, message integrity, replay, context substitution, prompt injection, privilege escalation, protocol downgrade, denial of service, and audio spoofing.

Candidate primitives in the research include SHA-256 digests, Ed25519 signatures, nonces, sequence numbers, expiry, TLS 1.3, explicit key IDs/rotation, JSON Canonicalization Scheme (RFC 8785), and HTTP Message Signatures (RFC 9421) where applicable. These are design candidates, not claims of deployed cryptographic integration.

Transport is pluggable. Structured text/JSON is the initial baseline. Voice is an optional transport, not an authentication root. Symbolic and latent communication remain experimental. SSL should first operate in isolated simulation or shadow mode; it must not become an execution gate until independently tested.

## 6. AKMS and context protocol

AKMS is the proposed durable knowledge and memory service. E1 supplies the current context-continuity direction.

Context references must carry sufficient identity, Branch scope, classification, version, digest, expiry, and consent/revocation metadata to resolve the requested context safely.

Retrieval must authenticate the requester; enforce User Root and Branch scope; check current consent and revocation; verify reference version and digest; apply relevance and minimum-sufficient-context selection; return provenance and uncertainty; and record consequential access where required.

Knowledge promotion is a separate governed process. Retrieval does not imply promotion, and a model-generated statement is not automatically a verified knowledge item.

## 7. Operator control and execution protocol

E3 identifies the need for explicit contracts covering service model, plugin lifecycle, event/policy model, control protocol, execution primitives, approval/cancellation, event durability/replay, security boundaries, baseline traceability, provider substitution, recovery, and runtime profiles.

Each contract must define scope and owner, inputs and outputs, trust assumptions, failure behavior, security boundary, evidence, acceptance and negative tests, S1–S6 traceability, and open gaps.

Critical requirements include monotonic denial, policy-gate isolation, durable Owner decision projection, cancellation quiescence proof, event replay/idempotency, Branch-scoped journals, provider substitution disclosure, effect reconciliation, and stale-lease rejection.

The Operator control interface is not an authority API. Client approval, user consent, and S3 authorization are distinct decisions.

## 8. Capability protocol

E5 requires untrusted or newly introduced capabilities to be quarantined. A capability manifest describes what a component claims to provide; it does not prove trust or grant permission.

Admission requires defined scope, dependencies, permission requests, isolation, evaluation, negative tests, provenance, and approval. Unload and failure handling must account for active work and side effects.

## 9. Federation protocol

S3-FED remains authoritative for federation design. Its boundaries cover transport, projection, and stewardship. The protocol must preserve independent identities and require explicit approvals for projected information and continuity transfers.

Snapshots and transfer envelopes must be signed and verifiable. Destination verification, replay protection, divergence detection, branch locking where specified, rollback alerts, and decommissioning must be enforced.

Federation is not activated by this proposal.

## 10. Evidence and recovery protocol

E6 and S6 require durable evidence with provenance and verifiable linkage to decisions and outcomes.

Evidence records should link the task, Branch, identity references, context digest/version, authorization decision, component versions, execution/effect record, result, verifier, and relevant timestamps/sequence numbers.

Operational event streams are not automatically evidence. Recovery must distinguish restored state from repeated effects and must reconcile side effects before resuming.

## 11. Protocol conformance and versioning

Each protocol requires versioned schemas; canonical serialization where signatures/digests depend on representation; explicit compatibility and downgrade rules; deterministic validation; negative and adversarial tests; replay and corruption tests where applicable; independent verification; evidence artifacts; and migration and rollback plans.

A protocol change that alters a frozen S1–S6 guarantee requires a formal baseline change, not a routine minor-version update.

## 12. Non-authorization

This document does not authorize live endpoints, network exposure, credential use, federation, execution, identity mutation, memory sharing, or changes to signed DNA and frozen baselines.
