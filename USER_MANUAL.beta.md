# AGI Entelechy beta 7 - user manual (minimal)

## Seats (ed25519 public-key)
```
python runtime/agi_seats.py --root <sandbox> --enroll NAME            # key shown once
python runtime/agi_seats.py --root <sandbox> --challenge NAME
python runtime/agi_seats.py --root <sandbox> --sign NAME NONCE --key <DEVICE_KEY>
python runtime/agi_seats.py --root <sandbox> --login NAME NONCE <PROOF>
python runtime/agi_seats.py --root <sandbox> --status
```
Ed25519 mode stores only the public key; login proves possession by signing
`agi-seat-login/v2:<member>:<nonce>`. Nonces are single-use/expiring. HMAC fallback exists for no-cryptography hosts.

## Master ceremony
```
python runtime/agi_master.py --root <sandbox> --ceremony
python runtime/agi_master.py --root <sandbox> --ident
python runtime/agi_master.py --root <sandbox> --sign FILE --out SIG
python runtime/agi_master.py --root <sandbox> --verify FILE SIG
```
Private key stays in state/master.key (0600); back it up offline; never commit it.

## Bridge / migration / conformance
MCP 12 tools incl. seat_challenge/seat_login; remote approval refused; event stream with Last-Event-ID and ?window=0.
Migration: `--snapshot-db` then `--apply` then `--restore-db` to prove rollback. Conformance C-beta1..C-beta17 PASS 18/18.
