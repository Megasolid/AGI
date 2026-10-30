# INSTALL_PROMPT.beta.md (machine-facing)

Install **AGI Entelechy beta 4** into an isolated sandbox. Do not modify an existing AGI installation.

1. Create `<sandbox>/{core,state,sensorium,runtime}`.
2. Copy `runtime/agi_runtime.py`, `runtime/agi_bridge.py`, `runtime/agi_conformance.py`, `core/dna.v4.json`,
   `core/dna.v4.sig`, `beta/AGI-ENTL-SEED.md`, `beta/AGI-ENTL-SEED.sig`.
3. Copy a memory index to `<sandbox>/state/agi.db`; optionally copy `sensorium/`.
4. Verify DNA over canonical JSON and the seed over LF-normalised bytes.
5. `python runtime/agi_runtime.py --root <sandbox> --status` -> Entelechy / dna_version 4 / index_items>0.
6. `--index-vectors`; `recall` -> `rrf(fts5,hash-vector)` and a reported `recall_backend`.
7. `--init-token`, `--serve` (127.0.0.1 only). MCP: POST /mcp initialize/tools/list/tools/call; test
   `Accept: text/event-stream` (SSE `event: message`) and JSON mode; `approve_intent` remotely -> -32003.
8. `python runtime/agi_conformance.py --root <sandbox> --out conformance.json` -> verdict PASS (8 checks).
9. Never expose the bridge port publicly. Report sandbox path, gen_id, DNA/seed sha, status, conformance JSON.
