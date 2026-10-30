# AGI Entelechy beta 9 - user manual (minimal)

## Master (dual signing)
```
python runtime/agi_master.py --root <sandbox> --ceremony      # Ed25519 + ML-DSA-65 if available
python runtime/agi_master.py --root <sandbox> --sign FILE
python runtime/agi_master.py --root <sandbox> --verify FILE SIG
```
Signatures list their `algos` (ed25519, ml-dsa-65). Tamper fails. Private keys are local files (no HSM).

## Policy gate
Remote passport issuance is OFF by default:
```
python runtime/agi_policy.py --root <sandbox> --show
python runtime/agi_policy.py --root <sandbox> --set remote_passport_issue_enabled=true   # local decision
```
MCP `passport_issue` requires write scope AND this enablement; otherwise it is refused.

## Stability
```
python runtime/agi_stability.py --root <sandbox> --runs 2
```
Runs the full conformance matrix on fresh cold copies; verdict STABLE only when every run passes.

## Conformance
`agi_conformance.py --root <sandbox>` -> C-beta1..C-beta22 (23 checks), PASS required before experiments.
