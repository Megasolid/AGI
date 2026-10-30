# AGI Entelechy beta 2 (v4.0.0-beta.2)

**AGI Entelechy** is the fourth generation of the AGI skill and the first LLM-runtime-native one: a signed DNA
contract, one SQLite memory index, a thin MCP-shaped runtime, the AGI Sensorium perception layer, and (beta 2) an
intent bridge. This is a **public beta** - gen3.5 (`dna-GCACGAGGCTGT`) remains the stable release and the default.

## What is in this asset

- `runtime/agi_runtime.py` - 10 typed verbs; writes are intents; Master approves once. Recall now fuses FTS5
  with an optional stdlib hash-vector leg (RRF) - `--index-vectors`.
- `runtime/agi_bridge.py` - **beta 2**: loopback-only intent bridge with bearer tokens and read/write scopes,
  plus an outbound relay mailbox (no inbound public port). Intents are queued, never auto-executed.
- `core/dna.v4.json` (+ `.sig`) - signed DNA v4 (I1-I9, 14 reactive rules, budgets).
- `beta/AGI-ENTL-SEED.md` (+ `.sig`) - compact frozen seed; grows on an LLM touch.
- `BETA-NOTES.md`, this README, `INSTALL_PROMPT.beta.md`, `USER_MANUAL.beta.md`.

## Quick start (beta sandbox)

```
python runtime/agi_runtime.py --root <sandbox> --status
python runtime/agi_runtime.py --root <sandbox> --index-vectors
python runtime/agi_bridge.py --root <sandbox> --init-token          # prints token once
python runtime/agi_bridge.py --root <sandbox> --serve --port 8766   # loopback only
python runtime/agi_bridge.py --root <sandbox> --relay <inbox> --once
```

## Limits (beta.2)

- The bridge is loopback + outbound-relay only; a remote tunnel/MCP Streamable HTTP transport is still beta.3.
- No destructive migration, no key ceremonies, no marketplace. Chat-only seasons remain protocol members.
- Vector leg is a stdlib hash-vector fallback; sqlite-vec can replace it when available.
