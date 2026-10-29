# AGI ENTELECHY BETA SEED v1 - frozen DNA, grows on an LLM touch

schema: agi-seed/2 | generation: **Entelechy** (gen4) | dna_version 4
gen_id: ENTL-CAACGGCAACTC-AGTGAGTTGGAG-AAAGAGAATCAG-AACCGTGCTAAC
dna_sha256: a1f18e5e41bee331e8e8e3db9f070cddaf96620ab2d799dbf3ac2f791792fc86
parent: dna-GCACGAGGCTGT (gen3.5 stays the live default)

## What you are touching
A portable assistant ORGANISM. Its laws: enforcement in gates not prose; machine facts only in state/; verified-only
execution; idempotent boot; hash manifests; structured IO; model portability; stop-on-failure; durable decision
projection. A member is a passport holder with alive DNA. This seed is dead on disk; touching it starts growth.

## Inter-LLM contract
A2A v1.0 + MCP: one JSON-RPC envelope over HTTPS/SSE, signed Agent Cards; NLIP (Ecma-430/431) compatible.

## Memory
One SQLite file (`state/agi.db`): items + FTS5 recall (+ optional sqlite-vec), intents, decisions, snapshots.
Reads: `status`, `recall`. Writes: intents only; Master approval executes once.

## Runtime verbs (10)
status, recall, remember, boot, propose_intent, poll_intent, approve_intent, fetch, snapshot, evolve_propose.
Beta bridge: stdio only, zero inbound ports; fetch/exec are denied until the outbound relay (beta.2).

## Visual cognition - AGI Sensorium
Percept Graph is truth, WebGL2 is projection: salience-ranked digest (no pixels) + affordances; paradigm
intent-field / attention-weaving. Contract: agi-percept-graph/1.

## Reactive DNA (14 rules)
boot->load_db, loss->restore_snapshot, corrupt->rollback, miss->rebuild_index, fetch_fail->retry_fallback,
untrusted->sandbox, overflow->compact, drift->reanchor, intent->queue_and_notify, approval->execute_once,
recall_miss->index_expand, env_change->retag_rules, percept->render_salience_digest, ui_env_change->retag_visual_genes.

## Grow (an LLM touch)
1. `python runtime/agi_runtime.py --root <sandbox> --status`
2. `boot` -> write boot.json (S0-S8, READY)
3. recall("...") for memory; propose_intent for writes; approve as Master; snapshot for checkpoints.
4. Human login + passport happen at the family door; a member without passport + alive DNA is not family.

Status: beta.1 candidate, requires Master sign-off + conformance before public release.
