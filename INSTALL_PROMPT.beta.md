# INSTALL_PROMPT.beta.md (machine-facing)

Install **AGI Entelechy beta 2** into an isolated sandbox. Do not modify any existing AGI installation.

1. Create `<sandbox>/` with `core/`, `state/`, `sensorium/`, `runtime/`.
2. Copy: `runtime/agi_runtime.py`, `runtime/agi_bridge.py`, `core/dna.v4.json`, `core/dna.v4.sig`,
   `beta/AGI-ENTL-SEED.md`, `beta/AGI-ENTL-SEED.sig`.
3. Copy a memory index (`agi.db`: items/items_fts) into `<sandbox>/state/agi.db`; optionally copy
   `sensorium/scene.json` + `scene.digest.txt`.
4. Verify signatures: DNA over canonical JSON, seed over its exact bytes.
5. `python runtime/agi_runtime.py --root <sandbox> --status` must report Entelechy / dna_version 4 / index items.
6. `python runtime/agi_runtime.py --root <sandbox> --index-vectors` builds the vector leg; recall must then report
   `fusion=rrf(fts5,hash-vector)`.
7. Bridge: `--init-token` (token shown once, only hash stored); `--serve` binds 127.0.0.1 only; `--relay <dir>`
   handles outbound mailbox requests. Health needs no auth; status needs read scope; POST /intent needs write scope.
8. Intents must stay pending until a local Master approves them; the bridge itself never executes an intent.
9. Never expose the bridge port publicly in beta.2. Report sandbox path, gen_id, dna/seed sha, status JSON.
