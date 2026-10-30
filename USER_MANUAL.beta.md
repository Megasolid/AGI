# AGI Entelechy beta 2 - user manual (minimal)

## Identity
Generation Entelechy (gen4) - DNA v4 - seed prefix ENTL- - signed at birth. Stable gen3.5 remains the default;
beta never migrates live state.

## Runtime
```
python runtime/agi_runtime.py --root <sandbox> --status
python runtime/agi_runtime.py --root <sandbox> --index-vectors
python runtime/agi_runtime.py --root <sandbox> --serve
```
Verbs: status, recall, remember, boot, propose_intent, poll_intent, approve_intent, fetch, snapshot, evolve_propose.
Reads are direct; writes are intents; `approve_intent actor=Master` executes once; nonce = idempotent; fetch/exec denied.

## Recall
FTS5 always works. After `--index-vectors`, recall fuses FTS5 + a 128-dim hash-vector with RRF and reports
`fusion: rrf(fts5,hash-vector)`.

## Intent bridge (beta 2)
```
python runtime/agi_bridge.py --root <sandbox> --init-token
python runtime/agi_bridge.py --root <sandbox> --serve --port 8766
```
- `/health` open; `/status` + `/intent/<id>` need `read`; `POST /intent` needs `write`.
- Bearer tokens are shown once; only sha256 is stored. Loopback clients only.
- Outbound relay mode: put request JSON files in `<inbox>/`; `--relay <inbox> --once` writes `*.result.json`.
  This simulates the tunnel without opening ingress.

## Security
No public ingress in beta.2; intents are approved locally by the Master; the bridge cannot execute writes.
