# INSTALL_PROMPT.beta.md (machine-facing)

Install **AGI Entelechy beta 5** into an isolated sandbox. Do not modify an existing AGI installation.

1. `<sandbox>/{core,state,sensorium,runtime}`.
2. Copy runtime/agi_runtime.py, runtime/agi_bridge.py, runtime/agi_migrate.py, runtime/agi_tunnel.py,
   runtime/agi_conformance.py, core/dna.v4.json(+.sig), beta/AGI-ENTL-SEED.md(+.sig).
3. Copy a memory index to <sandbox>/state/agi.db; optional sensorium/.
4. Verify DNA canonical digest and seed signature (LF-normalised bytes).
5. Run `--status` (Entelechy, dna_version 4, index_items>0); `--index-vectors`; recall -> rrf(fts5,hash-vector).
6. Migration: `agi_migrate.py --source <live> --target <sandbox>` dry-run (source_unchanged true). --apply only
   after review; it writes only the target index.
7. Token + serve loopback; MCP JSON and SSE; GET /mcp SSE replays events after Last-Event-ID and carries live events.
   Remote approve_intent -> -32003. Tunnel: `agi_tunnel.py --check/--plan` only; never auto-start.
8. Conformance: `agi_conformance.py --root <sandbox>` -> PASS 12/12 before experiments.
9. Report sandbox path, gen_id, DNA/seed sha, conformance JSON. Never expose the bridge port publicly.
