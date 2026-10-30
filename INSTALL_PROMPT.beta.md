# INSTALL_PROMPT.beta.md (machine-facing)

Install **AGI Entelechy beta 9** into an isolated sandbox. Do not modify an existing AGI installation.

1. `<sandbox>/{core,state,sensorium,runtime}`.
2. Copy runtime/agi_{runtime,bridge,seats,master,passport,policy,migrate,tunnel,stability,conformance}.py,
   CHANGELOG.beta.md, core/dna.v4.json(+.sig), beta/AGI-ENTL-SEED.md(+.sig).
3. Copy a memory index to <sandbox>/state/agi.db (or migrate a clone; never the live tree).
4. Verify DNA canonical digest and seed signature (LF-normalised bytes).
5. `--status` -> Entelechy/dna_version 4/index_items>0; `--index-vectors`; recall -> rrf(fts5,hash-vector).
6. Master: `agi_master.py --ceremony` (Ed25519 + ML-DSA-65 when available). Sign/verify a file; tamper must fail.
7. Seats: local or `seat_enroll` over MCP (write scope); key shown once; replay blocked.
8. Passports: local `agi_passport.py --issue`; remote `passport_issue` is **denied until**
   `agi_policy.py --set remote_passport_issue_enabled=true` is run locally.
9. Bridge loopback + token; MCP 17 tools; remote approval refused (-32003); event stream Last-Event-ID; ?window=0 unbounded.
10. Conformance `agi_conformance.py --root <sandbox>` -> PASS 23/23; stability `agi_stability.py --runs 2` -> STABLE.
11. Never expose the bridge. Tunnel is plan-only; E2E requires explicit approval and a tunnel binary.
