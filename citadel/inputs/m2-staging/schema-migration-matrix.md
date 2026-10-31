# M2 revised schema + migration matrix (Director amendments incorporated)

**Status:** design only; no apply. Revised after Director review 2026-10-31.
**Amendments:** identity/evolutionary classes are separate and read-only for ordinary ingestion; family/public are
disabled deny-by-default placeholders; authorization is not trust/truth; sensitive/secret excluded/redacted from
logs/exports/snapshots/adapters unless explicitly authorized; backfill preserves originals and reports ambiguous
classifications for approval; rollback tested on a copied baseline before production migration.

## Schema additions (additive; existing columns retained)
```sql
ALTER TABLE items ADD COLUMN memory_class TEXT NOT NULL DEFAULT 'episodic';   -- learned: episodic/semantic/procedural/relational/collective
ALTER TABLE items ADD COLUMN visibility TEXT NOT NULL DEFAULT 'private';     -- private(default)/family(disabled)/shared_authorized/public(disabled)
ALTER TABLE items ADD COLUMN origin_host_instance TEXT;
ALTER TABLE items ADD COLUMN provenance_event_id TEXT;
ALTER TABLE items ADD COLUMN trust_level TEXT NOT NULL DEFAULT 'attested';   -- untrusted/attested/validated/master_approved
ALTER TABLE items ADD COLUMN confidence REAL;
ALTER TABLE items ADD COLUMN created_at TEXT;
ALTER TABLE items ADD COLUMN updated_at TEXT;
ALTER TABLE items ADD COLUMN last_verified_at TEXT;
ALTER TABLE items ADD COLUMN source_sha256 TEXT;
ALTER TABLE items ADD COLUMN supersedes TEXT;
ALTER TABLE items ADD COLUMN superseded_by TEXT;
ALTER TABLE items ADD COLUMN conflicts_with TEXT;
ALTER TABLE items ADD COLUMN conflict_state TEXT NOT NULL DEFAULT 'none';
ALTER TABLE items ADD COLUMN version INTEGER NOT NULL DEFAULT 1;
CREATE INDEX idx_items_visibility ON items(visibility);
CREATE INDEX idx_items_class ON items(memory_class);
```
`identity` and `evolutionary` classes are **reserved and read-only**: ordinary experience ingestion must never write
them; only lineage/identity tools with Master approval may. `family` and `public` are enum placeholders that policy
always denies until a separate authorization change.

Separate shared store `state/agi5/shared.db`:
```sql
CREATE TABLE shared_experiences(
  event_id TEXT PRIMARY KEY, payload_digest TEXT NOT NULL, organism_id TEXT NOT NULL,
  visibility TEXT NOT NULL CHECK(visibility='shared_authorized'), approval_id TEXT,
  origin_host_instance TEXT, provenance TEXT, ingested_at TEXT NOT NULL);
```
No private body is copied into shared store.

## Migration matrix (current 1,967 items, read-only dry-run)
| Current | Count | New class | Visibility | Trust level | Confidence | Action |
|---|---:|---|---|---|---|---|
| memory / verified / private | 178 | episodic | private | validated (provenance verified) | high | auto |
| knowledge / verified / internal | 1,779 | semantic | private | validated | high | auto |
| doc / public / internal | 10 | semantic | private (legacy_public pending approval) | validated | medium | **approval required** |
| unknown kind/trust | 0 | private (fail-safe) | private | untrusted | low | **approval required** |
| identity / evolutionary | 0 | reserved | private | untrusted | — | never auto; Master only |

**Public docs:** until family/public authorization is separately approved, the 10 public docs are migrated to
`private` with `provenance.legacy_public=true` and listed for explicit approval; they are not silently exposed.
**Senstive/secret:** none currently indexed; future rows with sensitivity sensitive/secret are redacted from logs,
exports, snapshots and adapters unless explicitly authorized.

## Reversibility
Backup full DB + SHA-256 + row counts before apply; dry-run writes nothing; apply is idempotent; rollback restores the
backup copy and verifies schema/hashes on a **copied baseline** before touching production. No deletions.

## Director-required tests
Negative access-control matrix (private cross-host, family/public denied, shared wrong-host/no-approval, sensitive/
secret redaction, missing context, trust independent of visibility), dry-run counts, rollback-on-copy, v4/M1 regression.
