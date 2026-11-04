# AGI repository governance

The official AGI GitHub repository is the public project surface. Pull requests are the normal mechanism for proposing,
reviewing and recording changes. “Citadel” refers to this repository and its review/provenance workflow; it is not a
separate agent, runtime, identity authority or execution service.

## Authority

- The project owner retains final authority over protected identity, release, security and production decisions.
- A branch or pull request is a proposal until it is reviewed and accepted under the repository's rules.
- AI assistants, automated tools and contributors may research, draft, implement or review within an assigned scope.
  Their access does not grant governance, release, identity, federation or production authority.
- No assistant-generated statement, task envelope, semantic acknowledgement or test report substitutes for owner
  approval where approval is required.

## Change workflow

1. Inspect the current stable baseline and relevant source evidence before proposing a change.
2. Make bounded changes on a branch; do not write directly to `main`.
3. Keep each pull request focused and describe its scope, evidence, tests and any limitations.
4. Preserve signed release artifacts, manifests, signatures, lineage and historical evidence unless an explicit,
   reviewed retention decision authorizes a change.
5. Merge only after review and the required checks. Do not publish, tag, activate or deploy a release without the
   project owner's explicit approval.

## Stable release and safety boundaries

The current stable release is **v4.0.1**. It remains an immutable rollback baseline. The v4.1-E-rc1 material is an
unpublished candidate and must not be described as a stable release or activated.

No repository governance text grants permission for live endpoints, credentials, federation, identity mutation,
autonomous evolution or production execution. Those actions remain separately gated by the project's actual
authorizations and evidence.

## Historical records

Older task envelopes, handoffs, reports and documents may mention named agents, stations or operational arrangements.
Those references are historical records, not current governance appointments. Do not infer current authority from
their presence in the repository.
