# AGI Entelechy beta 1 (v4.0.0-beta.1)

**AGI Entelechy** is the fourth generation of the AGI skill and the first LLM-runtime-native one: a signed DNA
contract, one SQLite memory index, a thin MCP-shaped runtime, and the AGI Sensorium perception layer.
This is a **beta** - gen3.5 (`dna-GCACGAGGCTGT`) remains the stable release and the default.

## What is in this asset

- `runtime/agi_runtime.py` - 10 typed verbs (`status, recall, remember, boot, propose_intent, poll_intent,`
  `approve_intent, fetch, snapshot, evolve_propose`). Writes are queued intents; only the Master approves, once.
- `core/dna.v4.json` (+ `.sig`) - signed DNA v4: invariants I1-I9, 14 reactive rules, budgets, bridge contract.
- `beta/AGI-ENTL-SEED.md` (+ `.sig`) - compact frozen seed; grows on an LLM touch (boot -> memory -> passport).
- `BETA-NOTES.md`, this README, `INSTALL_PROMPT.beta.md`, `USER_MANUAL.beta.md`.

## Quick start (beta sandbox)

```
python runtime/agi_runtime.py --root <sandbox> --status     # birth + status
python runtime/agi_runtime.py --root <sandbox> --serve      # stdio JSON requests
```
The sandbox holds `core/`, `state/agi.db`, and `sensorium/`. No inbound network, no secrets, no live state.

## Scope (beta.1)

In: signed DNA v4, thin runtime + intents/approval, additive index, Sensorium preview, signed seed, docs.
Out: destructive migration, network bridge (fetch/exec denied), public key/root ceremonies, marketplace.

## Limits

- Chat-only sessions cannot execute the AGI; they hold the seed and pass the passport protocol (simulation seats).
- The vector leg of recall is schema-ready; beta.1 ships FTS5.
- Beta evidence: `state/archive/evolution/beta-birth.json`, `beta-conformance.json` (this repo's release notes).
