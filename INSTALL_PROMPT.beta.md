# INSTALL_PROMPT.beta.md (machine-facing)

Install **AGI Entelechy beta 8** into an isolated sandbox. Do not modify an existing AGI installation.

1. `<sandbox>/{core,state,sensorium,runtime}`.
2. Copy runtime/agi_runtime.py, agi_bridge.py, agi_seats.py, agi_master.py, agi_passport.py, agi_migrate.py,
   agi_tunnel.py, agi_conformance.py, CHANGELOG.beta.md, core/dna.v4.json(+.sig), beta/AGI-ENTL-SEED.md(+.sig).
3. Copy a memory index to <sandbox>/state/agi.db (or migrate a clone; never the live tree).
4. Verify DNA canonical digest and seed signature (LF-normalised bytes).
5. `--status` -> Entelechy/dna_version 4/index_items>0; `--index-vectors`; recall -> rrf(fts5,hash-vector).
6. Master: `agi_master.py --ceremony` (state/master.key 0600 + master_pub.json); sign/verify files.
7. Seats: local or `seat_enroll` over MCP (write scope) - key shown once; ed25519 default; replay blocked.
8. Passports: `agi_passport.py --issue MEMBER` (requires Master + seat), verify; tamper must fail.
9. Bridge loopback + token; MCP tools/list = 16 tools; remote approval refused (-32003); GET /mcp event replay;
   ?window=0 unbounded. Tunnel plan only; no ingress auto-opened.
10. `agi_conformance.py --root <sandbox>` -> PASS 20/20 before experiments. Never expose the bridge.
