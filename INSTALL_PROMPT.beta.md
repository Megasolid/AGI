# INSTALL_PROMPT.beta.md (machine-facing)

Install **AGI Entelechy beta 7** into an isolated sandbox. Do not modify an existing AGI installation.

1. `<sandbox>/{core,state,sensorium,runtime}`.
2. Copy runtime/agi_runtime.py, agi_bridge.py, agi_seats.py, agi_master.py, agi_migrate.py, agi_tunnel.py,
   agi_conformance.py, core/dna.v4.json(+.sig), beta/AGI-ENTL-SEED.md(+.sig).
3. Copy a memory index to <sandbox>/state/agi.db (or migrate a clone; never the live tree).
4. Verify DNA canonical digest and seed signature (LF-normalised bytes).
5. `--status` -> Entelechy/dna_version 4/index_items>0; `--index-vectors`; recall -> rrf(fts5,hash-vector).
6. Seats: `agi_seats.py --enroll NAME` (ed25519 default when cryptography is present; device key shown once, sandbox
   stores only the public key). Challenge/login; replay and wrong signatures must fail.
7. Master: `agi_master.py --ceremony` (creates state/master.key 0600 + master_pub.json), then `--sign FILE` /
   `--verify FILE SIG`; tamper must fail. Keep master.key offline and out of git.
8. Bridge loopback + token; MCP tools/list includes 12 tools (incl. seat_challenge/seat_login); remote approve_intent
   -> -32003; GET /mcp replays events; ?window=0 unbounded.
9. Migration: dry-run, then `--snapshot-db` before `--apply`; `--restore-db` proves rollback (sha matches).
10. `agi_conformance.py --root <sandbox>` -> PASS 18/18 before experiments. Never expose the bridge.
