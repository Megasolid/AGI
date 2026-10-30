# AGI Entelechy beta 6 - user manual (minimal)

## Runtime & recall
`agi_runtime.py --status`, `--index-vectors`, `--serve`. Intents queue; only the local Master approves;
fetch/exec denied; recall fuses FTS5 + vector and reports `recall_backend`.

## Seats (beta 6)
```
python runtime/agi_seats.py --root <sandbox> --enroll NAME   # key shown ONCE
python runtime/agi_seats.py --root <sandbox> --challenge NAME
python runtime/agi_seats.py --root <sandbox> --login NAME NONCE PROOF
python runtime/agi_seats.py --root <sandbox> --status
```
Proof = HMAC-SHA256(device_key, "agi-seat-login/v1:<member>:<nonce>"). Nonces are single-use and expire; status
shows hashes/status only. Seat secrets live in the local sandbox DB (local-only beta ceremony; Ed25519 is beta.7).

## Bridge / event stream
Default stream is bounded 6 s; `GET /mcp?window=0` keeps it open until the client closes. Events replay from
`Last-Event-ID`. Remote approval is refused by design.

## Migration / tunnel / conformance
`agi_migrate.py` dry-run default (source read-only), `agi_tunnel.py --plan` (never starts), 
`agi_conformance.py --root <sandbox>` -> C-beta1..C-beta13 PASS 14/14.
