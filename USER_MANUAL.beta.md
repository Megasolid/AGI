# AGI Entelechy beta 10 - user manual (minimal)

## Audit trail
Every passport issuance (local or MCP) appends to `<sandbox>/state/audit.jsonl`:
```
python runtime/agi_passport.py --root <sandbox> --audit
```
Entries carry seq, ts, event, member, actor (local/mcp), passport_sha256, signature algos.

## Release signing (dual)
```
python runtime/agi_release.py --root <sandbox> --sign [FILE ...]
python runtime/agi_release.py --root <sandbox> --verify
```
Artifacts (default: DNA, seed, notes present in the tree) are signed Ed25519 + ML-DSA-65 and recorded in
`state/release_signatures.json`; verification re-hashes and checks both signatures; tamper fails.

## Stability window
```
python runtime/agi_stability.py --root <sandbox> --runs 5
```
Runs the full C-beta matrix on fresh cold copies. Evidence only - the beta does not claim beta-stable by itself.

## Everything else
Seats, passports, policy gate, bridge/MCP (17 tools), migration + rollback, tunnel plan: see INSTALL/USER notes.
