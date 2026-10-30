# AGI Entelechy beta 5 - user manual (minimal)

## Runtime & recall
`agi_runtime.py --status`, `--index-vectors`, `--serve`. 10 verbs; writes are intents; Master approval local-only;
recall fuses FTS5 + vector (RRF) and reports `recall_backend`.

## Bridge & event stream
`agi_bridge.py --init-token`, `--serve --port 8766`, `--relay <dir>`.
- MCP: POST /mcp JSON or SSE; GET /mcp with `Accept: text/event-stream` replays events after `Last-Event-ID`,
  then streams live events + heartbeats for a bounded 6 s window.
- Intents queue; remote approval refused. Loopback only; tokens scoped read/write.

## Migration (normalization step)
```
python runtime/agi_migrate.py --source <live AGI> --target <sandbox>            # dry-run
python runtime/agi_migrate.py --source <live AGI> --target <sandbox> --apply    # target index only
```
Source is verified unchanged; same-tree targets are refused.

## Tunnel (plan only)
`agi_tunnel.py --check` / `--plan --port 8766 [--hostname]` prints reviewed commands + security policy
(access policy, token, rotate after exposure). It never starts a tunnel.

## Conformance
`agi_conformance.py --root <sandbox>` -> C-beta1..C-beta11; PASS required before adoption experiments.
