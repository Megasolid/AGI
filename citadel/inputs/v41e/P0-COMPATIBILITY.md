# P0 compatibility specification — AGI v4.1-E

**Status:** P0 planning artifact. No implementation, no release artifact.
**Base:** `main` `e61eb10fc5bf8a992f93ce15a8a352d5b08329bc` (tree `d085214…`).
**Rollback:** v4.0.1 `6a0fb796…` (tree `083f0ee…`), runtime `85a92254…`.

## 1. Compatibility statement

v4.1-E is **additive**. It adds new runtime/protocol/documentation layers; it does not modify:

- signed DNA v4 (`DNA.md`, `core/dna.v4.json`, `core/dna.v4.sig`);
- frozen S1–S6 packages or their manifests;
- identity/authority carriers, S2 consent, S3 grants/revocation/audit;
- S5 lease/fencing/Station isolation;
- S6 evidence/assessment rules;
- published tags or release assets.

No new identity or authority layer is introduced. The Operator remains non-identity; Minds remain replaceable; Branches remain the continuity/evidence unit.

## 2. New additive surfaces

| Surface | Compatibility rule |
|---|---|
| E1 context manifests | new versioned artifacts; pointers remain untrusted; retrieval through existing authorized gateway |
| E2 `agi.sem` | new semantic protocol; semantic-only; COMMIT never authorizes execution; `agi.session` binds S3/S5 |
| E3 Operator contracts | new service/control contracts; no change to S1–S6; policy gate remains S3 |
| E4 handoff | new task/handoff artifacts; no authority; references only |
| E5 capability quarantine | new branch-scoped catalogue; registration never authorizes execution |
| E6 journal/evidence | new durability/evidence layer; live streams are not evidence; hash-anchored packets |

## 3. Protected artifacts

Pinned by `baseline-hashes.json` and the release-control manifest: `DNA.md`, `core/dna.v4.json`, `core/dna.v4.sig`, `repo.json`, `repo.json.sig`, `POLICY.md`; plus 16/16 frozen packages / 29 files PASS.

## 4. Dependency and version policy

- New artifacts carry explicit `schema` + version; unknown/unsupported → fail closed.
- No silent schema downgrade.
- E1–E6 contracts are versioned independently; a contract change is a new version, not an in-place edit.
- No external runtime/framework becomes a required dependency for the release; optional adapters degrade explicitly.

## 5. Acceptance gates

Protected byte-identity; v4.0.1 rollback; E1 fresh-agent reconstruction; E2 two-mind semantic exchange + seeded misunderstanding + one correction; hard-constraint false accepts = 0; COMMIT alone cannot execute; cross-Branch denial without consent; prompt injection cannot reach Operator context; duplicate requests no duplicate effects; cancellation quiescence; evidence reproducible; existing regression/integrity pass; Kilo PASS; KING recommendation; Owner decision.

## 6. Non-authorization

P0 planning only. No implementation, activation, endpoint, credential, federation or frozen change.
