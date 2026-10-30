# AGI latest stable DNA (one-call file)

**Stable version:** `v4.0.1`  ·  **Generation:** Entelechy (gen4)  ·  **DNA version:** 4
**gen_id:** `ENTL-GGAACTATAAGT-TTGCAGTAAGTC-CCCAAAACATAT-TAGATAGAGAAT`
**DNA canonical sha256:** `39dd5592f5f0d2573bc7529e206d679767d70c49d4bdfc0ef7aa5236117954c8`
**Signature file (raw):** <https://raw.githubusercontent.com/Megasolid/AGI/main/core/dna.v4.sig>
**Release:** <https://github.com/Megasolid/AGI/releases/tag/v4.0.1>
**Lineage:** gen3.5 `dna-GCACGAGGCTGT` (archived ancestor) -> gen4 `v4.0.1` (current stable)

This single file is the machine entrypoint for the latest stable DNA. An LLM or agent that reads it in one call
has: the full signed DNA v4 contract, the identity, the verification rules, and the install path. Do not
improvise alternate DNA; if this file and `core/dna.v4.json` disagree, stop and report.

## Install (one line)

- Windows: `irm https://github.com/Megasolid/AGI/releases/download/v4.0.1/install.ps1 | iex`
- macOS/Linux: `curl -fsSL https://github.com/Megasolid/AGI/releases/download/v4.0.1/install.sh | bash`
- Or download `agi-runtime-v4.0.1.zip` and `SHA256SUMS.txt` from <https://github.com/Megasolid/AGI/releases/tag/v4.0.1> and verify the SHA-256 first.

## Verify the DNA

1. Read `core/dna.v4.json` (or the JSON block below) and the signature `core/dna.v4.sig`.
2. Recompute the canonical digest: `sha256(json.dumps({k:v for k,v in dna.items() if k != "digest_sha256"}, sort_keys=True, separators=(",", ":")))` must equal `39dd5592f5f0d2573bc7529e206d679767d70c49d4bdfc0ef7aa5236117954c8`.
3. Verify the signature under the published key (ML-DSA; see the runtime docs) — never accept a DNA whose
   digest/signature does not verify.
4. Confirm `generation.gen_id` equals `ENTL-GGAACTATAAGT-TTGCAGTAAGTC-CCCAAAACATAT-TAGATAGAGAAT`.

## Full signed DNA v4

```json
{
 "schema": "agi-dna/4",
 "generation": {
  "name": "Entelechy",
  "major": 4,
  "dna_version": 4,
  "status": "beta-candidate",
  "gen_id": "ENTL-GGAACTATAAGT-TTGCAGTAAGTC-CCCAAAACATAT-TAGATAGAGAAT"
 },
 "lineage": {
  "parent_dna_tag": "dna-GCACGAGGCTGT",
  "parent_core": "3.2",
  "parent_dna_version": 3,
  "rule": "preserve I1-I9; dna changes only by dna_version bump + Master sign-off"
 },
 "invariants": [
  "I1 enforcement in gates, never prose",
  "I2 machine facts only in state/",
  "I3 verified-only execution",
  "I4 idempotent boot from disk",
  "I5 hash manifests on portable artifacts",
  "I6 structured IO envelopes",
  "I7 model portability via adapters",
  "I8 stop on first failure; thresholds need Master",
  "I9 durable decision projection"
 ],
 "reactive_dna": {
  "schema": "agi-reactive-dna/1",
  "evaluation": "fitness = survival * task_success / attempt - cost - conflict_penalty - complexity_tax",
  "selection": "conflict-aware; one reaction per (trigger, env); env tags over env=any; held-out validation",
  "rules": [
   {
    "trigger": "boot",
    "env": "any",
    "reaction": "load_db"
   },
   {
    "trigger": "loss",
    "env": "any",
    "reaction": "restore_snapshot"
   },
   {
    "trigger": "corrupt",
    "env": "any",
    "reaction": "rollback"
   },
   {
    "trigger": "miss",
    "env": "any",
    "reaction": "rebuild_index"
   },
   {
    "trigger": "fetch_fail",
    "env": "noisy-web",
    "reaction": "retry_fallback"
   },
   {
    "trigger": "untrusted",
    "env": "noisy-web",
    "reaction": "sandbox"
   },
   {
    "trigger": "overflow",
    "env": "long-session",
    "reaction": "compact"
   },
   {
    "trigger": "drift",
    "env": "long-session",
    "reaction": "reanchor"
   },
   {
    "trigger": "intent",
    "env": "any",
    "reaction": "queue_and_notify"
   },
   {
    "trigger": "approval",
    "env": "any",
    "reaction": "execute_once"
   },
   {
    "trigger": "recall_miss",
    "env": "any",
    "reaction": "index_expand"
   },
   {
    "trigger": "env_change",
    "env": "any",
    "reaction": "retag_rules"
   },
   {
    "trigger": "percept",
    "env": "any",
    "reaction": "render_salience_digest"
   },
   {
    "trigger": "ui_env_change",
    "env": "any",
    "reaction": "retag_visual_genes"
   }
  ]
 },
 "memory": {
  "engine": "sqlite3",
  "db": "state/agi.db",
  "journal": "WAL",
  "tables": [
   "items",
   "items_fts (fts5/porter)",
   "items_vec (optional)",
   "intents",
   "decisions",
   "snapshots"
  ],
  "fusion": "RRF when vector leg is enabled; FTS5 always available"
 },
 "runtime": {
  "module": "runtime/agi_runtime.py",
  "verbs": [
   "status",
   "recall",
   "remember",
   "boot",
   "propose_intent",
   "poll_intent",
   "approve_intent",
   "fetch",
   "snapshot",
   "evolve_propose"
  ],
  "rule": "stateless typed adapter; writes are intents; execute-once after Master approval"
 },
 "bridge": {
  "inbound_ports": 0,
  "tunnel": [
   "cloudflared",
   "tailscale-funnel"
  ],
  "auth": "OAuth 2.1 PKCE, scoped short-lived tokens",
  "reads": "scoped/redacted",
  "writes": "intent queue + Master approval",
  "beta_1": "stdio only; fetch/exec denied"
 },
 "visual_genome": {
  "system": "AGI Sensorium",
  "contract": "agi-percept-graph/1",
  "engine": "WebGL2",
  "paradigm": "intent-field",
  "winning_genes": {
   "layout": "radial-field",
   "motion": "pulse",
   "palette": "ember",
   "density": "low",
   "a11y": "reduced-motion",
   "webgl_budget": "balanced"
  },
  "reference_genes": [
   "causal_filament: cyan-gold animated trails linking intent to predicted consequences",
   "stale_shimmer:pulse_node_opacity_by_seconds_since_last_state_change"
  ]
 },
 "budget": {
  "runtime_lines_max": 600,
  "dna_lines_max": 200,
  "docs_max_files": 4,
  "boot_context_max_kb": 8
 },
 "created": "2026-10-29T20:29:07+00:00",
 "digest_sha256": "39dd5592f5f0d2573bc7529e206d679767d70c49d4bdfc0ef7aa5236117954c8"
}
```
