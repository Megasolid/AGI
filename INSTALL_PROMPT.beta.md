# INSTALL_PROMPT.beta.md (machine-facing)

Install **AGI Entelechy beta 3** into an isolated sandbox. Do not modify an existing AGI installation.

1. Create `<sandbox>/{core,state,sensorium,runtime}`.
2. Copy `runtime/agi_runtime.py`, `runtime/agi_bridge.py`, `core/dna.v4.json`, `core/dna.v4.sig`,
   `beta/AGI-ENTL-SEED.md`, `beta/AGI-ENTL-SEED.sig`.
3. Copy a memory index (`agi.db`) to `<sandbox>/state/agi.db`; optionally copy `sensorium/scene.json` +
   `scene.digest.txt`.
4. Verify: DNA over canonical JSON; seed over LF-normalised bytes.
5. `python runtime/agi_runtime.py --root <sandbox> --status` -> generation Entelechy, dna_version 4, index_items>0,
   sensorium digest present.
6. `--index-vectors` -> vectors > 0; `recall` -> fusion `rrf(fts5,hash-vector)`.
7. `--init-token` (shown once, hash stored); `--serve` binds 127.0.0.1 only.
8. MCP check: POST /mcp `initialize` (session header returned), `tools/list` (10 tools), `tools/call` status.
   `approve_intent` over MCP must be refused (-32003); approval stays local.
9. Never expose the bridge port publicly. Report sandbox path, gen_id, DNA/seed sha, status JSON, MCP checks.
