# M2 taxonomy/visibility — non-live staging package (for Kilo independent review)

**Status:** staged only; no live integration/enforcement; `AGI_M2_HOST_AUTH=off`; v4.0.1/M1 preserved.
**Director direction:** stage M2 taxonomy, visibility policy, migration dry-run, rollback and adversarial bypass tests;
Kilo independently reviews the frozen package; no federation/identity mutation/evolution.

## Scope
- Memory taxonomy/visibility policy staged on copies of the live index; no live runtime wiring.
- Migration: added columns/classification for 1,957 items; 10 docs untouched pending approval.
- Visibility: private default; family/public disabled; shared separate; trust cannot raise visibility.
- Adversarial bypass evidence: host-auth prototype 27/27 (six critical independently re-executed by Kilo) plus
  staging visibility/migration checks 14/14.
- Rollback: tested against pre-M2 backup copy; hash restored.

## Evidence
- staging evidence: `state/archive/evolution/agi-v5-m2-staging-20261031/staging-evidence.json`
- migration tool: `tools/agi5_m2_migrate.py` (dry-run/apply/rollback)
- M2 schema/matrix: `state/archive/evolution/agi-v5-m2-schema-migration-matrix-20261031.md`
- host-auth prototype audit: `state/archive/evolution/kilo-m2-host-auth-prototype-audit-20261031.json`
- live apply evidence: `state/archive/evolution/agi-v5-m2-apply-evidence-20261031.json`

## Limits
- Staging/observation only; no runtime policy hook; no enforcement; no permission for canary/expansion.
- 10 documents remain untouched; family/public remain disabled placeholders.
- No release asset changes; no network.
