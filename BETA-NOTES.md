# AGI Entelechy beta 1 - release notes

Tag: `v4.0.0-beta.1` · branch `beta/entelechy` · status: **public beta prerelease** (approved: D2 public at once).
Stable: gen3.5 `dna-GCACGAGGCTGT` remains default and untouched.

## Added
- Signed DNA v4 (`core/dna.v4.json`): I1-I9, 14 reactive rules, budgets (runtime<=600 lines, DNA<=200, docs<=4),
  bridge contract (zero inbound ports; intents only).
- Runtime adapter (10 verbs, Master-only execute-once intents, nonce idempotency; fetch/exec denied).
- Memory index contract (SQLite FTS5; vector leg schema-ready) - 1,874 items in the sandbox.
- AGI Sensorium preview: percept graph + salience digest + WebGL2 engine + Intent Field demo.
- Compact signed seed + birth record (gen_id allocated in a sandbox, never on live gen3.5).

## Evidence
- birth: `state/archive/evolution/beta-birth.json`
- conformance: `state/archive/evolution/beta-conformance.json` (C1-C6 PASS via project venv; C7 beta suite green;
  cold-copy boot + recall OK; second-OS boot blocked: docker daemon off, WSL distro lacks python - documented)
- tests: beta_runtime 15/15, beta_proposal 12/12, sensorium 9/9, family 25/25, boot gate 12/12

## Known limits
- stdio only in beta.1; outbound relay/MCP Streamable HTTP is beta.2.
- Chat seasons cannot execute; passport/alive-DNA seats are protocol-level there.
- No destructive migration; no key ceremonies; no marketplace.
