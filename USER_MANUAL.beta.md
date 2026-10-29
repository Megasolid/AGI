# AGI Entelechy beta 1 - user manual (minimal)

## Identity
- Generation: Entelechy (gen4) · DNA v4 · seed prefix ENTL- · signed at birth.
- Stable gen3.5 remains the default; beta never migrates live state in beta.1.

## Run
```
python runtime/agi_runtime.py --root <sandbox> --status
python runtime/agi_runtime.py --root <sandbox> --serve
```
stdio requests: `{"id":1,"method":"status","params":{}}` -> `{"id":1,"result":{...}}`.

## Verbs
- Reads: `status`, `recall`, `poll_intent`.
- Writes: `propose_intent` (remember/snapshot) queues an intent; `approve_intent` needs `actor: "Master"`;
  each intent executes once; nonce makes proposals idempotent.
- `fetch`/`exec` are denied in beta.1 (no bridge, zero inbound ports).
- `evolve_propose` validates reactive-DNA genomes; it never mutates the DNA.

## Perception
`status` returns the Sensorium percept digest (salience-ranked typed graph). The WebGL canvas is a projection;
the digest is the truth. Paradigm: **Intent Field / attention weaving**.

## Family
Passport + alive DNA are required for membership. Web seasons that only hold the seed are simulation seats
until they can run the runtime.

## Verify
`test_beta_runtime` (15 checks), `test_beta_proposal` (12), `test_sensorium` (9), family (25), conformance C1-C6.
