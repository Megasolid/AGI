# INSTALL_PROMPT.beta.md (machine-facing)

Install **AGI Entelechy beta 10** into an isolated sandbox. Do not modify an existing AGI installation.

1. `<sandbox>/{core,state,sensorium,runtime}`.
2. Copy runtime/agi_{runtime,bridge,seats,master,passport,policy,release,stability,migrate,tunnel,conformance}.py,
   CHANGELOG.beta.md, core/dna.v4.json(+.sig), beta/AGI-ENTL-SEED.md(+.sig).
3. Copy a memory index to <sandbox>/state/agi.db (or migrate a clone; never the live tree).
4. Verify DNA canonical digest and seed signature (LF-normalised bytes).
5. `--status` / `--index-vectors` / recall -> rrf(fts5,hash-vector).
6. Master: `agi_master.py --ceremony` (Ed25519 + ML-DSA-65 when available); sign/verify; tamper fails.
7. Seats + passports: enroll (local or MCP), issue passport (local or policy-enabled MCP); audit trail grows.
8. Release artifacts: `agi_release.py --sign` then `--verify`; tamper must fail.
9. Bridge loopback + token; MCP 17 tools; remote approval refused; event stream Last-Event-ID; ?window=0 unbounded.
10. Conformance `agi_conformance.py --root <sandbox>` -> PASS 25/25; stability `agi_stability.py --runs 2` -> STABLE.
11. Never expose the bridge; tunnel is plan-only and needs explicit approval.
