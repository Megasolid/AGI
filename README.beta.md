# AGI Entelechy beta 4 (v4.0.0-beta.4)

**AGI Entelechy** is the fourth generation of the AGI skill: signed DNA v4, one SQLite memory index (FTS5 +
vector leg), a thin MCP-shaped runtime, the AGI Sensorium perception layer, an intent bridge, and (beta 4)
**MCP SSE streaming** plus the **beta conformance matrix**. Public beta; stable gen3.5 (`dna-GCACGAGGCTGT`)
remains the default and is never migrated by the beta.

## In this asset

- `runtime/agi_runtime.py` - 10 typed verbs; intents + Master approval; FTS5 + hash-vector RRF recall
  (`--index-vectors`, backend reported as `sqlite-vec` when the extension is present, else `hash-vector`).
- `runtime/agi_bridge.py` - loopback bridge: bearer tokens + scopes, outbound relay, MCP Streamable HTTP with
  **JSON and SSE modes**; remote `approve_intent` refused by design.
- `runtime/agi_conformance.py` - beta conformance matrix **C-beta1..C-beta8** (identity, integrity, DNA contract,
  runtime, recall, intents, Sensorium, bridge/approval locality/scopes/loopback, budgets).
- `core/dna.v4.json` (+ `.sig`), `beta/AGI-ENTL-SEED.md` (+ `.sig`), docs.

## Verify

```
python runtime/agi_conformance.py --root <sandbox> --out conformance.json
python runtime/agi_bridge.py --root <sandbox> --serve --port 8766
# POST /mcp with Accept: text/event-stream -> SSE; without -> JSON
```

## Verified
Windows (project venv) and Linux WSL2 kernel 6.18 / Python 3.10 cold boots PASS. Suites: runtime 15/15,
beta_2 13/13, beta_3 13/13, beta_4 10/10, proposal 12/12, sensorium 9/9; conformance matrix PASS.

## Limits
JSON/SSE MCP only (no long-lived server push beyond keepalive); no destructive migration; no key ceremonies;
no marketplace; chat-only seasons remain protocol members; no license chosen (research artifact).
