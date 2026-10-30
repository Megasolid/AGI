# AGI Entelechy beta 8 - user manual (minimal)

## Seats / Master / Passports
```
python runtime/agi_master.py --root <sandbox> --ceremony
python runtime/agi_seats.py --root <sandbox> --enroll NAME            # key once
python runtime/agi_seats.py --root <sandbox> --challenge NAME
python runtime/agi_seats.py --root <sandbox> --sign NAME NONCE --key <DEVICE_KEY>
python runtime/agi_seats.py --root <sandbox> --login NAME NONCE <PROOF>
python runtime/agi_passport.py --root <sandbox> --issue NAME
python runtime/agi_passport.py --root <sandbox> --verify NAME
python runtime/agi_passport.py --root <sandbox> --list
```
Passports bind member + gen_id + DNA sha + seat public key and are Master-signed; verification cross-checks all of
them. Tamper is rejected. Ed25519 needs `cryptography`; seats fall back to HMAC.

## Bridge (MCP, 16 tools)
Remote enrollment/passport tools require scopes (`seat_enroll` = write; `seat_status`, `passport_*` = read);
`approve_intent` is always refused remotely. Event stream: Last-Event-ID replay, `?window=0` unbounded.

## Migration / tunnel / conformance
`agi_migrate.py` dry-run + `--snapshot-db` / `--restore-db` rollback proof. `agi_tunnel.py --plan` only - tunnel E2E
is blocked on this host (no tunnel binary), relay mailbox is the proven transport. `agi_conformance.py` PASS 20/20.
