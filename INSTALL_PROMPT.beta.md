# INSTALL_PROMPT.beta.md (machine-facing)

Install **AGI Entelechy beta 6** into an isolated sandbox. Do not modify an existing AGI installation.

1. `<sandbox>/{core,state,sensorium,runtime}`.
2. Copy runtime/agi_runtime.py, runtime/agi_bridge.py, runtime/agi_seats.py, runtime/agi_migrate.py,
   runtime/agi_tunnel.py, runtime/agi_conformance.py, core/dna.v4.json(+.sig), beta/AGI-ENTL-SEED.md(+.sig).
3. Copy a memory index to <sandbox>/state/agi.db (or migrate a clone: agi_migrate.py --source ... --target ...).
4. Verify DNA canonical digest and seed signature (LF-normalised bytes).
5. `--status` -> Entelechy, dna_version 4, index_items>0; `--index-vectors`; recall -> rrf(fts5,hash-vector).
6. Seats: `agi_seats.py --enroll NAME` (device key shown once), `--challenge`, `--login` (HMAC proof), `--status`.
   Replay/wrong proofs must fail; never print key_secret.
7. Bridge: token + loopback serve; MCP JSON/SSE; GET /mcp replays after Last-Event-ID; `?window=0` unbounded,
   default bounded 6 s; remote approve_intent -> -32003. Tunnel plan only.
8. `agi_conformance.py --root <sandbox>` -> PASS 14/14 before experiments.
9. Report sandbox path, gen_id, DNA/seed sha, seat status (hashes only), conformance JSON. Never expose the bridge.
