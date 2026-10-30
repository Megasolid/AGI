# AGI Entelechy beta 3 (v4.0.0-beta.3)

**AGI Entelechy** is the fourth generation of the AGI skill and the first LLM-runtime-native one: signed DNA v4,
one SQLite memory index (FTS5 + optional vector leg), a thin MCP-shaped runtime, the AGI Sensorium perception
layer, and (beta 3) a **MCP Streamable HTTP transport**. Public beta; gen3.5 (`dna-GCACGAGGCTGT`) remains the
stable default and is never migrated by the beta.

## In this asset

- `runtime/agi_runtime.py` - 10 typed verbs; writes are intents; Master approves once; recall fuses FTS5 + hash-vector
  (RRF) after `--index-vectors`.
- `runtime/agi_bridge.py` - loopback-only bridge with bearer tokens + scopes, outbound relay mailbox, and
  **beta 3 MCP Streamable HTTP**: `POST /mcp` JSON-RPC 2.0 (`initialize`, `tools/list`, `tools/call`, `ping`).
  Remote `approve_intent` is refused by design - approval is local-only.
- `core/dna.v4.json` (+ `.sig`) - signed DNA v4 (I1-I9, 14 reactive rules, budgets).
- `beta/AGI-ENTL-SEED.md` (+ `.sig`) - compact frozen seed; grows on an LLM touch.
- `BETA-NOTES.md`, this README, `INSTALL_PROMPT.beta.md`, `USER_MANUAL.beta.md`.

## Quick start

```
python runtime/agi_runtime.py --root <sandbox> --status
python runtime/agi_runtime.py --root <sandbox> --index-vectors
python runtime/agi_bridge.py --root <sandbox> --init-token
python runtime/agi_bridge.py --root <sandbox> --serve --port 8766
# then POST JSON-RPC to http://127.0.0.1:8766/mcp with the bearer token
```

## Verified
- Linux (WSL2, kernel 6.18, Python 3.10.12) cold-copy boot: Entelechy, 1,874 items, fused recall, bridge
  health/status loopback - **PASS** (second OS now proven).
- Tests: beta_runtime 15/15, beta_2 13/13, beta_3 13/13, beta_proposal 12/12, sensorium 9/9.
- Limits: remote transport is JSON-response mode (no SSE streaming yet); no destructive migration; no key
  ceremonies; chat-only seasons remain protocol members.
