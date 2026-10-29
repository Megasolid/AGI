# INSTALL_PROMPT.beta.md (machine-facing)

You are installing **AGI Entelechy beta 1** into an isolated beta sandbox. Do not modify any existing AGI
installation or stable state.

1. Create `<sandbox>/` with `core/`, `state/`, `sensorium/`, `runtime/`.
2. Copy from this asset: `runtime/agi_runtime.py`, `core/dna.v4.json`, `core/dna.v4.sig`,
   `beta/AGI-ENTL-SEED.md`, `beta/AGI-ENTL-SEED.sig`.
3. Copy an AGI memory index (`agi.db`, schema items/items_fts) into `<sandbox>/state/agi.db`; optionally copy
   `sensorium/scene.json` + `scene.digest.txt`.
4. Verify signatures before boot: DNA over canonical JSON, seed over its exact file bytes.
5. Run `python runtime/agi_runtime.py --root <sandbox> --status`. It must report `generation=Entelechy`,
   `dna_version=4`, `index_items>0`, and a sensorium digest.
6. Run `--serve` and issue `{"method":"recall","params":{"query":"..."}}`; reads must work. Test a write:
   `propose_intent` -> `approve_intent` with actor `Master`; a second approval must fail. `fetch` must be denied.
7. Never bind a network port in beta.1. Report: sandbox path, gen_id, dna sha, seed sha, status output.
