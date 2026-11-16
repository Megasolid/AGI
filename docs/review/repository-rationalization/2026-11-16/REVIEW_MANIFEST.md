# REVIEW MANIFEST — Repository Rationalization Audit (Temporary Review)

**Submission type:** TEMPORARY REVIEW — not for merge, not for permanent publication.
**Prepared:** 2026-11-16
**Target branch:** `review/repository-rationalization-2026-11-16`
**Base:** `main` @ `98a53250181173815eddf1bc137b2c2f2d995b60`

| # | Filename | Source path | Revision | SHA-256 | Status | Sanitization | Notes |
|---|---|---|---|---|---|---|---|
| 1 | `REPOSITORY_SIZE_AUDIT.md` | `documentation/workspace/REPOSITORY_SIZE_AUDIT.md` | HEAD `e7eb0ca` (working tree) | `fd4eec4902bbae8a2b4d5c6a16f974a4f3da070da66fc2c708d6a0d38d2fc611` | Corrected | Sanitized: units normalized to MiB; no abs paths | Fresh measurements; git object DB corrected |
| 2 | `REPOSITORY_CONTENT_CLASSIFICATION.md` | `documentation/workspace/REPOSITORY_CONTENT_CLASSIFICATION.md` | HEAD `e7eb0ca` (working tree) | `b36de2e800b5d8f3398d770a118b4d6482f953be0e98138e5e1e8dee0d33998c` | Corrected | Sanitized: 1 local path redacted to `[REDACTED-LOCAL-PATH]` | Overlap warning added; points to primary classification |
| 3 | `AGI_V5_MINIMAL_REPOSITORY_DESIGN.md` | `documentation/workspace/AGI_V5_MINIMAL_REPOSITORY_DESIGN.md` | HEAD `e7eb0ca` (working tree) | `43a99ee9d49acd9fb9dbb9e5652fe2033e5f13950e0694fefef6818061500ac9` | Corrected | Sanitized: no abs paths (verified) | Design unchanged; externalization refs updated |
| 4 | `SIZE_REDUCTION_DISPOSITION_REGISTER.md` | `documentation/workspace/SIZE_REDUCTION_DISPOSITION_REGISTER.md` | HEAD `e7eb0ca` (working tree) | `fb3b083862a5ed85ce35449e573a512f9e7f91deb1c8487e9f2926babf9c67a9` | Corrected | Sanitized: 1 local path redacted to `[REDACTED-LOCAL-PATH]` | MiB units; regeneration evidence refs |
| 5 | `REPOSITORY_RATIONALIZATION_RISK_REGISTER.md` | `documentation/workspace/REPOSITORY_RATIONALIZATION_RISK_REGISTER.md` | HEAD `e7eb0ca` (working tree) | `2dc2284010e14fd7ff1b4a999920874ac00edef768e60a1725917970e22a827b` | Corrected | Sanitized: no abs paths (verified) | Q-09/Q-10 added |
| 6 | `REPOSITORY_SIZE_ACCOUNTING_AND_RECONCILIATION.md` | `documentation/workspace/REPOSITORY_SIZE_ACCOUNTING_AND_RECONCILIATION.md` | HEAD `e7eb0ca` (working tree) | `9f16e4ea2371e9315977a60e3dd4a4c9cd09963bf67d1f396f13f113d4de8c11` | New | Sanitized: 1 local path redacted to `[REDACTED-LOCAL-PATH]` | Authoritative byte counts; mutually-exclusive primary classification |

## Sanitization summary

- **Absolute paths:** 3 occurrences of `C:\Users\D\...` redacted to `[REDACTED-LOCAL-PATH]` (docs 2, 4, 6).
- **Credentials/tokens/secrets:** none found.
- **Emails/PII:** none found.
- **Private operational evidence / memory contents:** none included; documents reference protected material by category only.
- **Internal IDs:** git commit SHAs and branch names retained (already public in repo).
- **Model identifier:** `unsloth/bge-small-en-v1.5` retained (public HF model, not sensitive).

## Known limitations

- Documents reflect **read-only investigation** as of 2026-11-16; no cleanup/migration performed.
- `.reference` contents were **not inspected**; all `.reference` figures are aggregate sizes.
- Regeneration evidence for `.vs/` lacks exact Visual Studio version (noted in doc 6).
- Embedding model host-path portability violation noted; model identity public.

## Non-authorization

This submission is **temporary review access only**. No merge requested or authorized. No permanent publication intended at this stage. PR and branch may be closed and deleted after review.