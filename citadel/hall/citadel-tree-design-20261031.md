# Citadel Tree Design (proposal, non-destructive)

## Goals
- Keep runtime/release artifacts stable and immutable.
- Separate governance, evidence, prototypes and book documentation from release assets.
- One-hop management: KING -> DSH -> repository; Kilo independent review through signed task files.
- No secrets, private memory, credentials or production state in Citadel.

## Proposed tree
```
CITADEL.md                 KING/Council/Hall/Divisions + release policy
citadel/
  governance/              charter, decision ledger, policies
  hall/                    decisions history, inventory, audits, roadmap
  divisions/               division charters and status
  tasks/                   signed task envelopes
  reports/                 PR-only station reports
  inputs/                  pinned inputs for tasks
  prototypes/              isolated prototypes (never release assets)
  docs/                    book program: entry/handbook/chronicle outlines
docs/                      public documentation (current)
releases/                  immutable release assets and manifests
runtime/                   public runtime source (release-gated)
beta/                      public seed/install artifacts
```
## Migration rules
1. Only additive moves; no deletion of release assets.
2. Each move updates references, public-sync checks and task input hashes.
3. New tree changes are proposed to KING, submitted to Kilo for independent review where they affect release paths.
4. v4.0.1 remains immutable rollback baseline; v5 additive.
5. No secrets/private state in Citadel; no destructive rewrite without migration path.
